import os
import sys

from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv
import psycopg2
from sqlalchemy.orm import declarative_base

import models

load_dotenv()


def create_database(admin_credentials: dict):
    db_admin_user = admin_credentials['name_admin']
    db_admin_password = admin_credentials['password_admin']
    db_name = os.environ.get('pgsql_database')
    db_user_app = os.environ.get('pgsql_user')
    db_password_app = os.environ.get('pgsql_password')
    conn = create_connection({
        'db_user': db_admin_user,
        'db_password': db_admin_password,
        'db_name': 'postgres'
    })

    # Check if db exists
    cur = conn.cursor()
    cur.execute(f"SELECT 1 FROM pg_database WHERE datname='{db_name}';")
    db_exists = cur.fetchone()
    cur.close()
    cur = conn.cursor()
    cur.execute(f"SELECT 1 FROM pg_roles WHERE rolname='{db_user_app}';")
    user_exists = cur.fetchone()
    cur.close()
    conn.close()

    if db_exists:
        print(f'База данных {db_name} уже существует')
    else:
        conn = create_connection({
            'db_user': db_admin_user,
            'db_password': db_admin_password,
            'db_name': 'postgres'
        })
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(f"CREATE DATABASE {db_name}")
        conn.autocommit = False
        print(f"База данных '{db_name}' создана")
        cur.close()
        conn.close()

    if user_exists:
        print(f'Пользователь {db_user_app} уже существует')
    else:
        conn = create_connection({
            'db_user': db_admin_user,
            'db_password': db_admin_password,
            'db_name': db_name,
        })
        print(f"CREATE USER {db_user_app} WITH ENCRYPTED PASSWORD '{db_password_app}';")
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(f"CREATE USER {db_user_app} WITH ENCRYPTED PASSWORD '{db_password_app}';")
            cur.execute(f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user_app};")
            cur.execute(f"GRANT ALL PRIVILEGES ON SCHEMA public TO {db_user_app};")
            # Удалить пользователя и базу можно из psql:
            # DROP DATABASE digests;
            # REVOKE ALL ON SCHEMA public FROM digest_content;
            # DROP USER digest_content;
        conn.autocommit = False
        cur.close()
        conn.close()
        print(f"Пользователь '{db_user_app}' создан")


def create_connection(credencials: dict):
    host = os.environ.get('pgsql_host')
    port = os.environ.get('pgsql_port')
    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=credencials['db_name'],
        user=credencials['db_user'],
        password=credencials['db_password']
    )
    return conn


def get_admin_credentials():
    print("""Для создания базы данных и пользователя, прописанных в .env 
    введите имя и пароль пользователя БД PostgreSQL, имеющего привилегиии на создание
    новой базы данных и  пользователей""")
    name_admin = input('Имя пользователя PostgreSQL: ')
    if not name_admin:
        return None
    password_admin = input("Пароль: ")
    if name_admin is None or password_admin is None:
        return None
    return {'name_admin': name_admin, 'password_admin': password_admin}


def create_tables():
    models.Base.metadata.create_all(models.engine)


if __name__ == "__main__":
    admin_user = os.environ.get('pgsql_admin_user')
    admin_password = os.environ.get('pgsql_admin_password')
    if admin_user and admin_password:
        admin = {'name_admin': admin_user, 'password_admin': admin_password}
    else:
        admin = get_admin_credentials()
    if admin is None:
        sys.exit(0)
    create_database(admin)
    create_tables()
