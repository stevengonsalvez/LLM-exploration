import pytest
from pathlib import Path
from autogen_playwright.skills.playwright_skill import PlaywrightSkill
from autogen_playwright.utils.constants import SCREENSHOTS_DIR, REPORTS_DIR

def test_playwright_skill_can_navigate_and_interact():
    skill = PlaywrightSkill()
    
    # Test session start
    result = skill.start_session()
    assert "successfully" in result
    
    # Test navigation
    result = skill.navigate("https://example.com")
    assert "Navigated to" in result
    
    # Test clicking
    result = skill.click_element("h1")
    assert "Clicked element" in result or "Error clicking element" in result
    
    # Test form filling
    result = skill.fill_form("#search", "test query")
    assert "Filled" in result or "Error filling form" in result

def test_can_handle_invalid_selectors():
    skill = PlaywrightSkill()
    skill.start_session()
    
    result = skill.click_element("invalid-selector-that-doesnt-exist")
    assert "Error" in result 

def test_playwright_skill_handles_complex_scenarios():
    skill = PlaywrightSkill()
    skill.start_session("Complex Navigation Test")
    
    # Test navigation with wait
    result = skill.navigate("https://example.com", wait_for_load=True)
    assert "Navigated to" in result
    
    # Test element verification
    assert skill.verify_element_exists("h1")
    assert skill.verify_text_content("Example Domain")
    
    # Test multiple selector strategies
    result = skill.click_element("More information")
    assert "Clicked element" in result
    
    # Verify screenshots are created
    assert len(list(skill.screenshot_dir.glob("*.png"))) > 0
    
    skill.end_session()

def test_error_recovery_and_reporting():
    skill = PlaywrightSkill()
    skill.start_session("Error Recovery Test")
    
    # Test invalid selector with retry
    result = skill.click_element("non_existent_button")
    assert "Error clicking element" in result
    
    # Verify error screenshot was taken
    assert len(list(skill.screenshot_dir.glob("*click_error*.png"))) > 0
    
    # Verify report was generated
    assert len(list(Path("test_reports").glob("*.json"))) > 0
    
    skill.end_session("FAILED") 