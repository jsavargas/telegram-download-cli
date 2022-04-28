FROM python:3.10.2-alpine

WORKDIR /app


# update apk repo
RUN echo "http://dl-4.alpinelinux.org/alpine/v3.14/main" >> /etc/apk/repositories && \
    echo "http://dl-4.alpinelinux.org/alpine/v3.14/community" >> /etc/apk/repositories




COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY src  .

ENTRYPOINT ["python", "telegram-download-cli.py"]
