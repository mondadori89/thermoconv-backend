from flask import Flask, request
from flask_mail import Mail, Message
import os
import sys
import uuid
import shutil
import zipfile
from werkzeug.utils import secure_filename
from flask_cors import CORS
from converter.converter import convert_jpg_tiff
from dotenv import load_dotenv
import stripe

stripe.api_key = "sk_test_51NWOG7EdrJuCV8vEHlvkZOW4HC01y4zE2fOUFwO56lXcac64tRmbHEbbRoWR3o4atNzB40tUPvZruqol5Fhq1Ms000BqYb8BLF"

load_dotenv()
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
CORS(app)

# Configuration for file uploads
app.config['IMAGES_FOLDER'] = 'images'
app.config['INPUTS_FOLDER'] = 'inputs'
app.config['OUTPUTS_FOLDER'] = 'outputs'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'tiff'}
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587  # Gmail's TLS port
app.config['MAIL_USERNAME'] = 'thermoconv@gmail.com'    # Put on an env file
app.config['MAIL_PASSWORD'] = 'klisyfwmqftyahrz'        # Put on an env file
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

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
    inputs_folder_path = os.path.join(app.config['IMAGES_FOLDER'], email, conversion_id, app.config['INPUTS_FOLDER'])
    
    # Create the folder if it doesn't exist
    os.makedirs(inputs_folder_path, exist_ok=True)

    # Save each image file to the folder
    for image_file in image_files:
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(inputs_folder_path, filename))
        else:
            return "Invalid file format.", 400

    response_data = {
        "msg": f"Files uploaded successfully on Project ID {conversion_id}  Email: {email}",
        "conversion_id": conversion_id
    }
    # Return response_data
    return response_data, 200


@app.route('/create_checkout_session', methods=['POST'])
def create_checkout_session():
    email = request.form['email']
    conversion_id = request.form['conversion_id']

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Image Conversion',
                    },
                    'unit_amount': 1000,  # Replace with your actual price
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='http://localhost:5173/',  # Replace with your success URL
            cancel_url='http://google.com',  # Replace with your cancel URL
        )
        return {'id': session.id}
    except Exception as e:
        return {'error': str(e)}


@app.route('/convert', methods=['POST'])
def convert():
    email = request.form['email']
    conversion_id = request.form['conversion_id']
    session_id = request.form['session_id']  # Get the session ID from the request

    session = stripe.checkout.Session.retrieve(session_id)

    if session.payment_status != 'paid':
        return {'error': 'Payment not successful.'}, 400

    inputs_folder_path = os.path.join(app.config['IMAGES_FOLDER'], email, conversion_id, app.config['INPUTS_FOLDER'])
    output_folder_path = os.path.join(app.config['IMAGES_FOLDER'], email, conversion_id, app.config['OUTPUTS_FOLDER'])
    
    # Create the folder if it doesn't exist
    os.makedirs(output_folder_path, exist_ok=True)

    # Convert images from the input_folder to the output_folder
    convert_jpg_tiff(inputs_folder_path, output_folder_path)

    # Compress the output images into a .zip file
    zip_file_path = os.path.join(app.config['IMAGES_FOLDER'], email, conversion_id, f"{conversion_id}_outputs.zip")
    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
        for root, _, files in os.walk(output_folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, output_folder_path))
        print(f'Files zipped on path: {zip_file_path}')

    # Send the zip file via email
    with app.app_context():
        msg = Message(f'Image Conversion Results ID: {conversion_id}', sender='thermoconv@gmail.com', recipients=[email])
        msg.body = 'Please find the converted images attached.'
        with app.open_resource(zip_file_path) as attachment:
            msg.attach(conversion_id + '_outputs.zip', 'application/zip', attachment.read())
        print(f'Files on ID: {conversion_id} about to be send to {email}')
        mail.send(msg)
        print('Files sent')

    # Data to return
    response_data = {
        "msg": f"Image converted successfully! Check your email ({email}) to download it.",
        "conversion_id": conversion_id
    }
    return response_data, 200

if __name__ == '__main__':
    if os.environ.get('FLASK_ENV') == 'local':
        # Local environment
        app.run(debug=True)
    else:
        # AWS instance or any other environment
        app.run(host='0.0.0.0', port=5000)






