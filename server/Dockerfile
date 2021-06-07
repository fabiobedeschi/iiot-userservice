FROM python:3.8

EXPOSE 80

WORKDIR /home/root

COPY . ./server

RUN pip install --upgrade pip
RUN pip install -r server/requirements.txt

CMD ["python", "-um", "server.app"]
