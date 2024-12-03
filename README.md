# Point Transaction API

## Description
This project is a Flask REST API used to keep track of and make transactions with 'points' held by a user. Each point is designated as coming from a certain 'payer' which is additionally stored in transcations.

## Project Structure
- `app.py`: Starting point for the Flask Application.
- `src/auth.py`: Contains Authorization decorator using API tokens.
- `src/routes.py`: Contains logic and implementation for all API endpoints.
- `src/models.py`: Contains the defintition for SQLite database models.
- `src/database.db`: SQLite database file.
- `src/templates/index.html`: Frontend application to make API calls.
- `src/static/styles.css`: Styling for HTML file.

## Installation + Running Project
### To Run Locally:

1. **Install Required Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   
2. **Run Application**:
  ```bash
  python3 app.py
  ```

3. **Access the Application**:
Open a browser and open  `http://localhost:8000` to view information and access endpoints.

### To Run with Docker

1. **Make Docker Image**:
   ```bash
   docker build -t points-api .
   ```
2. **Run Docker Container**:
  ```bash
  docker run -p 8000:8000 points-api
  ```
3. **Access Application**:
Open a browser and open  `http://localhost:8000` to view information and access endpoints.
