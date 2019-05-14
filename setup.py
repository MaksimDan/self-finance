import os

from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), 'VERSION'), 'r') as version_file:
    setup(
        name='self_finance',
        version=version_file.read().strip(),
        packages=find_packages(),
        author='Daniel Maksimovich',
        author_email='maksimovich.daniel@gmail.com',
        description='Analyze your finances transparently',
        keywords='bank, finance, money, personal, growth, projections',
        include_package_data=True,
        install_requires=['flask']
    )
