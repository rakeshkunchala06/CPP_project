"""Setup configuration for transit-access-nci package."""

from setuptools import setup, find_packages

setup(
    name="transit-access-nci",
    version="1.0.0",
    author="Rakesh Kunchala",
    author_email="rakesh.kunchala@student.nci.ie",
    description="Accessible Public Transit Trip Planner Utilities",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/rakeshkunchala06/CPP_project",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[],
    extras_require={
        "dev": ["pytest>=7.0", "pytest-cov>=4.0"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: GIS",
    ],
)
