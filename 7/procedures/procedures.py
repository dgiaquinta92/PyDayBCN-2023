from paramiko.client import SSHClient, AutoAddPolicy, RSAKey
import sqlite3
import urllib3
urllib3.disable_warnings()
from datetime import datetime

from security import security

def client_shell(ip: str, username: str, password: str, port: int) -> SSHClient:
    #logging.info(f'Connecting to {ip}')
    client = SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy())
    client.connect(ip, port=port, username=username,
                   password=password, timeout=3)
    return client


def get_users():
    conn = sqlite3.connect('api-db.db')
    query = "SELECT * FROM API_USERS "
    cursor = conn.execute(query)
    result = cursor.fetchall()
        # Obtener los nombres de los campos
    field_names = [description[0] for description in cursor.description]

    # Crear una lista de diccionarios, donde cada diccionario representa un registro
    records = [dict(zip(field_names, row)) for row in result]


    return records

def add_user_to_db(user):
    conn = sqlite3.connect('api-db.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS API_USERS
                (ID INTEGER PRIMARY KEY AUTOINCREMENT,
                username     TEXT      NOT NULL,
                full_name    TEXT      NOT NULL,
                email        TEXT      NOT NULL,
                password     TEXT      NOT NULL,
                disabled     BOOLEAN   NOT NULL,
                admin        BOOLEAN   NOT NULL,
                cli          BOOLEAN   NOT NULL,
                role         TEXT      NOT NULL,
                created      TEXT      NOT NULL);''')
    usuario = user.dict()
    query = "SELECT count(username) FROM API_USERS WHERE username = '" + usuario["username"] + "'"
    print(query)
    usuario["created"] = datetime.now()
    usuario["password"] = security.hash_password(usuario["password"])
    result = conn.execute(query).fetchone()[0]
    if result > 0:
        print(result)
        conn.close()
        return False
    else:
        conn.execute("INSERT INTO API_USERS VALUES(NULL, :username, :full_name, :email, :password, :disabled, :admin, :cli, :role, :created)", usuario)
        conn.commit()
        conn.close()
        return "El usuario ha sido creado correctamente"


def delete_api_user(username):
    try:
        conn = sqlite3.connect('config/api-coml.db')
        query1 = "SELECT count(username) FROM API_USERS WHERE username = '" + username + "'"
        result = conn.execute(query1).fetchone()[0]
        if result > 0:
            query = "DELETE FROM API_USERS WHERE username = '" + username + "'"
            conn.execute(query)
            conn.commit()
            conn.close()
            return "El usuario ha sido borrado correctamente"
        else:
            conn.close()
            return False
    except:
        print("Ha ocurrido un error al conectar a la db")
        return False

