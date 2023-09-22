import os
from flask import Flask, render_template, request, redirect, url_for
from stl import mesh
import numpy as np
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Define the directory where uploaded files will be stored temporarily
UPLOAD_FOLDER = '/home/ec2-user/goldweight/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    UPLOAD_FOLDER = 'uploads'

ALLOWED_EXTENSIONS = {'stl'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB

# Densities of gold for different karats (g/cm³)
densities = {
    '9K': 11.0,
    '14K': 13.0,
    '18K': 15.6,
    '21K': 17.0,
    '22K': 17.5
}

def calculate_gold_weight(stl_file_path, karat):
    try:
        stl_mesh = mesh.Mesh.from_file(stl_file_path)
        volume, _, _ = stl_mesh.get_mass_properties()
        density = densities.get(karat, 0.0)  # Get the density for the selected karat
        weight = volume * density / 1000.0  # Convert volume from milligrams to grams
        return weight
    except Exception as e:
        print(f"Error calculating gold weight: {str(e)}")
        return None

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get the uploaded file from the form
        stl_file = request.files["stl_file"]

        # Check if the file extension is allowed
        if stl_file and '.' in stl_file.filename and stl_file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
            # Secure the filename to prevent directory traversal attacks
            filename = secure_filename(stl_file.filename)

            # Save the uploaded STL file to the UPLOAD_FOLDER
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            stl_file.save(file_path)

            # Calculate gold weights for all karat values
            gold_weights = {}
            for karat, density in densities.items():
                weight = calculate_gold_weight(file_path, karat)
                if weight is not None:
                    gold_weights[karat] = weight

            # Delete the file after calculation
            if os.path.exists(file_path):
                os.remove(file_path)

            return render_template("results.html", gold_weights=gold_weights)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)