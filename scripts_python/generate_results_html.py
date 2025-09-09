#!/usr/bin/env python3
"""Generate HTML results dashboard for experiment results."""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Add the project root to the sys path
sys.path.append(str(Path(__file__).parent.parent))

from scripts_python.utils import get_latest_experiment_with_results
from scripts_python.render_file_diffs import render_diff_log_html
from scripts_python.summarize_results import generate_html_table
from ade_bench.harness_models import BenchmarkResults


class ResultsHTMLGenerator:
    """Generates HTML dashboard for experiment results."""
    
    def __init__(self, experiment_dir: Path):
        self.experiment_dir = Path(experiment_dir)
        self.templates_dir = Path(__file__).parent.parent / "templates"
        self.html_dir = self.experiment_dir / "html"
        
    def generate_all(self):
        """Generate all HTML pages for the experiment."""
        # Create HTML directory
        self.html_dir.mkdir(exist_ok=True)
        
        # Load experiment data
        experiment_data = self._load_experiment_data()
        if not experiment_data:
            print(f"Error: Could not load experiment data from {self.experiment_dir}")
            return False
        
        # Generate summary page
        self._generate_summary_page(experiment_data)
        
        # Generate detail pages for each task
        for task_data in experiment_data['tasks']:
            self._generate_task_detail_pages(task_data)
        
        return True
    
    def _load_experiment_data(self) -> Dict[str, Any]:
        """Load experiment data from results.json and run_metadata.json."""
        results_path = self.experiment_dir / "results.json"
        metadata_path = self.experiment_dir / "run_metadata.json"
        
        if not results_path.exists():
            print(f"Error: results.json not found in {self.experiment_dir}")
            return None
        
        try:
            with open(results_path, 'r') as f:
                results_data = json.load(f)
            
            metadata = {}
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
            
            # Process results into a more usable format
            tasks = []
            for result in results_data.get('results', []):
                # Results are already in the correct format, just use them directly
                tasks.append(result)
            
            return {
                'experiment_id': self.experiment_dir.name,
                'start_time': metadata.get('start_time', 'Unknown'),
                'duration': self._calculate_duration(metadata),
                'total_tasks': len(tasks),
                'successful_tasks': sum(1 for t in tasks if t.get('is_resolved', False)),
                'failed_tasks': sum(1 for t in tasks if not t.get('is_resolved', False)),
                'tasks': tasks
            }
            
        except Exception as e:
            print(f"Error loading experiment data: {e}")
            return None
    
    def _format_time(self, seconds: float) -> str:
        """Format time in seconds to a readable string."""
        if seconds < 1:
            return f"{seconds:.2f}s"
        elif seconds < 60:
            return f"{seconds:.1f}s"
        else:
            minutes = int(seconds // 60)
            secs = seconds % 60
            return f"{minutes}m {secs:.1f}s"
    
    def _calculate_duration(self, metadata: Dict[str, Any]) -> str:
        """Calculate total experiment duration."""
        start_time = metadata.get('start_time')
        end_time = metadata.get('end_time')
        
        if start_time and end_time:
            try:
                start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                duration = end - start
                return str(duration).split('.')[0]  # Remove microseconds
            except:
                pass
        
        return "Unknown"
    
    def _generate_summary_page(self, experiment_data: Dict[str, Any]):
        """Generate the main summary page."""
        template_path = self.templates_dir / "summary.html"
        if not template_path.exists():
            print(f"Error: Template not found: {template_path}")
            return
        
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        # Use the results directly - they're already in the correct format
        benchmark_results = BenchmarkResults(results=experiment_data['tasks'])
        
        # Generate HTML table using centralized logic
        html_table = generate_html_table(benchmark_results)
        
        # Simple template replacement (we'll use Jinja2 later if needed)
        html_content = template_content.replace('{{ experiment_id }}', experiment_data['experiment_id'])
        html_content = html_content.replace('{{ start_time }}', experiment_data['start_time'])
        html_content = html_content.replace('{{ duration }}', experiment_data['duration'])
        html_content = html_content.replace('{{ total_tasks }}', str(experiment_data['total_tasks']))
        html_content = html_content.replace('{{ successful_tasks }}', str(experiment_data['successful_tasks']))
        html_content = html_content.replace('{{ failed_tasks }}', str(experiment_data['failed_tasks']))
        
        # Replace the entire table section with the generated HTML table
        import re
        pattern = r'<table[^>]*>.*?</table>'
        html_content = re.sub(pattern, html_table, html_content, flags=re.DOTALL)
        
        # Write the HTML file
        output_path = self.html_dir / "index.html"
        with open(output_path, 'w') as f:
            f.write(html_content)
    
    def _generate_task_detail_pages(self, task_data: Dict[str, Any]):
        """Generate detail pages for a specific task."""
        task_id = task_data['task_id']
        task_base_dir = self.experiment_dir / task_id
        
        # Find the actual task directory (usually task_id.base.1-of-1)
        task_dir = None
        if task_base_dir.exists():
            # Look for subdirectories that match the pattern task_id.base.*
            for subdir in task_base_dir.iterdir():
                if subdir.is_dir() and subdir.name.startswith(f"{task_id}.base."):
                    task_dir = subdir
                    break
        
        if not task_dir:
            # Fallback to the base directory if no subdirectory found
            task_dir = task_base_dir
        
        # Create task HTML directory
        task_html_dir = self.html_dir / task_id
        task_html_dir.mkdir(exist_ok=True)
        
        # Generate results page
        self._generate_results_page(task_data, task_dir, task_html_dir)
        
        # Generate panes page
        self._generate_panes_page(task_data, task_dir, task_html_dir)
        
        # Generate diffs page
        self._generate_diffs_page(task_data, task_dir, task_html_dir)
    
    def _generate_results_page(self, task_data: Dict[str, Any], task_dir: Path, task_html_dir: Path):
        """Generate results.json detail page."""
        results_path = task_dir / "results.json"
        content = ""
        
        if results_path.exists():
            with open(results_path, 'r') as f:
                results_data = json.load(f)
            content = json.dumps(results_data, indent=2)
        else:
            content = "No results.json file found."
        
        self._write_detail_page(
            task_html_dir / "results.html",
            "Results JSON",
            task_data['task_id'],
            content,
            "json"
        )
    
    def _generate_panes_page(self, task_data: Dict[str, Any], task_dir: Path, task_html_dir: Path):
        """Generate panes detail page."""
        panes_dir = task_dir / "panes"
        content = ""
        
        if panes_dir.exists():
            pane_files = list(panes_dir.glob("*.txt"))
            pane_dict = {p.name: p for p in pane_files}

            pane_order = ["pre-agent.txt", "agent.txt", "post-agent.txt"]
            
            # Main panes in desired order, then any missing panes
            main_panes = [pane_dict[p] for p in pane_order if p in pane_dict]
            missing_panes = [p for p in pane_files if p.name not in pane_order]
            
            panes = main_panes + missing_panes
            
            for pane_file in panes:
                content += f"\n{'='*80}\n"
                content += f"FILE: {pane_file.name}\n"
                content += f"{'='*80}\n\n"
                with open(pane_file, 'r') as f:
                    content += f.read()
                content += "\n\n"
        else:
            content = "No panes directory found."
        
        self._write_detail_page(
            task_html_dir / "panes.html",
            "Terminal Panes",
            task_data['task_id'],
            content,
            "panes"
        )
    
    def _generate_diffs_page(self, task_data: Dict[str, Any], task_dir: Path, task_html_dir: Path):
        """Generate diffs detail page."""
        diff_log_path = task_dir / "diffs" / "file_diff_log.txt"
        content = ""
        
        if diff_log_path.exists():
            # Try to generate HTML diff
            try:
                html_content = render_diff_log_html(diff_log_path, task_data['task_id'])
                # Write the HTML content directly to our task directory
                with open(task_html_dir / "diffs.html", 'w') as f:
                    f.write(html_content)
                return  # We've created the diffs.html file directly
            except Exception as e:
                print(f"Warning: Could not generate HTML diff: {e}")
                # Fall back to text content
                with open(diff_log_path, 'r') as f:
                    content = f.read()
        else:
            content = "No file diff log found."
        
        self._write_detail_page(
            task_html_dir / "diffs.html",
            "File Diffs",
            task_data['task_id'],
            content,
            "diffs"
        )
    
    def _write_detail_page(self, output_path: Path, title: str, task_id: str, content: str, content_type: str):
        """Write a detail page using the template."""
        template_path = self.templates_dir / "detail.html"
        if not template_path.exists():
            print(f"Error: Template not found: {template_path}")
            return
        
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        # Simple template replacement
        html_content = template_content.replace('{{ title }}', title)
        html_content = html_content.replace('{{ task_id }}', task_id)
        html_content = html_content.replace('{{ content }}', content)
        html_content = html_content.replace('{{ content_type }}', content_type)
        
        with open(output_path, 'w') as f:
            f.write(html_content)


def main():
    """Main function to generate HTML results."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate HTML results dashboard")
    parser.add_argument("--experiment-dir", type=Path, help="Experiment directory path")
    
    args = parser.parse_args()
    
    # Determine experiment directory
    if args.experiment_dir:
        experiment_dir = args.experiment_dir
    else:
        # Use latest experiment with results
        experiment_dir = get_latest_experiment_with_results()
        if not experiment_dir:
            print("Error: No experiments with results found. Run some tests first.")
            sys.exit(1)
        print(f"Using latest experiment: {experiment_dir}")
    
    # Generate HTML
    generator = ResultsHTMLGenerator(experiment_dir)
    success = generator.generate_all()
    
    if success:
        print(f"Successfully generated HTML dashboard")
        print(f"Open: {generator.html_dir / 'index.html'}")
    else:
        print("Failed to generate HTML dashboard")
        sys.exit(1)


if __name__ == "__main__":
    main()
