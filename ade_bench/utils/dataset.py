"""Dataset management for ADE-Bench."""

import random
from pathlib import Path
from typing import Any, List, Optional, Set

import yaml

from ade_bench.harness_models import TaskMetadata
from ade_bench.utils.logger import logger
from ade_bench.config import config


class Task:
    """Represents a single task in the dataset."""
    
    def __init__(self, task_path: Path, metadata: TaskMetadata):
        """Initialize task.
        
        Args:
            task_path: Path to task directory
            metadata: Task metadata
        """
        self.path = task_path
        self.task_id = metadata.task_id
        self.title = metadata.title
        self.description = metadata.description
        self.difficulty = metadata.difficulty
        self.category = metadata.category
        self.tags = metadata.tags
        self.timeout_seconds = metadata.timeout_seconds
        self.test_type = metadata.test_type
        self.db_type = metadata.db_type
        self.database = metadata.database  # Database configuration
        
        # Store full metadata
        self._metadata = metadata
    
    def __repr__(self) -> str:
        return f"Task(id={self.task_id}, title={self.title})"


class Dataset:
    """Manages a collection of tasks."""
    
    def __init__(
        self,
        dataset_path: Optional[Path] = None,
        dataset_config: Optional[Path] = None,
        task_ids: Optional[List[str]] = None,
        exclude_task_ids: Optional[Set[str]] = None,
        n_tasks: Optional[int] = None,
    ):
        """Initialize dataset.
        
        Args:
            dataset_path: Path to dataset directory
            dataset_config: Path to YAML config file
            task_ids: Specific task IDs to include
            exclude_task_ids: Task IDs to exclude
            n_tasks: Number of tasks to include
        """
        self._logger = logger.getChild("dataset")
        self.tasks: List[Task] = []
        
        if dataset_config:
            self._load_from_config(dataset_config)
        elif dataset_path:
            self._load_from_directory(dataset_path)
        else:
            raise ValueError("Either dataset_path or dataset_config must be provided")
        
        # Filter tasks
        self._filter_tasks(task_ids, exclude_task_ids, n_tasks)
    
    def _load_from_config(self, config_path: Path) -> None:
        """Load dataset from YAML configuration."""
        with open(config_path) as f:
            yaml_config = yaml.safe_load(f)
        
        # Handle dataset_path - resolve relative paths from project root
        dataset_path_str = yaml_config.get("dataset_path", "tasks")
        if dataset_path_str.startswith("/"):
            # Absolute path
            dataset_path = Path(dataset_path_str)
        else:
            # Relative path - resolve from project root
            dataset_path = config.project_root / dataset_path_str
        
        # Load specified tasks - support both 'task_ids' and 'tasks' for compatibility
        tasks_config = yaml_config.get("task_ids", yaml_config.get("tasks", []))
        
        # Support both simple list format and detailed format
        for task_item in tasks_config:
            if isinstance(task_item, str):
                # Simple format: just task ID
                task_id = task_item
                task_path = dataset_path / task_id
            elif isinstance(task_item, dict):
                # Detailed format with metadata
                task_id = task_item["task_id"]
                task_path = dataset_path / task_id
            else:
                self._logger.warning(f"Invalid task configuration: {task_item}")
                continue
            
            if not task_path.exists():
                self._logger.warning(f"Task directory not found: {task_path}")
                continue
            
            # Load task metadata
            metadata = self._load_task_metadata(task_path)
            if metadata:
                self.tasks.append(Task(task_path, metadata))
    
    def _load_from_directory(self, dataset_path: Path) -> None:
        """Load all tasks from a directory."""
        if not dataset_path.exists():
            raise ValueError(f"Dataset path does not exist: {dataset_path}")
        
        # Find all task directories
        for task_dir in sorted(dataset_path.iterdir()):
            if not task_dir.is_dir():
                continue
            
            # Check if it's a valid task directory
            if not (task_dir / "task.yaml").exists():
                continue
            
            # Load task metadata
            metadata = self._load_task_metadata(task_dir)
            if metadata:
                self.tasks.append(Task(task_dir, metadata))
    
    def _load_task_metadata(self, task_path: Path) -> Optional[TaskMetadata]:
        """Load task metadata from task.yaml."""
        metadata_path = task_path / "task.yaml"
        
        if not metadata_path.exists():
            self._logger.warning(f"No task.yaml found in {task_path}")
            return None
        
        try:
            with open(metadata_path) as f:
                data = yaml.safe_load(f)
            
            # Add task_id from directory name if not present
            if "task_id" not in data:
                data["task_id"] = task_path.name
            
            return TaskMetadata(**data)
            
        except Exception as e:
            self._logger.error(f"Error loading task metadata from {task_path}: {e}")
            return None
    
    def _filter_tasks(
        self,
        task_ids: Optional[List[str]],
        exclude_task_ids: Optional[Set[str]],
        n_tasks: Optional[int],
    ) -> None:
        """Filter tasks based on criteria."""
        # Filter by task IDs
        if task_ids:
            self.tasks = [t for t in self.tasks if t.task_id in task_ids]
        
        # Exclude specific tasks
        if exclude_task_ids:
            self.tasks = [t for t in self.tasks if t.task_id not in exclude_task_ids]
        
        # Limit number of tasks
        if n_tasks and len(self.tasks) > n_tasks:
            random.shuffle(self.tasks)
            self.tasks = self.tasks[:n_tasks]
        
        self._logger.info(f"Loaded {len(self.tasks)} tasks")
    
    def __len__(self) -> int:
        """Get number of tasks."""
        return len(self.tasks)
    
    def __iter__(self):
        """Iterate over tasks."""
        return iter(self.tasks)
    
    def __getitem__(self, index: int) -> Task:
        """Get task by index."""
        return self.tasks[index]
    
    def get_by_id(self, task_id: str) -> Optional[Task]:
        """Get task by ID."""
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        return None