from setuptools import setup, find_packages

setup(
    name='backend',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "python-dotenv",
        "langchain",
        "langchain-openai",
        "psycopg",
        "pydantic"
    ],
    entry_points={
        'console_scripts': [
            'start-backend=app.main:main',
        ],
    },
    package_data={
        '': ['*.env'],
    },
    include_package_data=True,
    zip_safe=False,
    author='Dat Nguyen', 
)