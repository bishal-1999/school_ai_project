from database import connect_to_database
import mysql.connector
import json

####################################################################################################################################

# Function to return the name of all the tables and it's columns 
def fetch_schema(connection, table_name):
    schema = {}
    try:
        cursor = connection.cursor()
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

# Function to return all the tables with it's column in json format
def fetch_full_schema_with_relationships(connection, output_file="schema.json"):
    schema = {}
    try:
        cursor = connection.cursor()

        # Fetch all tables in the database
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        for (table_name,) in tables:
            # Fetch columns for each table
            cursor.execute(f"SHOW COLUMNS FROM {table_name}")
            columns = cursor.fetchall()
            schema[table_name] = {
                "columns": [column[0] for column in columns],
                "relationships": []
            }

            # Fetch foreign key relationships for the table
            cursor.execute(f"""
                SELECT COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                WHERE TABLE_NAME = '{table_name}'
                AND REFERENCED_TABLE_NAME IS NOT NULL
            """)
            relationships = cursor.fetchall()

            # Add relationships to the schema
            for (column_name, referenced_table, referenced_column) in relationships:
                schema[table_name]["relationships"].append({
                    "column": column_name,
                    "referenced_table": referenced_table,
                    "referenced_column": referenced_column
                })

        # Write schema dictionary to a JSON file
        with open(output_file, "w") as file:
            json.dump(schema, file, indent=4)
        print(f"Schema and relationships saved to {output_file}")

    except mysql.connector.Error as e:
        print(f"Error fetching schema and relationships: {e}")
        return None
    finally:
        cursor.close()

####################################################################################################################################

# Function to return specifi tables with it's column in json format
def fetch_table_schema_with_relationships(connection, table_name, output_file="schema.json"):
    schema = {}
    try:
        cursor = connection.cursor()

        # Fetch columns for the specified table
        cursor.execute(f"SHOW COLUMNS FROM {table_name}")
        columns = cursor.fetchall()
        schema[table_name] = {
            "columns": [column[0] for column in columns],
            "relationships": []
        }

        # Fetch foreign key relationships for the specified table
        cursor.execute(f"""
            SELECT COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE TABLE_NAME = '{table_name}'
            AND REFERENCED_TABLE_NAME IS NOT NULL
        """)
        relationships = cursor.fetchall()

        # Add relationships to the schema
        for (column_name, referenced_table, referenced_column) in relationships:
            schema[table_name]["relationships"].append({
                "column": column_name,
                "referenced_table": referenced_table,
                "referenced_column": referenced_column
            })

        # Write schema dictionary to a JSON file
        with open(output_file, "w") as file:
            json.dump(schema, file, indent=4)
        print(f"Schema and relationships for table '{table_name}' saved to {output_file}")

    except mysql.connector.Error as e:
        print(f"Error fetching schema and relationships for table '{table_name}': {e}")
        return None
    finally:
        cursor.close()

####################################################################################################################################

# Function to return specific tables with it's column and it's related tables with it's column in json format
def fetch_table_and_related_schemas_in_json(connection, table_name, output_file="schema_with_related.json"):
    schema = {}

    try:
        cursor = connection.cursor()

        # Function to fetch columns and relationships for a specific table
        def fetch_table_schema(table):
            cursor.execute(f"SHOW COLUMNS FROM {table}")
            columns = cursor.fetchall()
            table_schema = {
                "columns": [column[0] for column in columns],
                "relationships": []
            }

            # Fetch foreign key relationships for the specified table
            cursor.execute(f"""
                SELECT COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                WHERE TABLE_NAME = '{table}'
                AND REFERENCED_TABLE_NAME IS NOT NULL
            """)
            relationships = cursor.fetchall()

            # Add relationships to the table schema
            for (column_name, referenced_table, referenced_column) in relationships:
                table_schema["relationships"].append({
                    "column": column_name,
                    "referenced_table": referenced_table,
                    "referenced_column": referenced_column
                })

            return table_schema

        # Fetch schema for the main table
        schema[table_name] = fetch_table_schema(table_name)

        # Fetch schemas for related tables
        related_tables = {rel["referenced_table"] for rel in schema[table_name]["relationships"]}
        for related_table in related_tables:
            schema[related_table] = fetch_table_schema(related_table)

        # Write schema dictionary to a JSON file
        with open(output_file, "w") as file:
            json.dump(schema, file, indent=4)
        print(f"Schema and relationships for table '{table_name}' and related tables saved to {output_file}")

    except mysql.connector.Error as e:
        print(f"Error fetching schema and relationships for table '{table_name}': {e}")
        return None
    finally:
        cursor.close()

####################################################################################################################################

# Function to return specific tables with it's column and it's related tables with it's column
def fetch_table_and_related_schemas(connection, table_name):
    schema = {}

    try:
        cursor = connection.cursor()

        # Function to fetch columns and relationships for a specific table
        def fetch_table_schema(table):
            cursor.execute(f"SHOW COLUMNS FROM {table}")
            columns = cursor.fetchall()
            table_schema = {
                "columns": [column[0] for column in columns],
                "relationships": []
            }

            # Fetch foreign key relationships for the specified table
            cursor.execute(f"""
                SELECT COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                WHERE TABLE_NAME = '{table}'
                AND REFERENCED_TABLE_NAME IS NOT NULL
            """)
            relationships = cursor.fetchall()

            # Add relationships to the table schema
            for (column_name, referenced_table, referenced_column) in relationships:
                table_schema["relationships"].append({
                    "column": column_name,
                    "referenced_table": referenced_table,
                    "referenced_column": referenced_column
                })

            return table_schema

        # Fetch schema for the main table
        schema[table_name] = fetch_table_schema(table_name)

        # Fetch schemas for related tables
        related_tables = {rel["referenced_table"] for rel in schema[table_name]["relationships"]}
        for related_table in related_tables:
            schema[related_table] = fetch_table_schema(related_table)

        # Return the schema as a normal dictionary
        return schema

    except mysql.connector.Error as e:
        print(f"Error fetching schema and relationships for table '{table_name}': {e}")
        return None
    finally:
        cursor.close()

####################################################################################################################################

# Function to return tables and it's connected tables and column in a formatted way
def format_schema(schema):
    schema_str = ""
    for table_name, table_data in schema.items():
        # Add table name
        schema_str += f"Table: {table_name}\n"
        
        # Add columns
        schema_str += f"Columns: {', '.join(table_data['columns'])}\n"
        
        # Add relationships (if any)
        if table_data["relationships"]:
            for relationship in table_data["relationships"]:
                schema_str += f"  Relationship: Column '{relationship['column']}' -> Referenced Table: {relationship['referenced_table']} -> Referenced Column: {relationship['referenced_column']}\n"
        else:
            schema_str += "  Relationships: No relationships\n"
        
        # Add a newline for separation between tables
        schema_str += "\n"

    return schema_str.strip()

####################################################################################################################################

def extract_table_name(input_text):
    # Split the input by lines
    lines = input_text.split("\n")
    
    # Loop through the lines to find the line starting with "Table Name:"
    for line in lines:
        if line.strip().startswith("Table Name:"):
            # Extract and return the table name
            return line.split("Table Name:")[1].strip()
    
    return "Table name not found"

####################################################################################################################################





















































# tables_details = []
# connection = connect_to_database()
# if connection:
#     for table_name in ['customers','orders']:
#         schema = fetch_table_and_related_schemas(connection, table_name)
#         tables_details.append(schema)

#     # Set to track already processed tables
#     processed_tables = set()
#     formatted_output = ""

#     for schema in tables_details:
#         for table_name, table_data in schema.items():
#             if table_name not in processed_tables:
#                 # Format and append only if the table is not already processed
#                 formatted_output += f"Table: {table_name}\n"
#                 formatted_output += f"Columns: {', '.join(table_data['columns'])}\n"
#                 if table_data['relationships']:
#                     for rel in table_data['relationships']:
#                         formatted_output += f"  Relationship: Column '{rel['column']}' -> Referenced Table: {rel['referenced_table']} -> Referenced Column: {rel['referenced_column']}\n"
#                 else:
#                     formatted_output += "  Relationships: No relationships\n"
#                 formatted_output += "\n"  # Add spacing between tables
#                 processed_tables.add(table_name)  # Mark the table as processed

#     # Print the combined formatted string
#     print(formatted_output.strip())  # Use `strip` to clean up trailing newlines


####################################################################################################################################


# # Function to return specific tables with their columns and related tables with their columns
# def fetch_table_and_related_schemas(connection, table_names):
#     schema = {}

#     try:
#         cursor = connection.cursor()

#         # Function to fetch columns and relationships for a specific table
#         def fetch_table_schema(table):
#             cursor.execute(f"SHOW COLUMNS FROM {table}")
#             columns = cursor.fetchall()
#             table_schema = {
#                 "columns": [column[0] for column in columns],
#                 "relationships": []
#             }

#             # Fetch foreign key relationships for the specified table
#             cursor.execute(f"""
#                 SELECT COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
#                 FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
#                 WHERE TABLE_NAME = '{table}'
#                 AND REFERENCED_TABLE_NAME IS NOT NULL
#             """)
#             relationships = cursor.fetchall()

#             # Add relationships to the table schema
#             for (column_name, referenced_table, referenced_column) in relationships:
#                 table_schema["relationships"].append({
#                     "column": column_name,
#                     "referenced_table": referenced_table,
#                     "referenced_column": referenced_column
#                 })

#             return table_schema

#         # Process each table in the input list
#         processed_tables = set()  # To avoid processing the same table multiple times
#         tables_to_process = table_names[:]  # Start with the input list of tables

#         while tables_to_process:
#             current_table = tables_to_process.pop(0)
            
#             if current_table in processed_tables:
#                 continue  # Skip already processed tables

#             # Fetch schema for the current table
#             schema[current_table] = fetch_table_schema(current_table)
#             processed_tables.add(current_table)

#             # Add related tables to the processing queue
#             related_tables = {rel["referenced_table"] for rel in schema[current_table]["relationships"]}
#             for related_table in related_tables:
#                 if related_table not in processed_tables:
#                     tables_to_process.append(related_table)

#         # Return the schema as a normal dictionary
#         return schema

#     except mysql.connector.Error as e:
#         print(f"Error fetching schema and relationships: {e}")
#         return None
#     finally:
#         cursor.close()


# ####################################################################################################################################

# # Function to return tables and their connected tables and columns in a formatted way
# def format_schema(schema):
#     schema_str = ""
#     for table_name, table_data in schema.items():
#         # Add table name
#         schema_str += f"Table: {table_name}\n"
        
#         # Add columns
#         schema_str += f"Columns: {', '.join(table_data['columns'])}\n"
        
#         # Add relationships (if any)
#         if table_data["relationships"]:
#             for relationship in table_data["relationships"]:
#                 schema_str += f"  Relationship: Column '{relationship['column']}' -> Referenced Table: {relationship['referenced_table']} -> Referenced Column: {relationship['referenced_column']}\n"
#         else:
#             schema_str += "  Relationships: No relationships\n"
        
#         # Add a newline for separation between tables
#         schema_str += "\n"

#     return schema_str.strip()

# ####################################################################################################################################

# # Example usage with multiple tables
# connection = connect_to_database()
# if connection:
#     table_names = ['products','customers']
#     schema = fetch_table_and_related_schemas(connection, table_names)

#     if schema:
#         formatted_schema = format_schema(schema)
#         print('\n', formatted_schema, '\n')

####################################################################################################################################