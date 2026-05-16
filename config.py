import os
from dotenv import load_dotenv
from datetime import timedelta


load_dotenv()

database_url = 'postgresql://postgres.lrngcvzjxjyqpwsemucn:Mory09124103725@aws-1-ca-central-1.pooler.supabase.com:5432/postgres'
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

class Config:
    SECRET_KEY = os.environ.get('e84316fb3042f735d227bab6a7dbd0de6c9c383adfc0ed43671aee358cbb32e3','change-this')
    SQLALCHEMY_DATABASE_URI = database_url if database_url else 'sqlite:///temp.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('ed957a1c3677f0bf350747eaa6972593ec9bc230fc0e1bec796ef90341f270a5','jwt-secret')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    SESSION_PERMANENT = True

