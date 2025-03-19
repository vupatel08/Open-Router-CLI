from setuptools import setup, find_packages

setup(
    name="orchat",
    version="1.0.0",
    author="oop7",
    author_email="oop7_support@proton.me",
    description="A powerful CLI for chatting with AI models through OpenRouter",
    long_description="A powerful CLI for chatting with AI models through OpenRouter.",
    long_description_content_type="text/markdown",
    url="https://github.com/oop7/OrChat",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "requests",
        "tiktoken",
        "rich",
        "python-dotenv", 
        "colorama",
        "packaging",
    ],
    entry_points={
        "console_scripts": [
            "orchat=orchat.main:main",
        ],
    },
)
