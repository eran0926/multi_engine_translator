import secrets
print(secrets.token_hex())


class BaseConfig:
    SECRET_KEY = secrets.token_hex()


class DevelopmentConfig(BaseConfig):
    pass


class TestingConfig(BaseConfig):
    pass


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
