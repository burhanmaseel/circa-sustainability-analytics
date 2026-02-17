import psycopg2
import os
from sqlalchemy import create_engine
from urllib.parse import quote_plus

# Retrieve the env variables
db_name = os.getenv('DB_NAME', 'circa')
db_user = os.getenv('DB_USER', 'postgres')
db_pass = os.getenv('DB_PASSWORD', 'root')
db_host = os.getenv('DB_HOST', 'localhost')
db_port = os.getenv('DB_PORT', '5432')

encoded_pass = quote_plus(db_pass)

def get_connection():
    connection = psycopg2.connect(
        database = db_name,
        user = db_user,
        password = db_pass,
        host = db_host,
        port = db_port
    )

    return connection

def get_sqlalchemy_engine():
    connection_string = f"postgresql+psycopg2://{db_user}:{encoded_pass}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(connection_string)

    return engine