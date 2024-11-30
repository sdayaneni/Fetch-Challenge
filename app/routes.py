from flask import Blueprint, request, jsonify

#Create a blueprint for modularity
routes = Blueprint('routes', __name__)

#Endpoint for adding points
@routes.post('/add')
def add_points():
    data = request.get_json()
    # To complete
    return jsonify({"message": "Points added successfully"}), 200

#Endpoint for spending points
@routes.post('/spend')
def spend_points():
    data = request.get_json()
    #To complete
    return jsonify([{"payer": "DANNON", "points": -100}]), 200

#Endpoint for returning balance
@routes.get('/balance')
def get_balance():
    #To complete
    return jsonify({"DANNON": 1000, "UNILEVER": 0, "MILLER COORS": 5300}), 200
