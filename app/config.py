import os
from dotenv import load_dotenv

load_dotenv('.env.example')


class Config:
    POCKETBASE_URL = os.getenv('POCKETBASE_URL', 'http://localhost:8090')
    POCKETBASE_ADMIN_EMAIL = os.getenv('POCKETBASE_ADMIN_EMAIL')
    POCKETBASE_ADMIN_PASSWORD = os.getenv('POCKETBASE_ADMIN_PASSWORD')
