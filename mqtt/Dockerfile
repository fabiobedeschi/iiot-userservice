FROM python:3.8

WORKDIR /home/root

COPY . ./

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["python", "-um", "app"]
