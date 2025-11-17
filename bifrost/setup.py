from setuptools import setup, find_packages

setup(
    name="bifrost",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "typer>=0.12.0",
        "requests>=2.31.0",
        "rich>=13.7.0",
    ],
    entry_points={
        "console_scripts": [
            "bifrost=bifrost.main:main",
        ],
    },
    python_requires=">=3.8",
)
