from datetime import datetime
import json
import os
from pathlib import Path
import shutil

class TestReport:
    def __init__(self, scenario_name):
        self.scenario_name = scenario_name
        self.start_time = datetime.now()
        self.steps = []
        self.screenshots = []
        self.status = "PENDING"
        
        # Get execution directory (where the script is run from)
        self.execution_dir = Path.cwd()
        
        # Create reports directory structure in execution directory
        self.reports_dir = self.execution_dir / "reports"
        self.reports_dir.mkdir(exist_ok=True)
        
        # Create timestamped directory for this run
        self.timestamp = self.start_time.strftime('%Y%m%d_%H%M%S')
        self.run_dir = self.reports_dir / f"run_{self.timestamp}"
        self.run_dir.mkdir(exist_ok=True)
        
        # Create screenshots directory within run directory
        self.screenshots_dir = self.run_dir / "screenshots"
        self.screenshots_dir.mkdir(exist_ok=True)
        
        print(f"Reports will be saved to: {self.reports_dir.absolute()}")
        
    def add_step(self, action, status, error=None):
        self.steps.append({
            "action": action,
            "status": status,
            "error": str(error) if error else None,
            "timestamp": datetime.now().isoformat()
        })
    
    def add_screenshot(self, path):
        # Copy screenshot to run directory and store relative path
        src_path = Path(path)
        if src_path.exists():
            dest_path = self.screenshots_dir / src_path.name
            shutil.copy2(src_path, dest_path)
            self.screenshots.append(str(dest_path.relative_to(self.run_dir)))
    
    def generate_markdown(self):
        """Generate markdown report"""
        md = [
            f"# Test Execution Report: {self.scenario_name}",
            f"\nExecution Date: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"\nStatus: {self.status}",
            "\n## Test Steps\n"
        ]
        
        for i, step in enumerate(self.steps, 1):
            md.append(f"{i}. **{step['action']}**")
            md.append(f"   - Status: {step['status']}")
            if step['error']:
                md.append(f"   - Error: {step['error']}")
            md.append("")
        
        if self.screenshots:
            md.append("\n## Screenshots\n")
            for screenshot in self.screenshots:
                md.append(f"![Screenshot]({screenshot})")
                md.append("")
        
        return "\n".join(md)
    
    def save(self):
        """Save both JSON and Markdown reports"""
        # Save JSON report
        json_path = self.run_dir / "report.json"
        with open(json_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
            
        # Save Markdown report
        md_path = self.run_dir / "report.md"
        with open(md_path, 'w') as f:
            f.write(self.generate_markdown())
            
        return str(self.run_dir)
    
    def to_dict(self):
        return {
            "scenario_name": self.scenario_name,
            "start_time": self.start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "status": self.status,
            "steps": self.steps,
            "screenshots": self.screenshots
        } 