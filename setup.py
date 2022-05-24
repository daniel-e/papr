import setuptools
from setuptools import find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="papr",
    version="0.0.20",
    entry_points = {
        "console_scripts": ['papr = papr.cli:main']
        },
    author="Daniel Etzold",
    author_email="detzold@gmail.com",
    description="A command line tool to manage scientific papers.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/daniel-e/papr",
    packages=['papr', 'papr/lib', 'papr/lib/migration'],
    package_data={'papr': ['html/*']},
    #include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'bs4',
        'termcolor',
        'Markdown',
        'pyyaml'
    ]
)
