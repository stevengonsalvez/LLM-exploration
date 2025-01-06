# Default configurations
SCREENSHOTS_DIR = "screenshots"
DEFAULT_TIMEOUT = 30000  # 30 seconds
DEFAULT_RETRY_COUNT = 3

# Browser configuration
BROWSER_CONFIG = {
    "headless": False,
    "slow_mo": 50,  # Slow down operations by 50ms
    "viewport": {
        "width": 1280,
        "height": 720
    }
} 