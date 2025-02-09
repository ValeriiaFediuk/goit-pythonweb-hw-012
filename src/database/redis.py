import redis.asyncio as redis

# Підключення до Redis
redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)