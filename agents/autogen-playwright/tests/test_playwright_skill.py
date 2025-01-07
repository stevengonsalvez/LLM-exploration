import pytest
from pathlib import Path

# Mark all tests in this file as async
pytestmark = pytest.mark.asyncio

async def test_start_session(skill):
    """Test browser session initialization"""
    # We now have the actual PlaywrightSkill instance, not a generator
    try:
        await skill.start_session("Test Scenario")
        assert skill.browser is not None, "Browser should be initialized"
        assert skill.context is not None, "Context should be initialized"
        assert skill.page is not None, "Page should be initialized"
    finally:
        # Clean up after this test
        if skill.page:
            await skill.end_session()

async def test_navigation(skill):
    """Test page navigation"""
    try:
        await skill.start_session("Navigation Test")
        test_url = "https://example.com"
        await skill.navigate(test_url)
        assert skill.page.url == test_url, f"Expected URL {test_url}, got {skill.page.url}"
    finally:
        if skill.page:
            await skill.end_session()

async def test_element_interaction(skill):
    """Test element interactions"""
    try:
        await skill.start_session("Element Test")
        await skill.navigate("https://example.com")
        
        assert await skill.verify_element_exists("h1"), "H1 element should exist"
        assert not await skill.verify_element_exists("non-existent-element")
        assert await skill.verify_text_content("Example Domain")
        assert not await skill.verify_text_content("Non-existent Text")
    finally:
        if skill.page:
            await skill.end_session()

async def test_screenshot(skill):
    """Test screenshot functionality"""
    try:
        await skill.start_session("Screenshot Test")
        await skill.navigate("https://example.com")
        
        screenshot_name = "test_screenshot"
        await skill.take_screenshot(screenshot_name)
        assert Path(f"{screenshot_name}.png").exists()
    finally:
        if skill.page:
            await skill.end_session()

async def test_error_handling(skill):
    """Test error handling scenarios"""
    try:
        await skill.start_session("Error Test")
        
        with pytest.raises(Exception):
            await skill.navigate("https://non-existent-domain.invalid")
            
        with pytest.raises(Exception):
            await skill.click_element("#non-existent")
            
        with pytest.raises(Exception):
            await skill.fill_form("#non-existent", "test value")
    finally:
        if skill.page:
            await skill.end_session()