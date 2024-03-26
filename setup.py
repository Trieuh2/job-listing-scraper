from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='job_listing_scraper',
    version='0.1',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'run_scraper=main:main'
        ],
    },
    description='Job search results scraper tool designed to parse, filter, and store more relevant job results in a working Excel spreadsheet.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Trieuh2/job-listing-scraper',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent'
    ],
)
