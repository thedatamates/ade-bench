# ABOUTME: Orchestrates task setup by coordinating setup functions and plugin hooks
# ABOUTME: Calls setup functions in sequence with plugin hooks at lifecycle phases

from typing import Dict, Any
from .base_setup import setup_base_files
from .duckdb_setup import setup_duckdb
from .snowflake_setup import setup_snowflake
from .dbt_setup import setup_dbt_project
from .migration_setup import setup_migration
from .agent_setup import setup_agent_config
from ..utils.logger import log_harness_info
from ..plugins.registry import PluginRegistry
from ..plugins.base_plugin import PluginContext


class SetupOrchestrator:
    """Orchestrator that calls setup functions and plugin hooks at lifecycle phases."""

    def __init__(self, logger=None, terminal=None, session=None, file_diff_handler=None, trial_handler=None, enabled_plugins=None):
        """Initialize orchestrator with plugin registry

        Args:
            logger: Logger instance for output
            terminal: Terminal/container manager
            session: Session for running commands
            file_diff_handler: Handler for file diffing
            trial_handler: Handler for trial operations
            enabled_plugins: List of plugin names to enable (from CLI --plugins)
        """
        self.logger = logger
        self.terminal = terminal
        self.session = session
        self.file_diff_handler = file_diff_handler
        self.trial_handler = trial_handler
        self.plugin_registry = PluginRegistry(enabled_plugins or [])

    def setup_task(self, task_id: str, variant: Dict[str, Any]) -> bool:
        """Setup a task with plugin hooks at lifecycle phases."""
        log_harness_info(self.logger, task_id, "setup", f"Starting task setup...")

        # Build context once for all hooks
        context = PluginContext(
            terminal=self.terminal,
            session=self.session,
            trial_handler=self.trial_handler,
            task_id=task_id,
            variant=variant,
            agent_name=variant.get("agent_name"),
            db_type=variant.get("database", {}).get("type") if variant.get("database") else None,
            project_type=variant.get("project_type"),
        )

        # Set up the project
        project_type = variant.get('project_type')
        if project_type in ['dbt', 'dbt-fusion']:
            log_harness_info(self.logger, task_id, "setup", f"Setting up dbt project...")
            setup_dbt_project(self.terminal, self.session, task_id, variant, self.trial_handler)


        # Setup agent-specific configuration files
        # Logging is in the setup_agent_config function
        setup_agent_config(self.terminal, task_id, self.trial_handler, self.logger)


        # Set up the database
        db_type = variant.get('db_type')
        if db_type == 'duckdb':
            log_harness_info(self.logger, task_id, "setup", f"Setting up DuckDB database...")
            setup_duckdb(self.terminal, self.session, variant, self.trial_handler)
        elif db_type == 'snowflake':
            log_harness_info(self.logger, task_id, "setup", f"Setting up Snowflake database from {variant.get('db_name')}...")
            setup_snowflake(self.terminal, self.session, task_id, variant, self.trial_handler)
            log_harness_info(self.logger, task_id, "setup", f"Snowflake setup complete.")


        # Take snapshot before migrations and main setup script
        if self.file_diff_handler:
            # Logging is contained in snapshot
            self.file_diff_handler.handle_phase_diffing(self.terminal.container, "setup", task_id, self.logger)


        # Set up any migrations and run them.
        log_harness_info(self.logger, task_id, "setup", f"Running migrations...")
        setup_migration(self.terminal, self.session, variant, self.trial_handler)
        log_harness_info(self.logger, task_id, "setup", "Migration script complete")

        # PRE-SETUP HOOKS
        self.plugin_registry.run_hooks("pre_setup", context)

        # Run main setup script.
        log_harness_info(self.logger, task_id, "setup", "Running setup script...")
        setup_base_files(self.terminal, self.session, task_id, variant, self.trial_handler)
        log_harness_info(self.logger, task_id, "setup", "Setup script complete.")

        # POST-SETUP HOOKS
        self.plugin_registry.run_hooks("post_setup", context)

        # Take final snapshot after setup script
        if self.file_diff_handler:
            # Logging is contained in snapshot
            self.file_diff_handler.handle_phase_diffing(self.terminal.container, "setup", task_id, self.logger)


        return True
