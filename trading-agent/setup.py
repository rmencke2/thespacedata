"""
Setup file for trading-agent package
"""
from setuptools import setup, find_packages

setup(
    name="trading-agent",
    version="1.0.0",
    description="LangGraph Multi-Agent Stock Trading System",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        'langgraph>=0.2.45',
        'langchain>=0.3.7',
        'langchain-openai>=0.2.8',
        'alpaca-py>=0.28.3',
        'yfinance>=0.2.49',
        'pandas>=2.2.3',
        'numpy>=1.26.4',
        'ta>=0.11.0',
        'sqlalchemy>=2.0.36',
        'python-dotenv>=1.0.1',
        'schedule>=1.2.2',
        'requests>=2.32.3',
        'pytz>=2024.2',
    ],
    python_requires='>=3.8',
)
