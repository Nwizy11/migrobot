from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests

app = Flask(__name__)

# Store responses in a dictionary
user_responses = {}

# List of cities with corresponding numbers
city_options = [
    "1) Riyadh",
    "2) Jeddah",
    "3) Mecca",
    "4) Medina",
    "5) Dammam",
    "6) Ta'if",
    "7) Tabuk",
    "8) Buraidah",
    "9) Khamis Mushait",
    "10) Abha",
    "11) Hofuf",
    "12) Al Khobar"
]

# Mapping of user input to city names
city_mapping = {
    "1": "Riyadh",
    "2": "Jeddah",
    "3": "Mecca",
    "4": "Medina",
    "5": "Dammam",
    "6": "Ta'if",
    "7": "Tabuk",
    "8": "Buraidah",
    "9": "Khamis Mushait",
    "10": "Abha",
    "11": "Hofuf",
    "12": "Al Khobar"
}

# List of truck types with corresponding numbers
truck_options = [
    "1) Pick-up Truck",
    "2) Box Truck",
    "3) Flatbed Truck",
    "4) Van",
    "5) Garbage Truck",
    "6) Log Carrier",
    "7) Haul Truck",
    "8) Heavy hauler"
]

# Mapping of user input to truck types
truck_mapping = {
    "1": "Pick-up Truck",
    "2": "Box Truck",
    "3": "Flatbed Truck",
    "4": "Van",
    "5": "Garbage Truck",
    "6": "Log Carrier",
    "7": "Haul Truck",
    "8": "Heavy hauler"
}

# List of questions
questions = [
    "First Name:",
    "Last Name:",
    "Phone:",
    "Truck Type:",
    "Email:",
    "From City:",
    "From Province:",
    "From Neighborhood:",
    "To City:",
    "To Province:",
    "To Neighborhood:",
    "Type of Load:"
]

@app.route('/bot', methods=['POST'])
def webhook():
    incoming_msg = request.values.get('Body', '').lower()
    sender_phone_number = request.values.get('From')

    if incoming_msg == "order truck":
        user_responses[sender_phone_number] = {}  # Initialize responses for a new user
        user_responses[sender_phone_number]['current_question_index'] = 0
        return send_message(sender_phone_number, questions[0])

    if sender_phone_number in user_responses:
        current_index = user_responses[sender_phone_number].get('current_question_index', 0)
        if current_index < len(questions):
            if "City" in questions[current_index]:
                # If the question is about city selection, send the list of city options
                user_responses[sender_phone_number][questions[current_index]] = map_city_or_truck(incoming_msg, city_mapping)
            elif "Truck Type" in questions[current_index]:
                # If the question is about truck type selection, send the list of truck options
                user_responses[sender_phone_number][questions[current_index]] = map_city_or_truck(incoming_msg, truck_mapping)
            else:
                user_responses[sender_phone_number][questions[current_index]] = incoming_msg

            user_responses[sender_phone_number]['current_question_index'] += 1
            next_index = user_responses[sender_phone_number]['current_question_index']

            if next_index < len(questions):
                return send_message(sender_phone_number, questions[next_index] + "\n" + get_options(questions[next_index]))
            else:
                # All questions answered, consume API
                consume_api(user_responses[sender_phone_number], sender_phone_number)
                return send_message(sender_phone_number, "Thank you for providing the information!")
        else:
            return send_message(sender_phone_number, "You've already completed providing the information. "
                                                     "Type 'Order truck' to start a new request.")
    else:
        return send_message(sender_phone_number, "Invalid command. Type 'Order truck' to start a new request.")

def send_message(phone_number, message):
    resp = MessagingResponse()
    resp.message(message)
    return str(resp)

def get_options(question):
    if "From City" in question or "To City" in question:
        return "\n".join(city_options)
    elif "Truck Type" in question:
        return "\n".join(truck_options)
    return ""

def map_city_or_truck(input_number, mapping):
    return mapping.get(input_number, "")

def consume_api(user_data, sender_phone_number):
    # Example: Consume API with user data
    api_url = "https://migro.onrender.com/api/ads/add"
    payload = {
        "id":0,
        "firstName": user_data.get("First Name:", ""),
        "lastName": user_data.get("Last Name:", ""),
        "phone": user_data.get("Phone:", ""),
        "truck_type": user_data.get("Truck Type:", ""),
        "email": user_data.get("Email:", ""),
        "from_city": user_data.get("From City:", ""),
        "from_province": user_data.get("From Province:", ""),
        "from_neighborhood": user_data.get("From Neighborhood:", ""),
        "to_city": user_data.get("To City:", ""),
        "to_province": user_data.get("To Province:", ""),
        "to_neighborhood": user_data.get("To Neighborhood:", ""),
        "type_of_load": user_data.get("Type of Load:", "")
    }
    response = requests.post(api_url, json=payload)
    if response.status_code == 201:
       return send_message(sender_phone_number, "Your request has been successfully processed!")
    else:
       return send_message(sender_phone_number, "There was an error processing your request. Please try again later.")

if __name__ == "__main__":
    app.run(port=4000)


