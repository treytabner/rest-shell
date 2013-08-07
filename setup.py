from setuptools import setup


setup(
    name='rest-shell',
    version='0.1',
    author = 'Trey Tabner',
    author_email = 'trey@tabner.com',
    url = 'https://github.com/treytabner/rest-shell',
    packages=['rest_shell'],
    entry_points={
        'console_scripts': [
            'rest-shell = rest_shell:main',
        ],
    },
    install_requires=[
        'Flask',
        'pyOpenSSL',
        'requests',
    ],
    license='GPLv3',
    description='RESTful shell for your server without shell access'
)
