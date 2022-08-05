import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="billy",
    version="1.0",
    author="Adrian Dolha",
    packages=['billy_api'],
    author_email="adriandolha@eyahoo.com",
    description="Expenses and bills Insights API",
    long_description=long_description,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
