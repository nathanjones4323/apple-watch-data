FROM python:3.11

COPY ./requirements.txt /requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

# Specify the entry point for your container
CMD ["python", "main.py"]