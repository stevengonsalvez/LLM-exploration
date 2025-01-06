import os
from datetime import datetime
from typing import List, Optional
from pathlib import Path

def find_script_root() -> Path:
    """Find the root directory relative to the script location"""
    # Get the directory containing the script
    script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    # Go up to the project root (autogen-playwright)
    project_root = script_dir.parent.parent.parent
    return project_root

class TestReport:
    # Default report location in script's project root
    DEFAULT_REPORT_DIR = find_script_root() / "reports"

    def __init__(self, scenario_name: str, report_dir: Optional[Path] = None, enabled: bool = True):
        """
        Initialize test reporter
        Args:
            scenario_name: Name of the test scenario
            report_dir: Custom report directory (defaults to project_root/reports)
            enabled: Whether to generate reports (defaults to True)
        """
        self.scenario_name = scenario_name
        self.run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.steps: List[dict] = []
        self.screenshots: List[str] = []
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
        self.status = "Running"
        self.enabled = enabled
        
        if self.enabled:
            # Use custom report dir if provided, otherwise use default
            base_dir = report_dir if report_dir else self.DEFAULT_REPORT_DIR
            self.report_dir = base_dir / f"run_{self.run_id}"
            self.report_dir.mkdir(parents=True, exist_ok=True)
            print(f"\nTest reports will be saved to: {self.report_dir.absolute()}")
        
    def add_step(self, description: str, status: str = "Success", error: Optional[str] = None):
        """Add a test step to the report"""
        step = {
            "description": description,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "error": error
        }
        self.steps.append(step)
        
        # Always print to console regardless of reporting status
        print(f"\n{step['timestamp']} - {description}")
        if error:
            print(f"Error: {error}")
        
    def add_screenshot(self, screenshot_path: str):
        """Add a screenshot to the report"""
        if not self.enabled:
            return

        if os.path.exists(screenshot_path):
            # Copy screenshot to report directory
            new_path = self.report_dir / Path(screenshot_path).name
            os.rename(screenshot_path, new_path)
            self.screenshots.append(str(new_path))
            print(f"Screenshot saved: {new_path}")
        
    def complete(self, status: str):
        """Complete the test report"""
        self.end_time = datetime.now()
        self.status = status
        
        if self.enabled:
            self._generate_markdown()
            print(f"\nTest completed with status: {status}")
            print(f"Report available at: {self.report_dir / 'report.md'}")
            # Generate and print summary
            self._print_summary()
        else:
            print(f"\nTest completed with status: {status}")
            print("Reporting is disabled - no report file generated")
            
    def _print_summary(self):
        """Generate and print a test summary"""
        print("\nTest Summary:")
        print(f"1. The test \"{self.scenario_name}\" started at {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}.")
        
        # Print each step
        for i, step in enumerate(self.steps[1:], 2):  # Start from 1 to skip the "Started browser session" step
            print(f"{i}. {step['description']}")
            
        # Print screenshot info if any
        if self.screenshots:
            print(f"{len(self.steps) + 1}. Screenshots were taken and saved in: {self.report_dir}")
            
        # Print completion status
        print(f"{len(self.steps) + 2}. Test completed with status: {self.status}")
        print(f"\nYou can find the full test report at: {self.report_dir / 'report.md'}")
        
    def _generate_markdown(self):
        """Generate markdown report"""
        if not self.enabled:
            return

        report = f"""# Test Report: {self.scenario_name}

## Summary
- Run ID: {self.run_id}
- Start Time: {self.start_time.isoformat()}
- End Time: {self.end_time.isoformat() if self.end_time else 'N/A'}
- Status: {self.status}

## Test Steps
"""
        for i, step in enumerate(self.steps, 1):
            report += f"\n### Step {i}: {step['description']}\n"
            report += f"- Status: {step['status']}\n"
            report += f"- Time: {step['timestamp']}\n"
            if step.get('error'):
                report += f"- Error: {step['error']}\n"
                
        if self.screenshots:
            report += "\n## Screenshots\n"
            for screenshot in self.screenshots:
                relative_path = os.path.relpath(screenshot, self.report_dir)
                report += f"\n![Screenshot]({relative_path})\n"
                
        report_path = self.report_dir / "report.md"
        with open(report_path, "w") as f:
            f.write(report) 