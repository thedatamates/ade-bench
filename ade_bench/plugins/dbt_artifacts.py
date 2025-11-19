# ABOUTME: dbt artifacts plugin generates baseline manifest.json and catalog.json
# ABOUTME: Creates artifacts in target-base directory before agent execution

import logging
import subprocess
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

    def pre_setup(self, context: PluginContext) -> None:
        """Generate dbt artifacts before setup runs"""
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

    def post_trial(self, context: PluginContext) -> None:
        """Generate final artifacts and archive both baseline and final to experiments folder"""
        logger.info(f"[DbtArtifactsPlugin] Generating final dbt artifacts after agent execution")

        # Generate final artifacts in /app/target/
        context.session.send_keys(
            [
                "cd /app && dbt docs generate",
                "Enter",
            ],
            block=True,
            max_timeout_sec=300
        )
        logger.info(f"[DbtArtifactsPlugin] Final dbt artifacts generated in /app/target/")

        # Archive artifacts to experiments folder
        trial_dir = context.trial_handler._task_output_path
        artifacts_dir = trial_dir / "dbt_artifacts"
        artifacts_dir.mkdir(exist_ok=True)

        logger.info(f"[DbtArtifactsPlugin] Archiving artifacts to {artifacts_dir}")

        # Copy baseline artifacts (target-base)
        baseline_dir = artifacts_dir / "baseline"
        baseline_dir.mkdir(exist_ok=True)
        self._copy_from_container(
            context.session.container,
            "/app/target-base/manifest.json",
            baseline_dir / "manifest.json"
        )
        self._copy_from_container(
            context.session.container,
            "/app/target-base/catalog.json",
            baseline_dir / "catalog.json"
        )
        logger.info(f"[DbtArtifactsPlugin] Baseline artifacts archived to {baseline_dir}")

        # Copy final artifacts (target)
        final_dir = artifacts_dir / "final"
        final_dir.mkdir(exist_ok=True)
        self._copy_from_container(
            context.session.container,
            "/app/target/manifest.json",
            final_dir / "manifest.json"
        )
        self._copy_from_container(
            context.session.container,
            "/app/target/catalog.json",
            final_dir / "catalog.json"
        )
        logger.info(f"[DbtArtifactsPlugin] Final artifacts archived to {final_dir}")

        logger.info(f"[DbtArtifactsPlugin] Artifact archival complete")

    def _copy_from_container(self, container, container_path: str, local_path: Path) -> None:
        """Copy a file from container to local filesystem using docker cp"""
        try:
            # Use docker cp command
            container_name = container.name
            subprocess.run(
                ["docker", "cp", f"{container_name}:{container_path}", str(local_path)],
                check=True,
                capture_output=True
            )
            logger.info(f"[DbtArtifactsPlugin] Copied {container_path} to {local_path}")
        except subprocess.CalledProcessError as e:
            logger.warning(f"[DbtArtifactsPlugin] Failed to copy {container_path}: {e.stderr.decode()}")
        except Exception as e:
            logger.warning(f"[DbtArtifactsPlugin] Failed to copy {container_path}: {e}")
