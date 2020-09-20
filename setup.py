"""
Install development package: pip install -e .
"""

import setuptools

setuptools.setup(
    name="vocabulary-RR",  # Replace with your own username
    version="0.1",
    author="Robert Radnai",
    description="Vocabulary app package",
    packages=setuptools.find_packages(),
    classifiers=[
    ],
    install_requires=['ngram', 'openpyxl'],
    python_requires='>=3.6'
)
