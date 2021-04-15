import sqlite3


def create_table():
    query = "DROP TABLE IF EXISTS login"
    cursor.execute(query)
    conn.commit()

    query = "CREATE TABLE login(username VARCHAR UNIQUE, password VARCHAR)"
    cursor.execute(query)
    conn.commit()


def add_user(username, password):
    query = "INSERT INTO login (username, password) VALUES (?, ?)"
    cursor.execute(query, (username, password))
    conn.commit()


def check_user(username, password):
    query = 'SELECT * FROM login WHERE username = ? AND password = ?'
    cursor.execute(query, (username, password))
    result = cursor.fetchone()
    conn.commit()
    print('[DEBUG][check] result:', result)
    return result


def login():
    answer = input("Login (Y/N): ")

    if answer.lower() == "y":
        username = input("Username: ")
        password = input("Password: ")
        if check_user(username, password):
            print("Username correct!")
            print("Password correct!")
            print("Logging in...")
        else:
            print("Something wrong")


# --- main ---

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

create_table()  # use only once

user = input("New username: ")
key = input("New password: ")

add_user(user, key)

login()

cursor.close()
conn.close()
