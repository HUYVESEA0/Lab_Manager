"""
Utility module for exporting database tables to SQL files.
"""

import argparse
import os

from sqlalchemy import create_engine, inspect, text


def export_table_to_sql(connection_string, table_name, output_file=None):
    """
    Export a specific table's data to a SQL file with INSERT statements

    Args:
        connection_string: Database connection string (e.g., 'sqlite:///app.db')
        table_name: Name of the table to export
        output_file: Output SQL file path (default: table_name.sql)
    """
    if output_file is None:
        output_file = f"{table_name}.sql"

    engine = create_engine(connection_string)
    inspector = inspect(engine)

    # Check if table exists - avoid potential None by checking if inspector is active
    if inspector is None or table_name not in inspector.get_table_names():
        print(f"Table {table_name} does not exist in the database")
        return False

    # Get table data - use transaction context to handle connection properly
    connection = engine.connect()
    try:
        # Get all table data - using text query for better compatibility
        result = connection.execute(text(f"SELECT * FROM {table_name}"))
        rows = result.fetchall()

        # Get column names
        columns = result.keys()

        # Generate INSERT statements
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"-- Export data from {table_name}\n\n")

            # Add delete statement to clear table first
            f.write(f"DELETE FROM {table_name};\n\n")

            # Add insert statements
            for row in rows:
                values = []
                for value in row:
                    if value is None:
                        values.append("NULL")
                    elif isinstance(value, (int, float)):
                        values.append(str(value))
                    else:  # Escape single quotes in string values
                        val_str = str(value).replace("'", "''")
                        values.append(f"'{val_str}'")

                columns_str = ", ".join(columns)
                values_str = ", ".join(values)
                f.write(f"INSERT INTO {table_name} ({columns_str}) VALUES ({values_str});\n")

            f.write("\n-- End of export\n")

        print(f"Successfully exported {len(rows)} rows from {table_name} to {output_file}")
        return True
    finally:
        connection.close()


def export_all_tables(connection_string, output_dir=None):
    """
    Export all tables in the database to separate SQL files

    Args:
        connection_string: Database connection string
        output_dir: Directory to save the SQL files (default: current directory)
    """
    if output_dir is None:
        output_dir = "."

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    engine = create_engine(connection_string)
    inspector = inspect(engine)

    # Make sure inspector is valid before using it
    if inspector is None:
        print("Error: Unable to inspect database schema")
        return False

    table_names = inspector.get_table_names()

    if not table_names:
        print("No tables found in the database")
        return False

    for table in table_names:
        output_file = os.path.join(output_dir, f"{table}.sql")
        export_table_to_sql(connection_string, table, output_file)

    print(f"Exported {len(table_names)} tables to {output_dir}")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export database tables to SQL files")
    parser.add_argument("--connection", "-c", required=True, help="Database connection string")
    parser.add_argument("--table", "-t", help="Table name to export (if not specified, export all tables)")
    parser.add_argument("--output", "-o", help="Output file or directory")

    args = parser.parse_args()

    if args.table:
        export_table_to_sql(args.connection, args.table, args.output)
    else:
        export_all_tables(args.connection, args.output)
