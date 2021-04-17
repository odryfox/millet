import io
import re

from setuptools import find_packages, setup

with io.open('README.rst', 'rt', encoding='utf8') as f:
    readme = f.read()

with io.open('src/millet/__init__.py', 'rt', encoding='utf8') as f:
    version = re.search(r'__version__ = \'(.*?)\'', f.read()).group(1)

setup(
    name='Millet',
    version=version,
    project_urls={
        'Code': 'https://github.com/odryfox/millet',
        'Issue tracker': 'https://github.com/odryfox/millet/issues',
    },
    license='BSD-3-Clause',
    author='Vyacheslav Rusov',
    author_email='odryfox@gmail.com',
    description='A simple framework for building complex dialogue systems.',
    long_description=readme,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    extras_require={
        'dev': [
            'pytest',
            'mkdocs',
            'redis',
            'isort',
        ],
        'docs': [
            'mkdocs',
        ],
    },
)
