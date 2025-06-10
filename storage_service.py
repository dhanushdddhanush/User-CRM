from azure.data.tables import TableServiceClient
import os

TABLE_NAME = "UserTokens"

connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
table_service = TableServiceClient.from_connection_string(conn_str=connection_string)
table_client = table_service.get_table_client(table_name=TABLE_NAME)

def store_refresh_token(user_id, refresh_token):
    entity = {
        "PartitionKey": "zoho",
        "RowKey": user_id,
        "refresh_token": refresh_token
    }
    table_client.upsert_entity(entity)

def get_refresh_token(user_id):
    try:
        entity = table_client.get_entity(partition_key="zoho", row_key=user_id)
        return entity["refresh_token"]
    except Exception as e:
        print(f"Error retrieving refresh token: {e}")
        return None
