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
source ./.venv/bin/activate
python3 app.py
```


## Progress of the project:

- [X] Set up your development backend environment: Python + Flask
- [X] Add simple route to connect with frontend
- [X] Set up the storage system
- [X] Connect the conversion app  
- [X] Compress outputs
- [X] Set up the email sending of results
- [X] Set up domain and point to aws instance IP
  - [X] Buy domain
  - [X] Connect domain
- [o] Set up Stripe, after the payment do the conversion
- [ ] Set up S3 to receive the zip file and get a download link to send on email
- [ ] Set up database for the ids/orders/clients/
- [ ] Set up Stripe and the database connection
- [ ] Set up SSL

## Deploy
On the aws instance, the code is on "thermoconv-backend" folder
```bash
cd thermoconv-backend
git pull origin main                                                          # to get the code updated
docker rm -f <container_id>                                                   # remove old ontainer
docker rmi -f <image_id>                                                      # remove old image
docker build -t thermoconv-backend .                                          # build the new image
docker run --name thermoconv-backend -itd -p 5000:5000 thermoconv-backend     # run the new container
docker logs -f thermoconv-backend                                             # Whatch the logs
```


## Deploy from zero on AWS

1. Setup AWS Instance:
- Launch an EC2 instance on AWS. Make sure to select an appropriate Amazon Machine Image (AMI) based on your needs (e.g., Amazon Linux, Ubuntu, etc.).
- Set up security groups to allow inbound traffic to the necessary ports (e.g., HTTP, HTTPS, etc.).

2. Install Docker:
- Connect to your AWS instance using SSH and install Docker. The specific commands will vary based on your operating system, but for most Linux-based instances, you can use:
```bash
sudo yum update -y  # Update package index
sudo yum install -y docker  # Install Docker
sudo service docker start  # Start Docker service
sudo usermod -aG docker ec2-user  # Add the current user to the docker group (optional but avoids using sudo with docker commands) 
```

3. Backend Dockerization:
- In your backend repository, create a Dockerfile to describe the Docker image for your Flask app.
- Build the Docker image on your local machine:
```bash
docker build -t my_backend_image .
# Push the image to a container registry (e.g., Amazon ECR, Docker Hub, etc.) or use AWS ECR to create a repository and push your image to it.
```

4. Frontend Dockerization:
- In your frontend repository, create a Dockerfile to describe the Docker image for your Frontend app.
- Build the Docker image on your local machine:
```bash
docker build -t my_frontend_image .
# Push the image to a container registry (e.g., Amazon ECR, Docker Hub, etc.) or use AWS ECR to create a repository and push your image to it.
```

5. Docker Compose (optional):
To manage both backend and frontend containers easily, you can use Docker Compose. Create a docker-compose.yml file in your AWS instance to define your services.
Here's a basic example of a docker-compose.yml file:
```yaml
version: '3'
services:
  backend:
    image: my_backend_image
    ports:
      - "5000:5000"
  frontend:
    image: my_frontend_image
    ports:
      - "80:80"
```

Use docker-compose to start the services:
```bash
Copy code
docker-compose up -d
```

6. Nginx as Reverse Proxy (optional):
- To handle incoming requests and route them to the appropriate containers, you can use Nginx as a reverse proxy.
- Install Nginx on your AWS instance:
```bash
sudo yum install -y nginx
```
- Configure Nginx to route requests to your backend and frontend containers. Create configuration files in /etc/nginx/conf.d/ or modify the default configuration in /etc/nginx/nginx.conf.

7. Domain and SSL (optional):
- If you have a domain, point it to your AWS instance's public IP or DNS name.
- Obtain and install an SSL certificate using Let's Encrypt or any other certificate provider for secure communication (HTTPS).

8. Final Steps:
- Make sure your backend Flask app listens on the appropriate IP and port (e.g., 0.0.0.0:5000).
- Make sure your frontend app is configured to use the backend API's URL appropriately (e.g., "http://backend:5000/api" if using Docker Compose).
- Restart Nginx and your containers if necessary.

## Docker network
- To connect the 2 containers in the aws instance
```bash
docker network create docker_network
```



