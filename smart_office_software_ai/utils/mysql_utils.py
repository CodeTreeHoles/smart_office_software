import mysql.connector

host = 'localhost'
username = "root"
password = "root"
# password = "root"
database = "smart_office_software"



def connect_mysql():
    db = mysql.connector.connect(
        host=host, user=username, password=password, database=database
    )
    return db


if __name__ == '__main__':
    conn = connect_mysql()
    print(conn.cursor())