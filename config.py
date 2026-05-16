import os
from dotenv import load_dotenv
from datetime import timedelta


load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('e84316fb3042f735d227bab6a7dbd0de6c9c383adfc0ed43671aee358cbb32e3')
    SQLALCHEMY_DATABASE_URI = os.environ.get('postgresql://postgres.lrngcvzjxjyqpwsemucn:Mory09124103725@aws-0-ca-central-1.pooler.supabase.com:5432/postgres', '').replace('postgres://', 'postgresql://')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('ed957a1c3677f0bf350747eaa6972593ec9bc230fc0e1bec796ef90341f270a5')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    SESSION_PERMANENT = True

