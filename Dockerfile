FROM python:3.11

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip3 install -r requirements.txt

# Copy your application code into the container
COPY . /app

# Specify the entry point for your container
CMD ["python", "main.py"]