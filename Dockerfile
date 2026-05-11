FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Environment variables for database connection
ENV DB_HOST=birthday-app-db
ENV DB_PORT=5432
ENV DB_USER=birthday_user
ENV DB_PASSWORD=birthday_password
ENV DB_NAME=birthday_db

EXPOSE 5000

CMD ["python", "app.py"]
