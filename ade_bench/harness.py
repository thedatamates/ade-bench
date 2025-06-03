"""Main harness for running ADE-Bench benchmarks."""

import asyncio
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from tqdm import tqdm

from ade_bench.agents.agent_factory import AgentFactory
from ade_bench.agents.base_agent import AgentResult, BaseAgent
from ade_bench.config import config
from ade_bench.handlers.trial_handler import TrialHandler
from ade_bench.harness_models import (
    BenchmarkResults,
    FailureMode,
    RunMetadata,
    TrialResults,
)
from ade_bench.parsers.sql_parser import SQLParser, SQLParserResult
from ade_bench.terminal.docker_compose_manager import DockerComposeManager
from ade_bench.terminal.tmux_session import TmuxSession
from ade_bench.utils.dataset import Dataset
from ade_bench.utils.logger import logger


class Harness:
    """Main harness for running ADE-Bench tasks."""
    
    def __init__(
        self,
        dataset_path: Path,
        output_path: Path,
        run_id: str,
        agent_name: str,
        model_name: Optional[str] = None,
        agent_kwargs: Optional[Dict[str, Any]] = None,
        no_rebuild: bool = False,
        cleanup: bool = False,
        log_level: int = logging.INFO,
        task_ids: Optional[List[str]] = None,
        n_tasks: Optional[int] = None,
        max_episodes: int = 50,
        n_concurrent_trials: int = 4,
        exclude_task_ids: Optional[set[str]] = None,
        n_attempts: int = 1,
        dataset_config: Optional[Path] = None,
    ):
        """Initialize the harness.
        
        Args:
            dataset_path: Path to the dataset directory
            output_path: Path to output results
            run_id: Unique identifier for this run
            agent_name: Name of the agent to use
            model_name: Model name for LLM agents
            agent_kwargs: Additional arguments for agent
            no_rebuild: Skip Docker image rebuilds
            cleanup: Clean up Docker resources after run
            log_level: Logging level
            task_ids: Specific task IDs to run
            n_tasks: Number of tasks to run
            max_episodes: Maximum interactions per task
            n_concurrent_trials: Number of concurrent tasks
            exclude_task_ids: Task IDs to exclude
            n_attempts: Number of attempts per task
            dataset_config: YAML config for dataset
        """
        self._start_time = datetime.now(timezone.utc).isoformat()
        
        self._dataset_path = dataset_path
        self._dataset_config = dataset_config
        self._n_tasks = n_tasks
        self._task_ids = task_ids
        self._exclude_task_ids = exclude_task_ids
        
        self._output_path = output_path
        self._agent_name = agent_name
        # Set default model names for agents
        if agent_name == "oracle":
            self._model_name = "Oracle"
        elif agent_name == "claude-code" and model_name is None:
            self._model_name = "claude-3-5-sonnet-20241022"
        else:
            self._model_name = model_name or "default"
        self._agent_kwargs = agent_kwargs or {}
        self._run_id = run_id
        self._no_rebuild = no_rebuild
        self._cleanup = cleanup
        self._log_level = log_level
        self._max_episodes = max_episodes
        self._n_concurrent_trials = n_concurrent_trials
        self._n_attempts = n_attempts
        
        self._run_path.mkdir(parents=True, exist_ok=True)
        
        self._init_dataset()
        self._init_logger()
    
    @property
    def _run_path(self) -> Path:
        """Path to run output directory."""
        return self._output_path / self._run_id
    
    @property
    def _results_output_path(self) -> Path:
        """Path to results JSON file."""
        return self._run_path / "results.json"
    
    @property
    def _run_metadata_output_path(self) -> Path:
        """Path to run metadata JSON file."""
        return self._run_path / "run_metadata.json"
    
    @property
    def _log_output_path(self) -> Path:
        """Path to run log file."""
        return self._run_path / "run.log"
    
    def _init_dataset(self) -> None:
        """Initialize the dataset."""
        self._dataset = Dataset(
            dataset_config=self._dataset_config,
            dataset_path=self._dataset_path,
            task_ids=self._task_ids,
            exclude_task_ids=self._exclude_task_ids,
            n_tasks=self._n_tasks,
        )
    
    def _init_logger(self) -> None:
        """Initialize logger for the run."""
        self._logger = logger.getChild("harness")
        
        # Add file handler for run log
        file_handler = logging.FileHandler(self._log_output_path)
        file_handler.setLevel(self._log_level)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        self._logger.addHandler(file_handler)
    
    def _create_agent_for_task(self, task_id: str) -> BaseAgent:
        """Create a fresh agent for a specific task."""
        agent_kwargs = self._agent_kwargs.copy()
        return AgentFactory.create_agent(
            agent_name=self._agent_name,
            model_name=self._model_name,
            task_id=task_id,
            max_episodes=self._max_episodes,
            **agent_kwargs,
        )
    
    def run(self) -> BenchmarkResults:
        """Run the benchmark and return results."""
        self._logger.info(f"Starting run {self._run_id}")
        self._logger.info(f"Running {len(self._dataset)} tasks")
        
        run_metadata = RunMetadata(
            run_id=self._run_id,
            agent_name=self._agent_name,
            model_name=self._model_name,
            dataset_path=str(self._dataset_path),
            n_tasks=len(self._dataset),
            task_ids=[task.task_id for task in self._dataset],
            start_time=self._start_time,
        )
        
        # Save run metadata
        with open(self._run_metadata_output_path, "w") as f:
            json.dump(run_metadata.model_dump(), f, indent=2)
        
        # Run trials
        trial_results = self._run_trials()
        
        # Create benchmark results
        end_time = datetime.now(timezone.utc).isoformat()
        benchmark_results = BenchmarkResults(
            run_metadata=run_metadata,
            trial_results=trial_results,
            end_time=end_time,
        )
        
        # Save results
        with open(self._results_output_path, "w") as f:
            json.dump(benchmark_results.model_dump(), f, indent=2)
        
        # Log summary
        self._log_summary(benchmark_results)
        
        return benchmark_results
    
    def _run_trials(self) -> List[TrialResults]:
        """Run all trials concurrently."""
        trial_results = []
        
        with ThreadPoolExecutor(max_workers=self._n_concurrent_trials) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(
                    self._run_trial,
                    task=task,
                    attempt=attempt,
                ): (task, attempt)
                for task in self._dataset
                for attempt in range(self._n_attempts)
            }
            
            # Process completed tasks with progress bar
            with tqdm(
                total=len(future_to_task),
                desc="Running trials",
                unit="trial",
            ) as pbar:
                for future in as_completed(future_to_task):
                    task, attempt = future_to_task[future]
                    try:
                        result = future.result()
                        trial_results.append(result)
                    except Exception as e:
                        self._logger.error(
                            f"Error running task {task.task_id} (attempt {attempt}): {e}"
                        )
                        # Create failed result
                        trial_results.append(
                            TrialResults(
                                task_id=task.task_id,
                                attempt=attempt,
                                success=False,
                                failure_mode=FailureMode.ERROR,
                                error_message=str(e),
                            )
                        )
                    finally:
                        pbar.update(1)
        
        return trial_results
    
    def _run_trial(self, task: Any, attempt: int) -> TrialResults:
        """Run a single trial for a task."""
        self._logger.info(f"Running task {task.task_id} (attempt {attempt})")
        
        trial_handler = TrialHandler(
            task=task,
            output_path=self._run_path / task.task_id / f"attempt_{attempt}",
            no_rebuild=self._no_rebuild,
            cleanup=self._cleanup,
        )
        
        try:
            # Initialize trial
            trial_handler.setup()
            
            # Start Docker containers
            with trial_handler.spin_up_containers() as container:
                # Create tmux session
                tmux = TmuxSession(
                    session_name=f"{task.task_id}_{attempt}",
                    container=container,
                )
                tmux.start()
                
                try:
                    # Create and run agent
                    agent = self._create_agent_for_task(task.task_id)
                    agent_result = asyncio.run(
                        agent.run(
                            task=task,
                            container=container,
                            tmux_session=tmux,
                        )
                    )
                    
                    # Run SQL tests
                    test_results = self._run_sql_tests(
                        task=task,
                        container=container,
                        trial_handler=trial_handler,
                    )
                    
                    # Create trial results
                    trial_results = TrialResults(
                        task_id=task.task_id,
                        attempt=attempt,
                        success=test_results.all_passed,
                        test_results=test_results.model_dump(),
                        agent_result=agent_result.model_dump() if agent_result else None,
                        failure_mode=None if test_results.all_passed else FailureMode.TEST_FAILED,
                    )
                    
                finally:
                    tmux.stop()
            
            return trial_results
            
        except Exception as e:
            self._logger.error(f"Error in trial: {e}", exc_info=True)
            return TrialResults(
                task_id=task.task_id,
                attempt=attempt,
                success=False,
                failure_mode=FailureMode.ERROR,
                error_message=str(e),
            )
    
    def _run_sql_tests(
        self,
        task: Any,
        container: Any,
        trial_handler: TrialHandler,
    ) -> SQLParserResult:
        """Run SQL tests for a task."""
        # Get database path in container based on type
        db_type = getattr(task, "db_type", "duckdb")
        db_name = getattr(task, "db_name", "analytics")
        
        if db_type == "sqlite":
            db_path = f"/data/{db_name}.db"
        elif db_type == "postgres":
            # For PostgreSQL, we'd need to handle this differently
            # as it's not a file-based database
            self._logger.warning("PostgreSQL test validation not yet implemented")
            return SQLParserResult()
        else:  # duckdb
            db_path = f"/data/{db_name}.duckdb"
        
        # Create SQL parser
        parser = SQLParser(database_path=db_path)
        
        # Run tests
        test_dir = trial_handler.task_path / "tests"
        expected_dir = trial_handler.task_path / "expected"
        
        if not test_dir.exists() or not expected_dir.exists():
            self._logger.warning(f"Test directories not found for {task.task_id}")
            return SQLParserResult()
        
        # Copy test files to container if needed
        # (In practice, these would already be in the container)
        
        # Parse and run tests
        results = parser.parse_tests(test_dir, expected_dir)
        
        return results
    
    def _log_summary(self, results: BenchmarkResults) -> None:
        """Log summary of benchmark results."""
        total_tasks = len(results.trial_results)
        successful_tasks = sum(1 for r in results.trial_results if r.success)
        
        self._logger.info(f"Benchmark complete!")
        self._logger.info(f"Total tasks: {total_tasks}")
        self._logger.info(f"Successful: {successful_tasks}")
        self._logger.info(f"Failed: {total_tasks - successful_tasks}")
        self._logger.info(f"Success rate: {successful_tasks / total_tasks * 100:.1f}%")
        self._logger.info(f"Results saved to: {self._results_output_path}")