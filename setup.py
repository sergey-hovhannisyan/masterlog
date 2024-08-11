from setuptools import setup, find_packages

setup(
    name='masterlog',
    version='0.1.1',
    packages=find_packages(),
    install_requires=[
        
    ],
    author='Sergey Hovhannisyan',
    description='Versatile Python logging package with source management.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
)