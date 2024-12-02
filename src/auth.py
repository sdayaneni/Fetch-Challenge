from flask import request, jsonify
from functools import wraps
from src.models import APIKey

#Define a decorator to require API key for specific routes
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('Authorization')
        if not api_key:
            return jsonify({"error": "API key is missing"}), 401
        
        #Check that API key exists
        key_record = APIKey.query.filter_by(key=api_key).first()
        if not key_record:
            return jsonify({"error": "Invalid API key"}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function
