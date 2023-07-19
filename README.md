# Thermoconv-backend

## Preparing the enviroment on Linux:

First steps:
```bash
sudo apt-get install build-essential
sudo apt update
sudo apt install libimage-exiftool-perl     # Install Exif tools globaly
python3.8 -m venv .venv                     # Create a virtual enviroment
source ./.venv/bin/activate                 # Activate venv
```

With venv activated:
```bash
pip install --upgrade pip                   # Update pip
pip install -r requirements.txt             # Installing dependencies
```

Run:
```bash
python3 app.py
```


## Progress of the project:

- [X] Set up your development backend environment: Python + Flask
- [X] Add simple route to connect with frontend
- [X] Set up the storage system
- [X] Connect the conversion app  
- [X] Compress outputs
- [X] Set up the email sending of results
