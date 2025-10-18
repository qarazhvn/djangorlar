import os
from decouple import Config, RepositoryEnv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE = os.path.join(BASE_DIR, "config", "env", ".env")
config = Config(RepositoryEnv(ENV_FILE))

ENV_POSSIBLE_OPTIONS = ("local", "prod")
ENV_ID = config("ENV_ID", default="local", cast=str)
SECRET_KEY = config("SECRET_KEY", cast=str)
