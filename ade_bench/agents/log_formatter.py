"""
Agent log formatting utilities.

This module provides utilities for parsing and formatting agent log files
into human-readable text. Each agent can implement its own log formatter
by subclassing LogFormatter.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List


class LogFormatter(ABC):
    """Base class for agent log formatters."""

    @abstractmethod
    def parse_log_file(self, log_path: Path) -> List[Dict[str, Any]]:
        """
        Parse the agent log file and extract structured information.
        
        Args:
            log_path: Path to the log file to parse
            
        Returns:
            List of turn dictionaries containing structured log data
        """
        pass

    @abstractmethod
    def write_readable_log(self, turns: List[Dict[str, Any]], output_path: Path) -> None:
        """
        Write the parsed turns to a readable text file.
        
        Args:
            turns: List of turn dictionaries from parse_log_file
            output_path: Path where the formatted log should be written
        """
        pass

    def format_log(self, log_path: Path, output_path: Path) -> bool:
        """
        Parse and format a log file in one step.
        
        Args:
            log_path: Path to the log file to parse
            output_path: Path where the formatted log should be written
            
        Returns:
            True if formatting succeeded, False otherwise
        """
        try:
            turns = self.parse_log_file(log_path)
            if not turns:
                return False
            self.write_readable_log(turns, output_path)
            return True
        except Exception:
            return False
