from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import secrets
import datetime
import os
import json

app = Flask(__name__, static_url_path='/static', static_folder='static')
app.secret_key = secrets.token_hex(24)

# Define the folder where job data will be saved
UPLOAD_FOLDER = 'job_data'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Create a login manager instance
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# Sample user data (replace with a database)
users = {'12345@gmail.com': {'password': '12345'}}

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    print("inside login")
    if request.method == 'POST':
        email = request.form.get('email')
        pin = request.form.get('pin')
        print(email)
        print(pin)
        if email in users and users[email]['password'] == pin:
            # Authentication successful
            user = User(email)  # Create a User object
            login_user(user)  # Log in the user
            session['user'] = email
            print("authenticated, redirecting to dashboard")
            return redirect(url_for('dashboard'))
        else:
            # Authentication failed, you can add an error message here
            return redirect(url_for('index'))
    return render_template('login.html')  # Render the login form for GET requests

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():
    submitted_jobs = get_submitted_jobs()  # Get a list of submitted job numbers
    retrieved_job = None

    if request.method == 'POST':
        job_number = request.form.get('job_number')

        if job_number:
            retrieved_job = retrieve_job_details(job_number)

    return render_template('dashboard.html', submitted_jobs=submitted_jobs, retrieved_job=retrieved_job)

@app.route("/retrieve_job/<job_number>")
@login_required
def retrieve_job(job_number):
    job_details = retrieve_job_details(job_number)

    return render_template('dashboard.html', job_details=job_details)

def get_submitted_jobs():
    # Implement this function to get a list of submitted job numbers for the current user
    # You can retrieve it from a database or any other data source
    # For this example, let's return a static list of job numbers
    return ['job123', 'job456', 'job789']

def retrieve_job_details(job_number):
    # Implement this function to retrieve job details based on the job number
    # You can load the details from a database or other data source
    # For this example, let's return a dictionary with sample job details
    job_details = {
        'job_number': job_number,
        'client_id': 'Client123',
        'description': 'Sample job description',
        'status': 'In Progress',
        # Add more job details as needed
    }
    return job_details

def generate_unique_job_number(client_id):
    # Generate a unique job number based on client ID, date, and timestamp
    current_datetime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    job_number = f"{client_id}_{current_datetime}"
    return job_number

def get_client_id():
    # Implement this function to get the client's ID
    # You can retrieve it from the user's session or other means
    # For example, you might store it in the session during login
    return session.get('user_id')  # Update this ac

@app.route("/submit_job", methods=['POST'])
@login_required
def submit_job():
    if request.method == 'POST':
        # Generate a unique job number based on client ID, date, and timestamp
        client_id = get_client_id()  # Implement this function to get the client's ID
        job_number = generate_unique_job_number(client_id)

        # Create a folder for the job data
        job_folder = os.path.join(app.config['UPLOAD_FOLDER'], job_number)
        os.makedirs(job_folder)

        # Store text fields in a dictionary to maintain order
        text_fields = {}

        # Save text fields to a JSON file
        text_fields_json_path = os.path.join(job_folder, 'text_fields.json')
        for field_name, field_value in request.form.items():
            text_fields[field_name] = field_value

        with open(text_fields_json_path, 'w') as json_file:
            json.dump(text_fields, json_file, indent=4)

        # Save uploaded pictures to the job folder
        for uploaded_file in request.files.getlist('pictures'):
            if uploaded_file.filename != '':
                picture_path = os.path.join(job_folder, uploaded_file.filename)
                uploaded_file.save(picture_path)

        flash(f"Job submitted successfully. Job number: {job_number}", 'success')
        return redirect(url_for('dashboard'))

    return render_template('dashboard.html')
if __name__ == "__main__":
    app.run(debug=True)
