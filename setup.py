import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="papr",
    version="0.0.5",
    entry_points = {
        "console_scripts": ['papr = papr.cli:main']
        },
    author="Daniel Etzold",
    author_email="detzold@gmail.com",
    description="A command line tool to manage scientific papers.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/daniel-e/papr",
    packages=['papr'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'keyboard',
        'bs4',
        'termcolor'
    ]
)
