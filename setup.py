from setuptools import setup

setup(
    name='transformers',
    version='0.0.0a',
    packages=['transformers', 'tests'],
    url='https://github.com/invanalabs/data-transformers',
    license='MIT',
    author='Ravi RT Merugu',
    author_email='ravi@invanalabs.ai',
    description='A library to transforming JSON with parsers.',
    install_requires=[
        'JSONBender==0.9.3',
        'pymongo==3.7.2'
    ],
)