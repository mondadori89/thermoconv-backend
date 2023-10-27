from flask import Flask, request
from flask_mail import Mail, Message
import os
import sys
import time
import uuid
import shutil
import zipfile
from werkzeug.utils import secure_filename
from flask_cors import CORS
from converter.converter import convert_jpg_tiff
from dotenv import load_dotenv
import stripe
import boto3

app = Flask(__name__)
CORS(app)

# ENV variables:
load_dotenv()
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
flask_env = os.environ.get('FLASK_ENV')
aws_access_key = os.environ.get('AWS_ACCESS_KEY')
aws_secret_key = os.environ.get('AWS_SECRET_KEY')
stripe_api_key_dev = os.environ.get('STRIPE_API_KEY_DEV')
s3_bucket = os.environ.get('S3_BUCKET')

# S3 set-up
s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name='us-west-2')

# Stripe set-up
stripe.api_key = stripe_api_key_dev

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
    conversion_id = request.form['conversion_id']
    image_file = request.files['imageFile']

    # Generate a unique folder name based on the email using UUID
    inputs_folder_path = os.path.join(app.config['IMAGES_FOLDER'], email, conversion_id, app.config['INPUTS_FOLDER'])

    # Save each image file to the folder
    print(f'Uploading file to S3: Email: {email} - ProjectID: {conversion_id} - Image: {image_file}')
    if image_file and allowed_file(image_file.filename):
        filename = secure_filename(image_file.filename)
        s3.upload_fileobj(image_file, s3_bucket, os.path.join(inputs_folder_path, filename))
    else:
        return "Invalid file format.", 400

    response_data = {
        "msg": f"Files uploaded successfully on Project ID {conversion_id}  Email: {email}",
    }
    # Return response_data
    return response_data, 200


@app.route('/create_checkout_session', methods=['POST'])
def create_checkout_session():
    email = request.form['email']
    conversion_id = request.form['conversion_id']

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types = ['card'],
            line_items = [{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Image Conversion',
                    },
                    'unit_amount': 1000,  # Replace with your actual price
                },
                'quantity': 1,
            }],
            customer_email = email,
            metadata = { "conversion_id": conversion_id },
            mode = 'payment',
            success_url = 'http://localhost:5173/convert?session_id={CHECKOUT_SESSION_ID}',  # Replace with your success URL
            cancel_url = 'http://localhost:5173/',  # Replace with your cancel URL
        )

        response_data = {
            "msg": f"checkout session generated.",
            "session_url": checkout_session.url
        }

        return response_data, 200
    
    except Exception as e:
        return {'error': str(e)}


@app.route('/check_stripe_session_info', methods=['POST'])
def check_stripe_session_info():
    session_id = request.form['session_id']   

    try:
        stripe_session = stripe.checkout.Session.retrieve(session_id)

        response_data = {
            "msg": f"session info fetched.",
            "stripe_session": stripe_session
        }

        return response_data, 200  
    
    except Exception as e:
        return {'error': str(e)}


@app.route('/convert', methods=['POST'])
def convert():
    email = request.form['email']
    conversion_id = request.form['conversion_id']
    # session_id = request.form['session_id']  # Get the session ID from the request

    # session = stripe.checkout.Session.retrieve(session_id)

    # if session.payment_status != 'paid':
    #     return {'error': 'Payment not successful.'}, 400

    inputs_folder_path = os.path.join(app.config['IMAGES_FOLDER'], email, conversion_id, app.config['INPUTS_FOLDER'])
    output_folder_path = os.path.join(app.config['IMAGES_FOLDER'], email, conversion_id, app.config['OUTPUTS_FOLDER'])
    
    # Create the folders if it doesn't exist
    os.makedirs(inputs_folder_path, exist_ok=True)
    os.makedirs(output_folder_path, exist_ok=True)

    # Download input images from S3
    input_files_list = s3.list_objects(Bucket=s3_bucket, Prefix=inputs_folder_path)

    if 'Contents' not in input_files_list:
        return "No files found for the provided email and conversion_id.", 404
    
    for obj in input_files_list['Contents']:
        file_name = obj['Key'].split('/')[-1]
        file_path = os.path.join(inputs_folder_path, file_name)
        
        # Skip if directory (S3 'folders' or empty files are listed as keys with size 0)
        if obj['Size'] == 0:
            continue
        
        s3.download_file(s3_bucket, obj['Key'], file_path)

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

    # Upload zipfile to S3
    print(f'\n Uploading Zip file to S3: Email: {email} - ProjectID: {conversion_id} - Zipfile: {zip_file_path}')
    zip_s3_path = os.path.join(zip_file_path)
    s3.upload_file(zip_file_path, s3_bucket, zip_s3_path)  
    
    zipfile_url = f"https://{s3_bucket}.s3.amazonaws.com/{zip_s3_path}"
    print(f'\n Zip file S3 download url: {zipfile_url}')
    
    # Send the zip file via email
    with app.app_context():
        msg = Message(f'Image Conversion Results ID: {conversion_id}', sender='thermoconv@gmail.com', recipients=[email])
        msg.body = f'Please find the converted images in the link below: \n Download Link: {zipfile_url}'
        print(f'Files on ID: {conversion_id} about to be send to {email}')
        mail.send(msg)
        print('Files sent')

    # Delete input and outputs from server
    folder_to_delete_path = os.path.join(app.config['IMAGES_FOLDER'], email, conversion_id)
    shutil.rmtree(folder_to_delete_path)

    # Data to return
    response_data = {
        "msg": f"Image converted successfully! Check your email ({email}) to download it.",
        "conversion_id": conversion_id
    }
    return response_data, 200


if __name__ == '__main__':
    if flask_env == 'local':
        # Local environment
        app.run(debug=True)
    else:
        # AWS instance or any other environment
        app.run(host='0.0.0.0', port=5000)






