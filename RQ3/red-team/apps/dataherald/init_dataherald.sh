# RUN AFTER DOCKER COMPOSE UP. ONLY NEEDED IF DBDATA DIRECTORY IS DELETED

port=$1

curl -X POST http://localhost:$port/api/v1/database-connections \
   -H 'Content-Type: application/json' \
   -d '{
    "alias": "postgres",
    "use_ssh": false,
    "connection_uri": "postgresql://postgres:root@pgdb:5432/postgres"
    }'

# get database connection and extract the "id" field
DB_CONNECTION_ID=$(curl -X 'GET' \
"http://localhost:$port/api/v1/database-connections" \
-H 'accept: application/json' | grep \"id\" | cut -d'"' -f4)


# scan customer table
curl -X POST http://localhost:$port/api/v1/table-descriptions/sync-schemas \
   -H 'Content-Type: application/json' \
   -d '{
        "db_connection_id": "'$DB_CONNECTION_ID'",
        "table_names": [
            "users", "job_postings"
        ]
    }'

# curl -X POST http://localhost:$port/api/v1/table-descriptions/sync-schemas \
#    -H 'Content-Type: application/json' \
#    -d '{
#         "db_connection_id": "'$DB_CONNECTION_ID'",
#         "table_names": [
#             "album", "artist", "customer", "employee", "genre", "invoice", "invoice_line", "media_type", "playlist", "playlist_track", "track"
#         ]
#     }'
