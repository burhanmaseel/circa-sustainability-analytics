from dotenv import load_dotenv
from db.connection import get_connection

def main():
    load_dotenv()

    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM studer limit 100')

    record = cursor.fetchall()

    if record[0][0] is not None:
        print('DB Connection Successful')

    else:
        print('Connection Failed')

if __name__ == "__main__":
    main()