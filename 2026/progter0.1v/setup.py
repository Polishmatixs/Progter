from setuptools import setup, find_packages

setup(
    name="progter",
    version="0.1.0",
    description="AI-powered terminal code assistant",
    packages=find_packages(),
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "progter=progter.cli:main",
        ],
    },
)
