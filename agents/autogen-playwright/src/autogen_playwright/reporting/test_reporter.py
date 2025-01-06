from datetime import datetime
import json
import os
from pathlib import Path

class TestReport:
    def __init__(self, scenario_name):
        self.scenario_name = scenario_name
        self.start_time = datetime.now()
        self.steps = []
        self.screenshots = []
        self.status = "PENDING"
        
    def add_step(self, action, status, error=None):
        self.steps.append({
            "action": action,
            "status": status,
            "error": str(error) if error else None,
            "timestamp": datetime.now().isoformat()
        })
    
    def add_screenshot(self, path):
        self.screenshots.append(path)
    
    def to_dict(self):
        return {
            "scenario_name": self.scenario_name,
            "start_time": self.start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "status": self.status,
            "steps": self.steps,
            "screenshots": self.screenshots
        }
    
    def save(self, output_dir="test_reports"):
        Path(output_dir).mkdir(exist_ok=True)
        report_path = Path(output_dir) / f"report_{self.start_time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2) 