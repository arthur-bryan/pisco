from setuptools import setup

with open("README.md", "r") as file:
    long_description = file.read()

setup(
    name='pisco',
    version='0.1.0-pre-alpha',
    description='Automate the configuration of Cisco devices.',
    long_description=long_description,
    author='Arthur Bryan',
    license="MIT",
    author_email='arthurbryan2030@gmail.com',
    url='https://github.com/arthur-bryan/pisco',
    python_requires='>=3.7',
    packages=['pisco'],
    package_data={'pisco': ['../data/*']},
    install_requires=[
        'bcrypt>=3.1.7',
        'cffi>=1.14.1',
        'cryptography>=3.0',
        'paramiko>=2.7.1',
        'pycparser>=2.20',
        'PyNaCl>=1.4.0',
        'six>=1.15.0'
    ],
    entry_points={'console_scripts': ['pisco = pisco.__init__']}
)
