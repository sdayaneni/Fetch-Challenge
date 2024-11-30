#Define python version for the image
FROM python:3.10-slim

#Set the working directory
WORKDIR /app

#Install dependencies from requirements file
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

#Copy the project files
COPY . .

#Expose the port the app runs on
EXPOSE 8000

#Run the application
CMD ["python", "app.py"]