from setuptools import find_packages, setup

setup(
    name='peonserver',
    version='1.2.1',
    packages=find_packages(),
    scripts=[],
    entry_points={
        'console_scripts': [
            'pserver = peonserver.server:main',
            'pdaemon = peonserver.daemon:main',
            'create-website = peonserver.scripts.create_website:main'
        ]
    }
)
