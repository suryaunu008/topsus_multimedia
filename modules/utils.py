import os
import logging
from typing import List

def setup_logger(name: str) -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(name)

def create_directories(paths: List[str]) -> None:
    for path in paths:
        os.makedirs(path, exist_ok=True)

def validate_environment() -> None:
    required_vars = ['PEXELS_API_KEY']
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        raise EnvironmentError(f'Missing required environment variables: {missing}')
