import json
import logging
import os
import uuid
import azure.functions as func
from azure.data.tables import TableServiceClient

# Initialize Function App (Python v2 model)
app = func.FunctionApp()

# HTTP-triggered function
@app.route(
    route="bookTable",
    methods=["POST"],
    auth_level=func.AuthLevel.ANONYMOUS
)
def book_table(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Book Table API called")

    # Parse JSON body
    try:
        data = req.get_json()
    except Exception:
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON"}),
            status_code=400,
            mimetype="application/json"
        )

    # Extract fields
    name = data.get("name")
    email = data.get("email")
    datetime = data.get("datetime")
    people = data.get("people")
    message = data.get("message", "")

    # Validate required fields
    if not name or not email or not datetime or not people:
        return func.HttpResponse(
            json.dumps({"error": "Missing required fields"}),
            status_code=400,
            mimetype="application/json"
        )

    # Get Azure Storage connection string
    conn_str = os.environ.get("AzureWebJobsStorage")

    if not conn_str:
        return func.HttpResponse(
            json.dumps({"error": "Storage connection string not found"}),
            status_code=500,
            mimetype="application/json"
        )

    try:
        # Connect to Azure Table Storage
        table_service = TableServiceClient.from_connection_string(conn_str)

        # Create table if it does not exist
        table_client = table_service.create_table_if_not_exists("Bookings")

        # Create booking entity
        booking_entity = {
            "PartitionKey": "Booking",
            "RowKey": str(uuid.uuid4()),
            "name": name,
            "email": email,
            "datetime": datetime,
            "people": int(people),
            "message": message
        }

        # Insert into Table Storage
        table_client.create_entity(entity=booking_entity)

    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(
            json.dumps({"error": "Failed to save booking"}),
            status_code=500,
            mimetype="application/json"
        )

    # Success response
    return func.HttpResponse(
        json.dumps({
            "success": True,
            "message": "Table booked successfully"
        }),
        status_code=200,
        mimetype="application/json"
    )
