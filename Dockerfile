FROM python:3.7.7-alpine3.12


WORKDIR /app/src

RUN apk update && apk upgrade && apk add gcc musl-dev libffi-dev openssl-dev

COPY . .

RUN pip install -r requirements.txt

EXPOSE 80

CMD ["python", "app.py"]