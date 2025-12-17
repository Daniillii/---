import os
from datetime import datetime

class Config:
    
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:12345@localhost:5432/financial_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = True
    TESTING = False
    
    APP_NAME = 'Система финансового моделирования'
    APP_VERSION = '1.0.0'

class DevelopmentConfig(Config):
    """Конфиг для разработки"""
    DEBUG = True

class ProductionConfig(Config):
    """Конфиг для продакшена"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

class TestingConfig(Config):
    """Конфиг для тестирования"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
