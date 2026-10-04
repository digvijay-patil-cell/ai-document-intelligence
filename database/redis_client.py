import redis
import json


# =========================================================
# REDIS CONNECTION
# =========================================================

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)


# =========================================================
# GET CACHED ANSWER
# =========================================================

def get_cached_answer(session_id, question):

    key = f"chat:{session_id}:{question.strip().lower()}"

    cached_data = redis_client.get(key)

    if cached_data:

        return json.loads(cached_data)

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

    redis_client.set(
        key,
        json.dumps(data),
        ex=3600
    )