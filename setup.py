import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='self_finance',
    version="0.0.1",
    author='Daniel Maksimovich',
    author_email='maksimovich.daniel@gmail.com',
    description='Analyze your finances transparently',
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords='bank, finance, money, personal, growth, projections',
    url="https://github.com/MaksimDan/self-finance",
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': ['self-finance=cli.__main__:run_from_command_line'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)