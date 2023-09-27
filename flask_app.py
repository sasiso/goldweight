import os
from flask import Flask, render_template, request, redirect, url_for
from stl import mesh
import numpy as np
from werkzeug.utils import secure_filename

app = Flask(__name__, static_url_path='/static', static_folder='static')

@app.route("/")
def index():
   return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)