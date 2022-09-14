import os
import setuptools

description = "A Python wrapper for the RuWordNet thesaurus."
long_description = description
if os.path.exists("README.md"):
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()


setuptools.setup(
    name="ruwordnet",
    version="0.0.4",
    author="David Dale",
    author_email="dale.david@mail.ru",
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/avidale/python-ruwordnet",
    packages=setuptools.find_packages(),
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['sqlalchemy'],
    entry_points={
        "console_scripts": [
            "ruwordnet=ruwordnet.__main__:main",
        ]
    }
)
