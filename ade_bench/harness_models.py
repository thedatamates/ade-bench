"""Data models for ADE-Bench harness."""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class FailureMode(str, Enum):
    """Types of failures that can occur during trials."""
    
    TEST_FAILED = "test_failed"
    TIMEOUT = "timeout"
    ERROR = "error"
    CONTEXT_LENGTH = "context_length"
    PARSE_ERROR = "parse_error"


class RunMetadata(BaseModel):
    """Metadata about a benchmark run."""
    
    run_id: str
    agent_name: str
    model_name: str
    dataset_path: str
    n_tasks: int
    task_ids: List[str]
    start_time: str
    end_time: Optional[str] = None


class TrialResults(BaseModel):
    """Results from a single trial."""
    
    task_id: str
    attempt: int
    success: bool
    failure_mode: Optional[FailureMode] = None
    error_message: Optional[str] = None
    test_results: Optional[Dict[str, Any]] = None
    agent_result: Optional[Dict[str, Any]] = None
    duration_seconds: Optional[float] = None


class BenchmarkResults(BaseModel):
    """Complete results from a benchmark run."""
    
    run_metadata: RunMetadata
    trial_results: List[TrialResults]
    end_time: str
    
    @property
    def success_rate(self) -> float:
        """Calculate overall success rate."""
        if not self.trial_results:
            return 0.0
        successful = sum(1 for r in self.trial_results if r.success)
        return successful / len(self.trial_results)
    
    @property
    def failure_summary(self) -> Dict[str, int]:
        """Summarize failures by mode."""
        summary = {}
        for result in self.trial_results:
            if result.failure_mode:
                mode = result.failure_mode.value
                summary[mode] = summary.get(mode, 0) + 1
        return summary


class DatabaseConfig(BaseModel):
    """Configuration for task database."""
    
    source: str = Field(default="local", pattern="^(local|shared)$")
    name: Optional[str] = None  # For shared databases
    type: Optional[str] = Field(default=None, pattern="^(duckdb|sqlite|postgres)$")
    path: Optional[str] = None  # For local databases


class TaskMetadata(BaseModel):
    """Metadata for a task."""
    
    task_id: str
    title: str
    description: str
    difficulty: str = Field(pattern="^(easy|medium|hard)$")
    category: str
    tags: List[str] = Field(default_factory=list)
    timeout_seconds: int = 300
    test_type: str = "sql"
    db_type: str = "duckdb"
    database: Optional[DatabaseConfig] = None