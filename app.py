from flask import Flask, request
import os
import uuid
import shutil
from werkzeug.utils import secure_filename
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuration for file uploads
app.config['UPLOAD_FOLDER'] = 'images'
app.config['DOWNLOAD_FOLDER'] = 'outputs'
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
    conversion_id = str(uuid.uuid4())
    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], email, conversion_id)
    
    # Create the folder if it doesn't exist
    os.makedirs(folder_path, exist_ok=True)

    # Save each image file to the folder
    for image_file in image_files:
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(folder_path, filename))
        else:
            return "Invalid file format.", 400

    response_data = {
        "msg": f"Files uploaded successfully on Project ID {conversion_id}  Email: {email}",
        "conversion_id": conversion_id
    }
    # Return response_data
    return response_data, 200


@app.route('/convert', methods=['POST'])
def convert():
    email = request.form['email']
    conversion_id = request.form['conversion_id']

    inputs_folder_path = os.path.join(app.config['UPLOAD_FOLDER'], email, conversion_id)
    output_folder_path = os.path.join(app.config['DOWNLOAD_FOLDER'], email, conversion_id)
    
    # Create the folder if it doesn't exist
    os.makedirs(output_folder_path, exist_ok=True)

    # Get a list of files in the inputs folder
    input_files = os.listdir(inputs_folder_path)

    # Copy each file from the inputs folder to the output folder
    for file_name in input_files:
        input_file_path = os.path.join(inputs_folder_path, file_name)
        output_file_path = os.path.join(output_folder_path, file_name)

        shutil.copy(input_file_path, output_file_path)

    response_data = {
        "msg": f"Image converted successfully! Check your email ({email}) for the download link.",
        "conversion_id": conversion_id
    }
    # Return response_data
    return response_data, 200


if __name__ == '__main__':
    app.run(debug=True)








