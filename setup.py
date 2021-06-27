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
    install_requires=['et-xmlfile==1.0.1', 'jdcal==1.4.1', "ngram==3.3.2", "openpyxl==3.0.5",
                      "dataclasses-json==0.5.4"],
    python_requires='>=3.6'
)
