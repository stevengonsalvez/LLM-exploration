from setuptools import setup, find_packages

setup(
    name="autogen-playwright",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "pyautogen>=0.2.0",
        "playwright>=1.39.0",
        "python-dotenv>=0.19.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ],
    },
    python_requires=">=3.8",
) 