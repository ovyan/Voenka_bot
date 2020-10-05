FROM python:slim-buster

WORKDIR /code

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY Bot/ .

CMD ["python3",  "Bot.py"]