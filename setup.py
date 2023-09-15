from setuptools import setup

setup(
    name='grandstart',
    version='0.1.0',
    package_dir={'': 'src'},
    install_requires=[
        'click==8.1.3',
        'cryptography==39.0.1',
        'inotify==0.2.10',
        'loguru==0.7.0',
        'passlib[bcrypt]==1.7.4',
        'pyyaml==6.0',
        'pydantic==1.10.2',
        'pydantic[email]',
        'python-dotenv==0.21.0',
        'python-jose[cryptography]==3.3.0',
    ],
    entry_points={
        'console_scripts': [
            'grandstart = app.cli.start:cli',
        ],
    },
)