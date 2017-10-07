# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='orion-wicm',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='v1.0',

    description='WICM client',
    long_description=long_description,

    # The project's main homepage.
    url='',

    # Author details
    author='Stavros Kolometsos',
    author_email='skolometsos@orioninnovations.gr',

    # Choose your license
    license='',

    # What does your project relate to?
    keywords='SDN Management',

    packages=find_packages(),
    install_requires=['pytricia', 'Flask>=0.10.1', 'Flask-RESTful', 'requests','SQLAlchemy'],

    setup_requires=['pytest-runner'],
    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    #entry_points={
    #    'console_scripts': [
    #        'sample=sample:main',
    #    ],
    #},
)
