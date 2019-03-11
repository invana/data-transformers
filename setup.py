from setuptools import setup

setup(
    name='invana-transformers',
    version='0.0.0b',
    packages=['transformers', 'tests'],
    url='https://github.com/invanalabs/data-transformers',
    license='MIT',
    author='Ravi RT Merugu',
    author_email='ravi@invanalabs.ai',
    description='A library to transforming JSON with parsers.',
    install_requires=[
        'JSONBender==0.9.3',
        'pymongo',
        'python-slugify'

    ],
)
