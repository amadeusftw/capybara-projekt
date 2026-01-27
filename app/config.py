import os
from dataclasses import dataclass

@dataclass
class Config:
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "dev-secret-key")
    DEBUG: bool = False
    TESTING: bool = False

@dataclass
class DevelopmentConfig(Config):
    DEBUG: bool = True

@dataclass
class TestingConfig(Config):
    TESTING: bool = True

@dataclass
class ProductionConfig(Config):
    pass

config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}