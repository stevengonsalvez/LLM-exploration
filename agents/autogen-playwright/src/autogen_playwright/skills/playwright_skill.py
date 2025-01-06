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

class PlaywrightSkill:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None
        self.report = None
        self.screenshot_dir = Path("screenshots")
        self.screenshot_dir.mkdir(exist_ok=True)
        
    def start_session(self, scenario_name="Unnamed Scenario"):
        """Initialize playwright session and reporting"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)
        self.page = self.browser.new_page()
        self.report = TestReport(scenario_name)
        return "Browser session started successfully"
    
    def _take_screenshot(self, name):
        """Capture screenshot with timestamp"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        path = self.screenshot_dir / f"{name}_{timestamp}.png"
        self.page.screenshot(path=str(path))
        self.report.add_screenshot(str(path))
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
            self._take_screenshot("navigation_error")
            self.report.add_step(f"Navigate to {url}", "FAILED", error=e)
            raise

    def click_element(self, selector, retry_count=3):
        """Click an element with retry mechanism"""
        try:
            result = self._retry_with_different_selectors(self.page.click, selector)
            self.report.add_step(f"Click {selector}", "SUCCESS")
            return f"Clicked element: {selector}"
        except Exception as e:
            self._take_screenshot("click_error")
            self.report.add_step(f"Click {selector}", "FAILED", error=e)
            return f"Error clicking element: {str(e)}"

    def fill_form(self, selector, value, retry_count=3):
        """Fill a form field with retry mechanism"""
        try:
            result = self._retry_with_different_selectors(self.page.fill, selector, value)
            self.report.add_step(f"Fill {selector} with {value}", "SUCCESS")
            return f"Filled {selector} with {value}"
        except Exception as e:
            self._take_screenshot("fill_error")
            self.report.add_step(f"Fill {selector} with {value}", "FAILED", error=e)
            return f"Error filling form: {str(e)}"

    def verify_element_exists(self, selector, timeout=5000):
        """Verify element exists with timeout"""
        try:
            self.page.wait_for_selector(selector, timeout=timeout)
            self.report.add_step(f"Verify {selector} exists", "SUCCESS")
            return True
        except PlaywrightTimeout:
            self._take_screenshot("verification_error")
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
            self._take_screenshot("text_verification_error")
            self.report.add_step(f"Verify text '{text}' exists", "FAILED",
                               error="Text not found within timeout")
            return False

    def end_session(self, status="COMPLETED"):
        """Clean up and save report"""
        if self.report:
            self.report.status = status
            self.report.save()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop() 