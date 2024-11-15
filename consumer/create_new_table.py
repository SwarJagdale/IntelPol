# from google.cloud import bigquery

# # Initialize BigQuery client
# client = bigquery.Client()

# # Define dataset and table IDs
# dataset_id = "bdeminiproject"
# table_id = "master_updated"
# new_table_id = "master"

# # Get the existing table schema
# table_ref = client.dataset(dataset_id).table(table_id)
# table = client.get_table(table_ref)
# schema = table.schema  # Extracts schema of the original table

# # Define the new table reference and create it with the extracted schema
# new_table_ref = client.dataset(dataset_id).table(new_table_id)
# new_table = bigquery.Table(new_table_ref, schema=schema)
# new_table = client.create_table(new_table)  # Creates an empty table

# print(f"Created empty table {new_table_id} with the schema from {table_id}")

# from google.cloud import bigquery
# import pandas as pd
# from datetime import datetime

# # Initialize BigQuery client
# client = bigquery.Client()

# # Define BigQuery table information
# dataset_id = "bdeminiproject"  # Replace with your BigQuery dataset ID
# table_id = "master"            # Replace with your BigQuery table ID

# # Define the path to your local CSV file
# csv_file_path = "/app/clean_crime_data.csv"

# def format_date(date_str):
#     date_formats = [
#         "%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d",
#         "%Y.%m.%d", "%m-%d-%Y", "%d %B %Y", "%B %d, %Y", "%d %b %Y",
#         "%b %d, %Y", "%Y %b %d", "%b %d %Y", "%Y %B %d", "%d-%b-%Y",
#         "%d.%m.%Y", "%d %m %Y"
#     ]
    
#     for fmt in date_formats:
#         try:
#             return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
#         except ValueError:
#             continue
    
#     print(f"Invalid date format: {date_str}")
#     return None

# def format_time(time_str):
#     try:
#         return datetime.strptime(time_str, "%H:%M:%S").strftime("%H:%M:%S")
#     except ValueError:
#         try:
#             return datetime.strptime(time_str, "%I:%M %p").strftime("%H:%M:%S")
#         except ValueError:
#             print(f"Invalid time format: {time_str}")
#             return None

# def process_and_upload_file(filename):
#     try:
#         # Load the CSV into a DataFrame
#         df = pd.read_csv(filename)

#         # Check if the DataFrame is empty
#         if df.empty:
#             print("File is empty or has no readable columns.")
#             return

#         # Format the 'Date Rptd', 'Date Occ', and 'Time Occ' columns
#         df["Date Rptd"] = df["Date Rptd"].apply(lambda x: format_date(x) if pd.notnull(x) else None)
#         df["Date Occ"] = df["Date Occ"].apply(lambda x: format_date(x) if pd.notnull(x) else None)
#         df["Time Occ"] = df["Time Occ"].apply(lambda x: format_time(x) if pd.notnull(x) else None)

#         # Replace NaN values with None to avoid errors in BigQuery
#         df = df.where(pd.notnull(df), None)

#         # Define the destination table
#         table_ref = client.dataset(dataset_id).table(table_id)

#         # Load the DataFrame to BigQuery
#         job = client.load_table_from_dataframe(df, table_ref)

#         # Wait for the load job to complete
#         job.result()

#         print(f"File {filename} uploaded successfully to BigQuery.")

#     except Exception as e:
#         print(f"Error processing file: {e}")

# # Call the function with the specified file
# process_and_upload_file(csv_file_path)
