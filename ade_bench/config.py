"""Configuration management for ADE-Bench."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()


class Config(BaseModel):
    """Main configuration for ADE-Bench."""
    
    # API Keys
    anthropic_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY"))
    openai_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    
    # S3 Configuration
    s3_bucket_name: Optional[str] = Field(default_factory=lambda: os.getenv("S3_BUCKET_NAME"))
    aws_access_key_id: Optional[str] = Field(default_factory=lambda: os.getenv("AWS_ACCESS_KEY_ID"))
    aws_secret_access_key: Optional[str] = Field(default_factory=lambda: os.getenv("AWS_SECRET_ACCESS_KEY"))
    aws_region: str = Field(default_factory=lambda: os.getenv("AWS_REGION", "us-east-1"))
    
    # Database Configuration
    database_url: Optional[str] = Field(default_factory=lambda: os.getenv("DATABASE_URL"))
    
    # Docker Configuration
    docker_default_platform: str = Field(default_factory=lambda: os.getenv("DOCKER_DEFAULT_PLATFORM", "linux/amd64"))
    
    # Logging
    log_level: str = Field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    
    # Paths
    project_root: Path = Field(default_factory=lambda: Path(__file__).parent.parent)
    
    @property
    def tasks_dir(self) -> Path:
        """Path to tasks directory."""
        return self.project_root / "tasks"
    
    @property
    def experiments_dir(self) -> Path:
        """Path to experiments directory."""
        return self.project_root / "experiments"
    
    @property
    def shared_dir(self) -> Path:
        """Path to shared resources directory."""
        return self.project_root / "shared"
    
    @property
    def docker_dir(self) -> Path:
        """Path to docker configurations directory."""
        return self.project_root / "docker"


# Global config instance
config = Config()