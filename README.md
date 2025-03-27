# Event-management-System
1.Clone the repository:
-git clone
-cd event_management_system-main

2.Create a virtual environment:
-python -m venv venv
-source venv/bin/activate

3.Install dependencies:
-pip install -r requirements.txt

4.Configure environment variables (create a .env file):
DB_HOST=localhost
DB_PORT=3306
DB_USER='user_name'
DB_PASSWORD='user-password'
DB_NAME='DB-Name'

5.Apply database migrations:
-alembic revision --autogenerate -m "Your migration message"
-alembic upgrade head

6.Run the FastAPI application:
uvicorn main:app --reload