import os
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from ultralytics import YOLO
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads/'
OUTPUT_FOLDER = 'static/outputs/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

model = YOLO('best.pt')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

users = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/predict')
def predict():
    return render_template('predict.html')

@app.route('/summary')
def summary():
    return render_template('summary.html')

@app.route('/upload', methods=['POST'])
def upload():
    uploaded_files = request.files.getlist('images')
    processed_images = []

    for file in uploaded_files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)

            results = model(filepath)
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], unique_filename)
            results[0].save(filename=output_path)

            processed_images.append({
                'original': filepath,
                'processed': output_path
            })

    return render_template('predict.html', images=processed_images)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = users.get(email)
        if user and user['password'] == password:
            return render_template('home.html', message='Login successful!')
        return render_template('log.html', error='Invalid credentials')
    return render_template('log.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        if email in users:
            return render_template('signup.html', error='Email already registered')
        users[email] = {'name': name, 'password': password}
        return render_template('login.html', message='Signup successful, please log in!')
    return render_template('signup.html')

if __name__ == '__main__':
    app.run(debug=True)
