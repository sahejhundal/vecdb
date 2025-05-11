from setuptools import setup, find_packages

setup(
    name="vectordb-sdk",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "pydantic",
        "fastapi",
        "numpy",
        "cohere",
        "python-dotenv",
        "requests"
    ],
)