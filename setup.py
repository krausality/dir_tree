# setup.py

from setuptools import setup, find_packages

setup(
    name='dir_tree',
    version='0.1',
    packages=find_packages(),
    install_requires=[],  # Add any dependencies here
    entry_points={
        'console_scripts': [
            'dir-tree=dir_tree.directory_tree:main',  # Adds `dir-tree` command to the CLI
        ],
    },
    author='Your Name',
    author_email='krausality42@gmail.com',
    description='A package for generating directory trees with exclusions.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/krausality/dir_tree',  # Update this if hosting the package
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',
)
