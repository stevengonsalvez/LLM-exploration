from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import time
from pathlib import Path
from datetime import datetime
from autogen_playwright.reporting.test_reporter import TestReport
from autogen_playwright.utils.constants import (
    SCREENSHOTS_DIR,
    DEFAULT_TIMEOUT,
    DEFAULT_RETRY_COUNT,
    BROWSER_CONFIG
)
from subprocess import run

class PlaywrightSkill:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None
        self.report = None
        
        # Use execution directory for screenshots
        self.screenshot_dir = Path.cwd() / "screenshots"
        self.screenshot_dir.mkdir(exist_ok=True)
        
        self.failed_steps = []
        self.max_retries = 5
        
        # Install browsers if needed
        try:
            print("Checking Playwright installation...")
            run(["playwright", "install", "chromium"], check=True)
            print("Playwright browsers installed successfully")
        except Exception as e:
            print(f"Error installing Playwright browsers: {e}")
            
    def start_session(self, scenario_name="Unnamed Scenario"):
        """Initialize playwright session and reporting"""
        print(f"\nStarting test scenario: {scenario_name}")
        self.playwright = sync_playwright().start()
        
        # Launch browser with explicit configuration
        print("Launching browser...")
        self.browser = self.playwright.chromium.launch(
            headless=False,  # Force headed mode
            slow_mo=500,     # Slow down for visibility
        )
        
        # Configure viewport
        context = self.browser.new_context(
            viewport={'width': 1280, 'height': 720}
        )
        self.page = context.new_page()
        
        self.report = TestReport(scenario_name)
        print("Browser session started successfully")
        return "Browser session started successfully"
    
    def take_screenshot(self, name: str, full_page: bool = False) -> str:
        """Capture screenshot of the current page state"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        path = self.screenshot_dir / f"{name}_{timestamp}.png"
        
        print(f"Taking screenshot: {name}")
        self.page.screenshot(
            path=str(path),
            full_page=full_page
        )
        self.report.add_screenshot(str(path))
        print(f"Screenshot saved: {path}")
        return str(path)

    def _retry_with_different_selectors(self, action, selector, *args):
        """Try different selector strategies"""
        selector_strategies = [
            selector,  # Original selector
            f"text={selector}",  # Try text content
            f"[aria-label*='{selector}']",  # Try aria-label
            f"[title*='{selector}']",  # Try title attribute
            f"[data-testid*='{selector}']",  # Try test ID
        ]
        
        last_error = None
        for strategy in selector_strategies:
            try:
                return action(strategy, *args)
            except Exception as e:
                last_error = e
                time.sleep(1)  # Brief pause between retries
        
        raise last_error

    def navigate(self, url, wait_for_load=True):
        """Navigate to specified URL with enhanced error handling"""
        try:
            response = self.page.goto(url, wait_until="networkidle" if wait_for_load else "commit")
            self.report.add_step(f"Navigate to {url}", "SUCCESS")
            return f"Navigated to {url}"
        except Exception as e:
            self.take_screenshot("navigation_error")
            self.report.add_step(f"Navigate to {url}", "FAILED", error=e)
            raise

    def click_element(self, selector, retry_count=3):
        """Click an element with retry mechanism"""
        try:
            result = self._retry_with_different_selectors(self.page.click, selector)
            self.report.add_step(f"Click {selector}", "SUCCESS")
            return f"Clicked element: {selector}"
        except Exception as e:
            self.take_screenshot("click_error")
            self.report.add_step(f"Click {selector}", "FAILED", error=e)
            return f"Error clicking element: {str(e)}"

    def fill_form(self, selector, value, retry_count=3):
        """Fill a form field with retry mechanism"""
        try:
            result = self._retry_with_different_selectors(self.page.fill, selector, value)
            self.report.add_step(f"Fill {selector} with {value}", "SUCCESS")
            return f"Filled {selector} with {value}"
        except Exception as e:
            self.take_screenshot("fill_error")
            self.report.add_step(f"Fill {selector} with {value}", "FAILED", error=e)
            return f"Error filling form: {str(e)}"

    def verify_element_exists(self, selector, timeout=5000):
        """Verify element exists with timeout"""
        try:
            self.page.wait_for_selector(selector, timeout=timeout)
            self.report.add_step(f"Verify {selector} exists", "SUCCESS")
            return True
        except PlaywrightTimeout:
            self.take_screenshot("verification_error")
            self.report.add_step(f"Verify {selector} exists", "FAILED", 
                               error="Element not found within timeout")
            return False

    def verify_text_content(self, text, timeout=5000):
        """Verify text exists on page"""
        try:
            self.page.wait_for_selector(f"text={text}", timeout=timeout)
            self.report.add_step(f"Verify text '{text}' exists", "SUCCESS")
            return True
        except PlaywrightTimeout:
            self.take_screenshot("text_verification_error")
            self.report.add_step(f"Verify text '{text}' exists", "FAILED",
                               error="Text not found within timeout")
            return False

    def _handle_error(self, action: str, error: Exception, context: str = None):
        """Handle errors and maintain failure records"""
        error_msg = f"{action} failed: {str(error)}"
        if context:
            error_msg = f"{error_msg} (Context: {context})"
            
        self.failed_steps.append(error_msg)
        self.take_screenshot(f"error_{action.lower().replace(' ', '_')}")
        return error_msg
        
    def get_test_summary(self) -> dict:
        """Get summary of test execution"""
        return {
            "total_steps": len(self.report.steps),
            "failed_steps": self.failed_steps,
            "screenshots": self.report.screenshots,
            "status": self.report.status,
            "start_time": self.report.start_time,
            "end_time": datetime.now()
        }
        
    def end_session(self, status="COMPLETED"):
        """Clean up and save report with summary"""
        try:
            summary = self.get_test_summary()
            print("\nTest Execution Summary:")
            print("-" * 50)
            print(f"Total Steps: {summary['total_steps']}")
            print(f"Failed Steps: {len(summary['failed_steps'])}")
            if summary['failed_steps']:
                print("\nFailures:")
                for failure in summary['failed_steps']:
                    print(f"- {failure}")
            print(f"\nScreenshots captured: {len(summary['screenshots'])}")
            print(f"Test Status: {status}")
            
            self.report.status = status
            report_dir = self.report.save()
            print(f"\nDetailed report available at: {report_dir}")
            
        finally:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop() 