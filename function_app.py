import json
import logging
import os
import uuid
import azure.functions as func
from azure.data.tables import TableServiceClient

app = func.FunctionApp()

@app.route(
    route="bookTable",
    methods=["POST"],
    auth_level=func.AuthLevel.ANONYMOUS
)
def book_table(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Book Table API called")

    try:
        data = req.get_json()
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON"}),
            status_code=400,
            mimetype="application/json"
        )

    name = data.get("name")
    email = data.get("email")
    datetime = data.get("datetime")
    people = data.get("people")
    message = data.get("message", "")

    if not name or not email or not datetime or not people:
        return func.HttpResponse(
            json.dumps({"error": "Missing required fields"}),
            status_code=400,
            mimetype="application/json"
        )

    # ✅ Use default Azure storage variable
    conn_str = os.environ.get("AzureWebJobsStorage")

    if not conn_str:
        return func.HttpResponse(
            json.dumps({"error": "Storage connection string not found"}),
            status_code=500,
            mimetype="application/json"
        )

    table_service = TableServiceClient.from_connection_string(conn_str)
    table_client = table_service.get_table_client("Bookings")

    booking_entity = {
        "PartitionKey": "Booking",
        "RowKey": str(uuid.uuid4()),
        "name": name,
        "email": email,
        "datetime": datetime,
        "people": people,
        "message": message
    }

    table_client.create_entity(entity=booking_entity)

    return func.HttpResponse(
        json.dumps({
            "success": True,
            "message": "Table booked successfully"
        }),
        status_code=200,
        mimetype="application/json"
    )
