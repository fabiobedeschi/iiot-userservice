FROM python:3.8

WORKDIR /home/root

COPY . ./subscriber

RUN pip install --upgrade pip
RUN pip install -r subscriber/requirements.txt

CMD ["python", "-um", "subscriber.app"]
