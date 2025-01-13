import os
import logging
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

def find_env_file() -> Path:
    """Find the .env file in the project root
    
    Returns:
        Path: Path to the .env file
        
    Raises:
        FileNotFoundError: If no .env file is found in any of the expected locations
    """
    current_dir = Path.cwd()
    
    # First check in current directory
    env_path = current_dir / '.env'
    if env_path.exists():
        return env_path
        
    # Then check in project root (up one level from examples)
    project_root = current_dir.parent if current_dir.name == 'examples' else current_dir
    env_path = project_root / '.env'
    if env_path.exists():
        return env_path
        
    # Finally check in parent directory
    env_path = project_root.parent / '.env'
    if env_path.exists():
        return env_path
        
    raise FileNotFoundError("Could not find .env file in project directories")

def load_env_from_file() -> Path:
    """Load environment variables from .env file
    
    Returns:
        Path: Path to the loaded .env file
        
    Raises:
        FileNotFoundError: If no .env file is found
    """
    env_path = find_env_file()
    load_dotenv(dotenv_path=env_path, override=True)
    logger.info("Loaded environment from %s", env_path)
    return env_path 