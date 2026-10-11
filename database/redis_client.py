import os
import json
import redis

# =========================================================
# REDIS CONNECTION
# =========================================================

redis_url = os.getenv("REDIS_URL")

if redis_url:
    redis_client = redis.Redis.from_url(
        redis_url,
        decode_responses=True,
        socket_connect_timeout=2,
        socket_timeout=2
    )
else:
    redis_client = redis.Redis(
        host="localhost",
        port=6379,
        decode_responses=True,
        socket_connect_timeout=1,
        socket_timeout=1
    )


# =========================================================
# GET CACHED ANSWER
# =========================================================

def get_cached_answer(session_id, question):

    key = f"chat:{session_id}:{question.strip().lower()}"

    try:
        cached_data = redis_client.get(key)

        if cached_data:
            return json.loads(cached_data)

    except (redis.exceptions.RedisError, json.JSONDecodeError) as exc:
        print(f"Redis cache unavailable: {exc}")

    return None


# =========================================================
# SET CACHED ANSWER
# =========================================================

def set_cached_answer(
    session_id,
    question,
    answer,
    sources
):

    key = f"chat:{session_id}:{question.strip().lower()}"

    data = {
        "answer": answer,
        "sources": sources
    }

    try:
        redis_client.set(
            key,
            json.dumps(data),
            ex=3600
        )

    except redis.exceptions.RedisError as exc:
        print(f"Redis cache unavailable: {exc}")