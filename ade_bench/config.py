import os

# import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    # Try to get from streamlit secrets first, then environment variables
    @staticmethod
    def get_setting(key, default=None):
        # Check Streamlit secrets
        # if os.path.exists(".streamlit/secrets.toml"):
        #     if key.lower() in st.secrets:
        #         return st.secrets[key.lower()]

        # Check environment variables (converting to uppercase)
        env_val = os.environ.get(key.upper())
        if env_val is not None:
            return env_val

        return default

    # AWS Settings
    @property
    def aws_region(self):
        return self.get_setting("aws_region", "us-west-2")

    @property
    def s3_bucket_name(self):
        return self.get_setting("s3_bucket_name")

    # Database Settings
    @property
    def db_host(self):
        return self.get_setting("db_host")

    @property
    def db_name(self):
        return self.get_setting("db_name")

    @property
    def db_user(self):
        return self.get_setting("db_user")

    @property
    def db_password(self):
        return self.get_setting("db_password")

    # Timeout Settings
    @property
    def setup_timeout_sec(self) -> float:
        """Timeout for setup scripts in seconds."""
        return float(self.get_setting("setup_timeout_sec", 120.0))

    @property
    def default_agent_timeout_sec(self) -> float:
        """Default timeout for agent execution in seconds."""
        return float(self.get_setting("default_agent_timeout_sec", 180.0))

    @property
    def default_test_timeout_sec(self) -> float:
        """Default timeout for test execution in seconds."""
        return float(self.get_setting("default_test_timeout_sec", 30.0))

    @property
    def cleanup_timeout_sec(self) -> float:
        """Timeout for cleanup operations in seconds."""
        return float(self.get_setting("cleanup_timeout_sec", 30.0))


config = Config()
