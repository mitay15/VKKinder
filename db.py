import psycopg2 as pg
from config import host, user, password, db_name

with pg.connect(
        host = host,
        user = user,
        password = password,
        database = db_name
) as conn:
    conn.autocommit = True


def create_table_seen_person():
    with conn.cursor() as cursor:
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS seen_person(
            id serial,
            id_vk varchar(50) PRIMARY KEY);"""
        )


def insert_data_seen_person(id_vk):
    with conn.cursor() as cursor:
        cursor.execute(
            f"""INSERT INTO seen_person (id_vk) 
           VALUES (%s)""",
            (id_vk,)
        )


def check():
    with conn.cursor() as cursor:
        cursor.execute(
            f"""SELECT sp.id_vk
            FROM seen_person AS sp;"""
        )
        return cursor.fetchall()


def delete_table_seen_person():
    with conn.cursor() as cursor:
        cursor.execute(
            """DROP TABLE  IF EXISTS seen_person CASCADE;"""
        )



create_table_seen_person()
print("База данных создана!")