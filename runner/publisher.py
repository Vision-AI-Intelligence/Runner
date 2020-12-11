import redis
import time

HOST = '103.57.220.118'
PORT = '6379'
CHANNEL = 'test'

if __name__ == '__main__':
    r = redis.Redis(host=HOST, port=PORT,
                    password="4t6PN9SJrXcN2ZLR47cnzG93wCLZa2W7")
    pub = r.publish(
        channel=CHANNEL,
        message='HelloWorld!'
    )
