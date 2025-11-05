# ABOUTME: dbt artifacts plugin generates baseline manifest.json and catalog.json
# ABOUTME: Creates artifacts in target-base directory before agent execution

import logging
from pathlib import Path
from ade_bench.plugins.base_plugin import BasePlugin, PluginContext

logger = logging.getLogger(__name__)


class DbtArtifactsPlugin(BasePlugin):
    name = "dbt-artifacts"
    description = "Generates baseline dbt artifacts (manifest.json, catalog.json) in target-base directory"

    def should_run(self, phase: str, context: PluginContext) -> bool:
        """Only run for dbt and dbt-fusion projects"""
        is_dbt = context.project_type in ["dbt", "dbt-fusion"]
        return is_dbt

    def post_setup(self, context: PluginContext) -> None:
        """Generate dbt artifacts after setup completes"""
        script_path = context.trial_handler._shared_path / "plugins/dbt-artifacts/generate-artifacts.sh"

        logger.info(f"[DbtArtifactsPlugin] Preparing to generate baseline dbt artifacts")
        logger.info(f"[DbtArtifactsPlugin] Source script path: {script_path}")
        logger.info(f"[DbtArtifactsPlugin] Script exists: {script_path.exists()}")

        if not script_path.exists():
            logger.error(f"[DbtArtifactsPlugin] Script not found at {script_path}")
            raise FileNotFoundError(f"dbt-artifacts script not found at {script_path}")

        logger.info(f"[DbtArtifactsPlugin] Copying script to container at /scripts/generate-dbt-artifacts.sh")
        context.terminal.copy_to_container(
            paths=script_path,
            container_dir="/scripts",
            container_filename="generate-dbt-artifacts.sh"
        )
        logger.info(f"[DbtArtifactsPlugin] Script copied successfully")

        logger.info(f"[DbtArtifactsPlugin] Generating baseline dbt artifacts in target-base/")
        context.session.send_keys(
            [
                "bash /scripts/generate-dbt-artifacts.sh",
                "Enter",
            ],
            block=True,
            max_timeout_sec=300
        )
        logger.info(f"[DbtArtifactsPlugin] Baseline dbt artifacts generated successfully")
