FROM python:3.7-buster


WORKDIR /app/src

#RUN apt-get update && apt-get upgrade && apt-get install gcc musl-dev libffi-dev openssl-dev

COPY . .

RUN pip install -r requirements.txt

EXPOSE 80

CMD ["python", "app.py"]