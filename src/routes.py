from flask import Blueprint, request, jsonify
from src.models import db, Transaction, Balance

#Create a blueprint for modularity
routes = Blueprint('routes', __name__)

#Endpoint for adding points
@routes.post('/add')
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

    try:
        for transaction in transactions:
            if points_to_spend <= 0:
                break

            payer = transaction.payer
            available_points = transaction.points
            balance = Balance.query.filter_by(payer=payer).first()

            #Check case where points in transaction are negative
            if available_points < 0:
                points_to_spend += abs(available_points)
                balance.points += abs(available_points)
                transaction.points = 0
                continue

            #Deduct points based on transaction
            points_to_deduct = min(points_to_spend, available_points)
            transaction.points -= points_to_deduct
            points_to_spend -= points_to_deduct

            #Update the payer's balance in the balance table
            if balance:
                balance.points -= points_to_deduct

        #Verify that all points are spent
        if points_to_spend > 0:
            return jsonify({"error": "Error during point deduction."}), 500

        #Commit changes to DB
        db.session.commit()

        return jsonify({"message": "Points spent successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500




#Endpoint for returning balance
@routes.get('/balance')
def get_balance():
    try:
        #Query the balances table to get all payers and their points
        balances = Balance.query.all()
        
        #Convert the result into a dictionary and return
        balance_dict = {balance.payer: balance.points for balance in balances}
        return jsonify(balance_dict), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
