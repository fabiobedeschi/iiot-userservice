FROM eclipse-mosquitto:2.0.8

EXPOSE 1883

WORKDIR /home/root

COPY config/ ./config/ 

CMD [ "mosquitto", "-c", "config/mosquitto.conf" ]