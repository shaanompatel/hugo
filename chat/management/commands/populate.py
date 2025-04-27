from django.core.management.base import BaseCommand
from django.conf import settings
import sqlite3
import pandas as pd
import numpy as np

class Command(BaseCommand):
    help = "Prints all tables in the SQLite database"

    def handle(self, *args, **kwargs):
        # Path to Django database
        db_path = settings.DATABASES['default']['NAME']


        # Connect to the existing Django SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        #for file in ['sales_orders', 'stock_levels', 'stock_movements', 'suppliers', 'dispatch_parameters', 'material_master', 'material_orders', 'S1_V1_BOM', 'S1_V2_BOM', 'S2_V1_BOM', 'S2_V2_BOM', 'S3_V1_BOM', 'S3_V2_BOM']:
        for file in ['material_orders', 'material_master', 'S1_V1_BOM', 'S1_V2_BOM', 'S2_V1_BOM', 'S2_V2_BOM', 'S3_V1_BOM', 'S3_V2_BOM']:
            df = pd.read_csv(f'./data/{file}.csv')

            # Define table name based on the filename
            table_name = file

            # Prepare the INSERT INTO statement
            cols = df.columns
            # Generate column names string separately, quoting each name
            col_names_str = ', '.join([f'"{c}"' for c in cols])
            placeholders = ', '.join(['?'] * len(cols))
        
            # Corrected insert_sql using the separately generated col_names_str
            insert_sql = f"INSERT INTO \"{table_name}\" ({col_names_str}) VALUES ({placeholders})"
            #print(f"Using INSERT statement structure: {insert_sql}\n")

            # Convert DataFrame rows to list of tuples, replacing NaN with None
            # Convert NaN values in the DataFrame to None for SQL compatibility
            df_sql = df.replace({np.nan: None})
            data_to_insert = [tuple(row) for row in df_sql.itertuples(index=False)]
            print(data_to_insert)

            # Insert data using executemany for efficiency
            cursor.executemany(insert_sql, data_to_insert)

            # Commit the changes
            conn.commit()