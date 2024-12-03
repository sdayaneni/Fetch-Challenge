from flask import Blueprint, request, jsonify, render_template
from src.models import db, Transaction, Balance, APIKey
from src.auth import require_api_key
import secrets

routes = Blueprint('routes', __name__)

#Display UI
@routes.route('/')
def index():
    return render_template('index.html')

#Endpoint to generate new API keys
@routes.post('/register')
def generate_api_key():
    api_key = secrets.token_hex(32)

    #Store API key in the database
    try:
        new_key = APIKey(key=api_key)
        db.session.add(new_key)
        db.session.commit()

        return jsonify({"message": "API key generated successfully", "api_key": api_key}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    

#Endpoint for adding points
@routes.post('/add')
@require_api_key 
def add_points():
    data = request.get_json()
    
    #Check that all required fields are passed
    required_fields = ["payer", "points", "timestamp"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    payer = data['payer']
    points = data['points']
    timestamp = data['timestamp']

    #Validate input
    if not isinstance(points, int):
        return jsonify({"error": "Points must be an integer"}), 400

    try:
        #Add transaction to the database
        new_transaction = Transaction(payer=payer, points=points, timestamp=timestamp)
        db.session.add(new_transaction)

        #Update/insert balance for the payer
        balance = Balance.query.filter_by(payer=payer).first()
        if balance:
            balance.points += points
        else:
            db.session.add(Balance(payer=payer, points=points))

        db.session.commit()

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Points added successfully"}), 200

#Endpoint for spending points
@routes.post('/spend')
@require_api_key 
def spend_points():
    data = request.get_json()
    
    #Validate input
    if 'points' not in data or not isinstance(data['points'], int) or data['points'] <= 0:
        return jsonify({"error": "Invalid input. 'points' must be a positive integer."}), 400

    points_to_spend = data['points']
    
    #Calculate the total available points
    total_points = db.session.query(db.func.sum(Balance.points)).scalar()
    if total_points is None or total_points < points_to_spend:
        return jsonify({"error": "Not enough points available."}), 400

    #Sort transactions by timestamp
    transactions = Transaction.query.order_by(Transaction.timestamp.asc()).all()

    #List to display in response body
    spent_points = []

    try:
        for transaction in transactions:
            if points_to_spend <= 0:
                break

            payer = transaction.payer
            available_points = transaction.points
            balance = Balance.query.filter_by(payer=payer).first()

            #Check if payer exists in spent_points list
            existing_entry = None
            for i in range (len(spent_points)):
                if spent_points[i]['payer'] == payer:
                    existing_entry = spent_points[i]

            #Check case where points in transaction are negative
            if available_points < 0:
                points_to_spend += abs(available_points)
                balance.points += abs(available_points)

                if existing_entry:
                    existing_entry['points'] += abs(available_points)
                else:
                    spent_points.append({"payer": payer, "points": abs(available_points)})
                
                transaction.points = 0
                continue

            #Deduct points based on transaction
            points_to_deduct = min(points_to_spend, available_points)
            transaction.points -= points_to_deduct
            points_to_spend -= points_to_deduct

            #Update the payer's balance in the balance table
            if balance:
                balance.points -= points_to_deduct

            #Track spent points
            if existing_entry:
                existing_entry['points'] -= points_to_deduct
            else:
                spent_points.append({"payer": payer, "points": -points_to_deduct})


        #Verify that all points are spent
        if points_to_spend > 0:
            return jsonify({"error": "Error during point deduction."}), 500

        #Commit changes to DB
        db.session.commit()

        return jsonify(spent_points), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500




#Endpoint for returning balance
@routes.get('/balance')
@require_api_key
def get_balance():
    try:
        #Query the balances table to get all payers and their points
        balances = Balance.query.all()
        
        #Convert the result into a dictionary and return
        balance_dict = {balance.payer: balance.points for balance in balances}
        return jsonify(balance_dict), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
