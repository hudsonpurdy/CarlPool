from Datasource import *
from flask import Flask, request, jsonify, session, abort, redirect
import os
import pathlib
from flask_cors import CORS # for communication with frontend
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport.requests import Request
import cachecontrol
import requests

app = Flask(__name__)
CORS(app)
#os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

#Public for sharing/development purposes, actual keys hidden
app.secret_key = "***********" # for google oauth
GOOGLE_CLIENT_ID = "***********.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="https://externship2024backend.vercel.app/callback"
    )

offered_rides = [] 
requested_rides = []

@app.route("/")
def index():
    return "<a href='/login'><button>Login</button></a>"

@app.route('/datatest', methods=['GET'])
def datatest():
    return jsonify({
        'status':"request",
        'name':"hudson",
        'contact':"1234567890",
        'from':"evans",
        'to':"target center",
        'pay':10,
        'seats':2
    })

@app.route('/get_upcoming_rides', methods=['GET'])
def upcoming_requested_rides():
    """this method gets all of the upcoming requested rides from the requested_rides table where the departure times are greater than the current time"""
    try:
        rides = get_upcoming_rides()  # Call the function to get rides
        return jsonify(rides), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/available-rides', methods=['GET'])
def upcoming_available_rides():
    """this method gets all of the upcoming available rides from the available_rides table where the departure times are greater than the current time"""
    try:
        rides = get_available_rides()
        return jsonify(rides), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/add_ride', methods=['POST'])
def add_ride_handler():
    """adds a requested ride to the requested_rides table"""
    data = request.get_json()  # Assuming data is sent as JSON
    print(f"Received data: {data}")
    # Extract data from the JSON request
    request_id = data.get('request_id')
    session_id = data.get('session_id')
    contact_info = data.get('contact_info')
    departure_time = data.get('departure_time')  # Ensure this is in proper datetime format
    departure_location = data.get('departure_location')
    destination = data.get('destination')
    required_seats = data.get('required_seats')
    offer_per_seat = data.get('offer_per_seat')
    
    try:
        # 
        add_requested_ride(request_id, session_id, contact_info, departure_time, departure_location, destination, required_seats, offer_per_seat)
        return jsonify({"status": "success", "message": "Ride added successfully"}), 200
    except Exception as e:
        print(f"Error adding ride: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/add_available_ride', methods=['POST'])
def add_available_ride_route():
    """adds an available ride to the available_rides table"""
    data = request.get_json()  # Assuming data is sent as JSON
    ride_id = data.get('ride_id')
    session_id = data.get('session_id')  # Added session_id
    contact_info = data.get('contact_info')
    departure_time = data.get('departure_time')  # Ensure this is in proper datetime format
    departure_location = data.get('departure_location')
    destination = data.get('destination')
    available_seats = data.get('available_seats')
    cost_per_seat = data.get('cost_per_seat')

    try:
        # Pass session_id to the add_available_ride method
        add_available_ride(ride_id, session_id, contact_info, departure_time, departure_location, destination, available_seats, cost_per_seat)
        return jsonify({"message": "Available ride added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@app.route('/delete_ride', methods=['POST'])
def delete_ride():
    """deletes a row from either available_rides or requested_rides depending on if a request or ride id is received. It then matches this id to a row in the respective table, and if the session id of the user matches the session id in that row, deletes it"""
    data = request.get_json()
    
    ride_id = data.get('ride_id')
    request_id = data.get('request_id') 
    session_id = data.get('session_id')  

    try:
        # Ensure at least one ID (ride_id or request_id) is provided
        if not (ride_id or request_id):
            return jsonify({"error": "Either ride_id or request_id must be provided"}), 400
        
        # Call the helper function to delete the ride based on session_id and provided ID
        delete_specific_ride(ride_id=ride_id, request_id=request_id, session_id=session_id)
        return jsonify({"message": "Ride deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/newrequesttest', methods=['GET'])
def newrequesttest():
    return jsonify({
        'contact':"1234567890",
        'departure_time':"12/18/2024 06:30 PM",
        'departure_location':"evans",
        'destination':"target center",
        'needed_seats':2,
        'offer_per_seat':5
    },{
        'contact':"0987654321",
        'departure_time':"12/20/2024 11:00 AM",
        'departure_location':"burton",
        'destination':"mall of america",
        'needed_seats':4,
        'offer_per_seat':10
    })

@app.route('/newoffertest', methods=['GET'])
def newoffertest():
    return jsonify({
        'contact':"1234567890",
        'departure_time':"12/18/2024 06:30 PM",
        'departure_location':"evans",
        'destination':"target center",
        'available_seats':2,
        'cost_per_seat':5
    },{
        'contact':"0987654321",
        'departure_time':"12/20/2024 11:00 AM",
        'departure_location':"burton",
        'destination':"mall of america",
        'available_seats':4,
        'cost_per_seat':10
    },{
        'contact':"0987654321",
        'departure_time':"12/20/2024 11:00 AM",
        'departure_location':"burton",
        'destination':"mall of america",
        'available_seats':4,
        'cost_per_seat':10
    },{
        'contact':"0987654321",
        'departure_time':"12/20/2024 11:00 AM",
        'departure_location':"burton",
        'destination':"mall of america",
        'available_seats':4,
        'cost_per_seat':10
    },{
        'contact':"0987654321",
        'departure_time':"12/20/2024 11:00 AM",
        'departure_location':"burton",
        'destination':"mall of america",
        'available_seats':4,
        'cost_per_seat':10
    },{
        'contact':"0987654321",
        'departure_time':"12/20/2024 11:00 AM",
        'departure_location':"burton",
        'destination':"mall of america",
        'available_seats':4,
        'cost_per_seat':10
    })

@app.route('/rides/offered', methods=['GET'])
def get_offered_rides():
    return jsonify(offered_rides)

@app.route('/rides/requested', methods=['GET'])
def get_requested_rides():
    return jsonify(requested_rides)

@app.route('/rides/offered', methods=['POST'])
def add_offered_ride():
    data = request.get_json()
    required_fields = ['contact_info', 'departure_time', 'departure_location', 'destination', 'available_seats', 'cost_per_seat']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    offered_ride = {
        "contact_info": data['contact_info'],
        "departure_time": data['departure_time'],
        "departure_location": data['departure_location'],
        "destination": data['destination'],
        "available_seats": data['available_seats'],
        "cost_per_seat": data['cost_per_seat']
    }
    offered_rides.append(offered_ride)
    return jsonify(offered_ride), 201

@app.route('/rides/requested', methods=['POST'])
def add_requested_ride_handler():
    print("Route handler `add_requested_ride_handler` is being executed.")
    data = request.get_json()
    required_fields = ['contact_info', 'departure_time', 'departure_location', 'destination', 'required_seats', 'offer_per_seat']
    if any(field not in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    requested_ride = {
        "contact_info": data['contact_info'],
        "departure_time": data['departure_time'],
        "departure_location": data['departure_location'],
        "destination": data['destination'],
        "required_seats": data['required_seats'],
        "offer_per_seat": data['offer_per_seat'],
    }
    print(f"Adding ride: {requested_ride}")
    requested_rides.append(requested_ride)
    return jsonify(requested_ride), 201

#Google Auth methods below 

def login_required(function):
    def wrapper(*args, **kwargs):
        return abort(401) if "google_id" not in session else function()

    return wrapper

@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)
    if session["state"] != request.args["state"]:
        abort(500) #State doesn't match
    credentials = flow.credentials
    request_session = requests.Session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token = credentials._id_token,
        request = token_request, 
        audience = GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")

    return redirect("/protected_area")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/protected_area")
@login_required
def protected_area():
    return "Protected <a href='/logout'><button>Logout</button></a>"

#if __name__ == '__main__':
#    app.run(debug=True)
