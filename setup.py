#!/usr/bin/env python3
"""Setup script for rfd-sovereign-stack package."""

from setuptools import setup, find_packages

if __name__ == "__main__":
    setup(
        packages=find_packages() + find_packages(where="gaming-platform"),
        package_dir={"gaming_platform": "gaming-platform/gaming_platform"},
        include_package_data=True,
    )
