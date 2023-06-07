import environ

env = environ.Env()
environ.Env.read_env()


class Config():
    
    SQLALCHEMY_DATABASE_URI = env("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False