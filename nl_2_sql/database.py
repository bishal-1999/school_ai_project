import mysql.connector

####################################################################################################################################

def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='example_school_db'
        )
        if connection.is_connected():
            return connection
    except mysql.connector.Error:
        return None


####################################################################################################################################

def fetch_schema(connection):
    schema = {}
    try:
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        for (table_name,) in tables:
            cursor.execute(f"SHOW COLUMNS FROM {table_name}")
            columns = cursor.fetchall()
            schema[table_name] = [column[0] for column in columns]
        
        return schema
    except mysql.connector.Error as e:
        print(f"Error fetching schema: {e}")
        return None
    finally:
        cursor.close()


####################################################################################################################################

def run_query(connection, query):
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        return results
    except mysql.connector.Error:
        return None
    finally:
        cursor.close()


####################################################################################################################################