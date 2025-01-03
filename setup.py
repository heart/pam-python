from setuptools import setup, find_packages

setup(
    name="pam-python",  
    version="0.1.1",    
    author="Narongrit Kanhanoi",
    author_email="narongrit@pams.ai",
    description="Pam Python Library",
    long_description=open("README.md", encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/heart/pam-python",  
    packages=find_packages(), 
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: Other/Proprietary License",  
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: Customer Service",
        "Topic :: Software Development :: Libraries",
    ],
    package_data={
        "pam": ["templates/**/*"], 
    },
    install_requires=[
        "setuptools>=70.0.0",
        "Flask>=3.0.2",
        "aiohttp>=3.11.11",
        "pandas>=2.2.3",
        "Faker>=33.1.0",
        "dask>=2024.12.1",
        "dask-expr>=1.1.21",
        "requests>=2.32.3"
    ],
    entry_points={
        "console_scripts": [
            "pam=pam.cli:main",  
        ],
    },
    python_requires=">=3.8",  
)
