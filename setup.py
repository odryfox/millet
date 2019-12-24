import io

from setuptools import find_packages
from setuptools import setup

from src import dialogus


with io.open("README.rst") as f:
    readme = f.read()


setup(
    name='Dialogus',
    version=dialogus.__version__,
    project_urls={
        "Code": "https://github.com/odryfox/dialogus",
        "Issue tracker": "https://github.com/odryfox/dialogus/issues",
    },
    license="BSD-3-Clause",
    author="Vyacheslav Rusov",
    author_email="odryfox@gmail.com",
    description="A simple framework for building complex dialogue systems.",
    long_description=readme,
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    extras_require={
        "dev": [
            "pytest",
        ],
    },
)
