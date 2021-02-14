FROM python:3.9.1-alpine

ENV FLASK_APP=ctac.py
WORKDIR /app

COPY . /app
RUN apk add --update --no-cache --virtual .build-deps zlib-dev jpeg-dev gcc musl-dev \
    && pip install -r requirements.txt \
    && apk del .build-deps \
    && apk add libjpeg-turbo \
    && flask db upgrade

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]