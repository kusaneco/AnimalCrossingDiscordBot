import redis
import os

class RedisRepository:

    def __init__(self):
        self.conn = redis.from_url(
            url=os.environ.get('REDIS_URL'),
            decode_responses=True,
        )

    def set(self, key, value):
        self.conn.set(key, value)

    def get(self, key):
        return self.conn.get(key)
