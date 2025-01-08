from typing import Optional
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from ..reporting.test_reporter import TestReport

class PlaywrightSkill:
    def __init__(self, report_dir: Optional[Path] = None, reporting_enabled: bool = True,
                 timeout: int = 5000, slow_mo: int = 100):
        """
        Initialize PlaywrightSkill
        Args:
            report_dir: Custom report directory (defaults to ./reports)
            reporting_enabled: Whether to generate reports (defaults to True)
            timeout: Default timeout in milliseconds for actions (default 5000ms)
            slow_mo: Delay between actions in milliseconds (default 100ms)
        """
        self.browser = None
        self.context = None
        self.page = None
        self.report = None
        self.report_dir = report_dir
        self.reporting_enabled = reporting_enabled
        self.timeout = timeout
        self.slow_mo = slow_mo
        
    def start_session(self, scenario_name: str):
        """Start a new browser session"""
        self.report = TestReport(
            scenario_name,
            report_dir=self.report_dir,
            enabled=self.reporting_enabled
        )
        playwright = sync_playwright().start()
        
        # Launch browser in headed mode with slower execution for visibility
        self.browser = playwright.chromium.launch(
            headless=False,  # Show the browser
            slow_mo=self.slow_mo  # Add delay between actions for visibility
        )
        
        # Configure viewport and create context
        self.context = self.browser.new_context(
            viewport={'width': 1280, 'height': 720}
        )
        self.page = self.context.new_page()
        # Set default timeout for all operations
        self.page.set_default_timeout(self.timeout)
        self.report.add_step("Started browser session", "Success")
        
    def navigate(self, url: str, wait_for_load: bool = True):
        """Navigate to a URL"""
        try:
            self.page.goto(url, wait_until='networkidle' if wait_for_load else 'commit', timeout=self.timeout)
            self.report.add_step(f"Navigated to {url}", "Success")
        except PlaywrightTimeout as e:
            self.report.add_step(f"Navigation timeout for {url}", "Warning", str(e))
            # Continue execution as page might have loaded enough
        except Exception as e:
            self.report.add_step(f"Failed to navigate to {url}", "Error", str(e))
            raise
            
    def fill_form(self, selector: str, value: str):
        """Fill a form field"""
        try:
            self.page.fill(selector, value, timeout=self.timeout)
            self.report.add_step(f"Filled form field {selector} with value {value}", "Success")
        except Exception as e:
            self.report.add_step(f"Failed to fill form field {selector}", "Error", str(e))
            raise
            
    def click_element(self, selector: str):
        """Click an element"""
        try:
            self.page.click(selector, timeout=self.timeout)
            self.report.add_step(f"Clicked element {selector}", "Success")
        except PlaywrightTimeout as e:
            self.report.add_step(f"Click timeout for {selector}", "Warning", str(e))
            # Try force click as fallback
            try:
                self.page.evaluate(f"document.querySelector('{selector}').click()")
                self.report.add_step(f"Force clicked element {selector}", "Success")
            except Exception as force_e:
                raise Exception(f"Both normal and force click failed: {str(e)}, {str(force_e)}")
        except Exception as e:
            self.report.add_step(f"Failed to click element {selector}", "Error", str(e))
            raise
            
    def verify_element_exists(self, selector: str):
        """Verify an element exists"""
        try:
            element = self.page.query_selector(selector)
            if element:
                self.report.add_step(f"Verified element {selector} exists", "Success")
                return True
            else:
                self.report.add_step(f"Element {selector} not found", "Failed")
                return False
        except Exception as e:
            self.report.add_step(f"Error verifying element {selector}", "Error", str(e))
            raise
            
    def verify_text_content(self, text: str):
        """Verify text exists on page"""
        try:
            content = self.page.text_content('body')
            if text in content:
                self.report.add_step(f"Verified text '{text}' exists on page", "Success")
                return True
            else:
                self.report.add_step(f"Text '{text}' not found on page", "Failed")
                return False
        except Exception as e:
            self.report.add_step(f"Error verifying text '{text}'", "Error", str(e))
            raise
            
    def take_screenshot(self, name: str, full_page: bool = False):
        """Take a screenshot"""
        try:
            screenshot_path = f"{name}.png"
            self.page.screenshot(path=screenshot_path, full_page=full_page)
            self.report.add_screenshot(screenshot_path)
            self.report.add_step(f"Took screenshot {name}", "Success")
        except Exception as e:
            self.report.add_step(f"Failed to take screenshot {name}", "Error", str(e))
            raise
            
    def end_session(self, status: str = "Completed"):
        """End the browser session and save report"""
        try:
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.report:
                self.report.complete(status)
            self.report.add_step("Ended browser session", "Success")
        except Exception as e:
            if self.report:
                self.report.add_step("Failed to end session cleanly", "Error", str(e))
            raise 