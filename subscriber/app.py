from os import getenv

from .src.subscriber import Subscriber

if __name__ == '__main__':
    subscriber = Subscriber()
    subscriber.connect(
        host=getenv('BROKER_HOST', 'mosquitto'),
        port=int(getenv('BROKER_PORT', 1884))
    )
    subscriber.loop_forever()
