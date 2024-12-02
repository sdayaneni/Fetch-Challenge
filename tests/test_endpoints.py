import pytest
from src import create_app
from src.models import db, Balance, APIKey
import secrets

@pytest.fixture
def client():
    #Create an app and client for testing
    app = create_app()
    app.config['TESTING'] = True

    with app.test_client() as client:
        with app.app_context():
            #Set up DB
            db.create_all()
            #Generate an API key for testing
            api_key = secrets.token_hex(32)
            new_key = APIKey(key=api_key)
            db.session.add(new_key)
            db.session.commit()

            #Yield the client and API key for use in tests
            yield client, api_key  
            db.session.remove()
            db.drop_all()

#Test basic add endpoint functionality
def test_add_points(client):
    client, api_key = client

    headers = {
        'Authorization': api_key
    }

    response = client.post('/add', json={
        "payer": "DANNON",
        "points": 300,
        "timestamp": "2022-10-31T10:00:00Z"
    }, headers = headers)

    assert response.status_code == 200
    assert response.json["message"] == "Points added successfully"

    #Check the balance in the database
    balance = Balance.query.filter_by(payer="DANNON").first()
    assert balance is not None
    assert balance.points == 300

#Test basic spend endpoint functionality
def test_spend_points(client):
    client, api_key = client

    headers = {
        'Authorization': api_key
    }
    
    client.post('/add', json={"payer": "DANNON", "points": 300, "timestamp": "2022-10-31T10:00:00Z"}, headers = headers)
    client.post('/add', json={"payer": "UNILEVER", "points": 200, "timestamp": "2022-10-31T11:00:00Z"}, headers = headers)
    client.post('/add', json={"payer": "DANNON", "points": -200, "timestamp": "2022-10-31T15:00:00Z"}, headers = headers)
    
    response = client.post('/spend', json={"points": 100}, headers = headers)
    assert response.status_code == 200
    assert response.json["message"] == "Points spent successfully"

    
    #Check balances in the database
    dannon_balance = Balance.query.filter_by(payer="DANNON").first()
    unilever_balance = Balance.query.filter_by(payer="UNILEVER").first()
    assert dannon_balance.points == 0
    assert unilever_balance.points == 200

#Test basic balance endpoint functionality
def test_get_balance(client):
    client, api_key = client

    headers = {
        'Authorization': api_key
    }

    client.post('/add', json={"payer": "DANNON", "points": 300, "timestamp": "2022-10-31T10:00:00Z"}, headers = headers)
    client.post('/add', json={"payer": "UNILEVER", "points": 200, "timestamp": "2022-10-31T11:00:00Z"}, headers = headers)
    
    response = client.get('/balance', headers = headers)
    assert response.status_code == 200
    assert response.json == {
        "DANNON": 300,
        "UNILEVER": 200
    }

#Cumulative test with all 3 endpoints (provided in instructions document)
def test_provided_case(client):
    client, api_key = client

    headers = {
        'Authorization': api_key
    }

    #1. Add Transactions
    transactions = [
        { "payer": "DANNON", "points": 300, "timestamp": "2022-10-31T10:00:00Z" },
        { "payer": "UNILEVER", "points": 200, "timestamp": "2022-10-31T11:00:00Z" },
        { "payer": "DANNON", "points": -200, "timestamp": "2022-10-31T15:00:00Z" },
        { "payer": "MILLER COORS", "points": 10000, "timestamp": "2022-11-01T14:00:00Z" },
        { "payer": "DANNON", "points": 1000, "timestamp": "2022-11-02T14:00:00Z" }
    ]

    for transaction in transactions:
        response = client.post('/add', json=transaction, headers = headers)
        assert response.status_code == 200
        assert response.json["message"] == "Points added successfully"

    #2. Spend
    spend_response = client.post('/spend', json={ "points": 5000 }, headers = headers)
    assert spend_response.status_code == 200
    assert spend_response.json["message"] == "Points spent successfully"

    #3. Check Balances
    balance_response = client.get('/balance', headers = headers)
    assert balance_response.status_code == 200
    assert balance_response.json == {
        "DANNON": 1000,
        "UNILEVER": 0,
        "MILLER COORS": 5300
    }
