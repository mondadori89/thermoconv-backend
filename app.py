from flask import Flask, request
import os
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration for file uploads
app.config['UPLOAD_FOLDER'] = 'images'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'tiff'}

# helper function to check if the file has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def index():
    return 'Suuuup! World'  # A simple route to test if the server is running

@app.route('/upload', methods=['POST'])
def upload():
    email = request.form['email']
    image_files = request.files.getlist('imageFiles')

    # Generate a unique folder name based on the email using UUID
    folder_name = str(uuid.uuid4())
    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], email, folder_name)
    
    # Create the folder if it doesn't exist
    os.makedirs(folder_path, exist_ok=True)

    # Save each image file to the folder
    for image_file in image_files:
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(folder_path, filename))
        else:
            return "Invalid file format.", 400

    # Return a success message
    return f"Email: {email} Files uploaded successfully on folder {folder_name} and are located in {folder_path}.", 200


if __name__ == '__main__':
    app.run(debug=True)








