from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import secrets
import datetime
import os

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

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template('dashboard.html')
@app.route("/retrieve_job", methods=['POST'])

@login_required
def retrieve_job():
    if request.method == 'POST':
        job_number = request.form.get('job_number')

        # Load data from the job folder
        job_folder = os.path.join(app.config['UPLOAD_FOLDER'], job_number)
        text_fields = []
        pictures = []

        if os.path.exists(job_folder):
            # Read text fields
            text_file_path = os.path.join(job_folder, 'text_fields.txt')
            if os.path.exists(text_file_path):
                with open(text_file_path, 'r') as text_file:
                    text_fields = text_file.readlines()

            # List picture files
            picture_files = os.listdir(job_folder)
            pictures = [f"{job_number}/{filename}" for filename in picture_files]

        return render_template('retrieve_job.html', job_number=job_number, text_fields=text_fields, pictures=pictures)
    return render_template('dashboard.html')

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

      # Save text fields to a text file
      with open(os.path.join(job_folder, 'text_fields.txt'), 'w') as text_file:
            for field_name, field_value in request.form.items():
               text_file.write(f"{field_name}: {field_value}\n")

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
