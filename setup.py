from setuptools import setup


setup(
    name='rest-shell',
    packages=['rest_shell'],
    entry_points={
        'console_scripts': [
            'rest-shell = rest_shell:main',
        ],
    },
    version='1.0',
    install_requires=[
        'bottle',
        'requests',
    ],
    license='GPLv3',
    description='RESTful shell for your server without shell access'
)
