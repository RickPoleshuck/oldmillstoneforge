import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", '2feef37a19322b1e9030db491614052b842d845226ce3b471d13bd91ea844498')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(basedir, "oldmillstoneforge.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    APP_NAME = "Old Millstone Forge"
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")  # prod default
    MAX_CONTENT_LENGTH = 1024 * 1024 * 1024  # Limits payload/upload size to 1G


class TestConfig(Config):
    TESTING = True
    SECRET_KEY = "test"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    LOG_LEVEL = "DEBUG"
