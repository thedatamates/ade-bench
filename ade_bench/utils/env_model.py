"""Environment variable model for ADE-Bench."""

import os
from typing import Dict

from pydantic import BaseModel


class EnvModel(BaseModel):
    """Base model for environment variables with ADE_BENCH prefix."""
    
    def to_env_dict(self, include_os_env: bool = False) -> Dict[str, str]:
        """Convert model to environment variable dictionary.
        
        Args:
            include_os_env: Whether to include existing OS environment variables
            
        Returns:
            Dictionary of environment variables with ADE_BENCH_ prefix
        """
        env_dict = {}

        for field_name, value in self.model_dump(exclude_none=True).items():
            if value is None:
                continue

            env_dict[f"ADE_BENCH_{field_name.upper()}"] = str(value)

        if include_os_env:
            env_dict.update(os.environ.copy())

        return env_dict