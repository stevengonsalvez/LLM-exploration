from setuptools import setup, find_packages
from pathlib import Path

# Read README.md if it exists, otherwise use a default description
readme_path = Path("README.md")
long_description = """
AutoGen Playwright - Web Testing Framework
A framework for automated web testing using AutoGen agents and Playwright.
""".strip()

if readme_path.exists():
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="autogen-playwright",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pyautogen",
        "playwright",
        "python-dotenv",
    ],
    extras_require={
        "dev": [
            "pytest",
            "black",
            "flake8",
        ]
    },
    python_requires=">=3.9",
    author="Your Name",
    author_email="your.email@example.com",
    description="Playwright testing with AutoGen agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/autogen-playwright",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
) 