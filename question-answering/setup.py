#!/usr/bin/env python
from setuptools import setup, find_packages


install_requires = [
    "gensim",
    "bottle",
    "click",
    "paste",
    "numpy",
    "scipy",
    "Faker"
]

setup(
    name="questionanswering",
    version="0.0.1",
    author="The AutoGuru Team",
    author_email="",
    url="https://github.com/robrua/autoguru",
    description="Taking our jobs one Guru at a time",
    license="MIT",
    packages=find_packages(),
    zip_safe=True,
    install_requires=install_requires,
    include_package_data=True
)
