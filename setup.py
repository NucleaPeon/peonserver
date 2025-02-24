from setuptools import find_packages, setup

setup(
    name='peonserver',
    version='0.3.0',
    packages=find_packages(),
    scripts=[],
    entry_points={
        'console_scripts': [
            'pserver = peonserver.server:main',
            'pdaemon = peonserver.daemon:main',
            # 'wpcsetadminpw = wpcwebsite.db:resetadmin',
            # 'wpccheckadmin = wpcwebsite.db:checkadmin',
            # 'wpcdeploy = wpcwebsite.deploy:main'
        ]
    }
)
