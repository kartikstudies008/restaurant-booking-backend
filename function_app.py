import json
import logging
import azure.functions as func

app = func.FunctionApp()

@app.route(route="bookTable", methods=["POST"])
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

    booking = {
        "name": name,
        "email": email,
        "datetime": datetime,
        "people": people,
        "message": message
    }

    return func.HttpResponse(
        json.dumps({
            "success": True,
            "booking": booking,
            "message": "Table booked successfully"
        }),
        status_code=200,
        mimetype="application/json"
    )
