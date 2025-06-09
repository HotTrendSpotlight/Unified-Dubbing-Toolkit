"""
Setup script for Unified Dubbing System
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = requirements_file.read_text().strip().split('\n')
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith('#')]

setup(
    name="unified-dubbing-system",
    version="1.0.0",
    author="Unified Dubbing System Team",
    author_email="contact@unifieddubbing.com",
    description="A comprehensive, modular dubbing toolkit integrating multiple AI technologies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HotTrendSpotlight/Unified-Dubbing-Toolkit",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Multimedia :: Video",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.2.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
            "mypy>=0.910",
        ],
        "gpu": [
            "torch>=1.9.0+cu111",
            "torchaudio>=0.9.0+cu111",
        ],
        "all": [
            "whisperx>=3.1.0",
            "pyannote.audio>=3.0.0",
            "kokoro>=1.0.0",
            "resemblyzer>=0.1.1",
        ]
    },
    entry_points={
        "console_scripts": [
            "unified-dubbing=unified_dubbing_system.__main__:main",
        ],
    },
    include_package_data=True,
    package_data={
        "unified_dubbing_system": [
            "config/*.yaml",
            "config/*.json",
        ],
    },
    zip_safe=False,
)