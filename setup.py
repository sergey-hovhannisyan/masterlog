from setuptools import setup, find_packages

setup(
    name='masterlog',
    version='0.1.4',
    packages=find_packages(),
    author='Sergey Hovhannisyan',
    description='Versatile Python logging package with source management.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license='Apache License 2.0',
    url="https://github.com/sergey-hovhannisyan/masterlog",
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
)