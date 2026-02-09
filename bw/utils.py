import re
import functools
import asyncio
import random


def backoff(delay=2, retries=3, max_delay=float('inf')):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            current_retry = 0
            current_delay = delay
            while current_retry < retries:
                try:
                    if asyncio.iscoroutinefunction(func):
                        return await func(*args, **kwargs)
                    else:
                        return func(*args, **kwargs)
                except Exception as e:
                    current_retry += 1
                    if current_retry >= retries:
                        raise e
                    await asyncio.sleep(current_delay + random.random() * delay)
                    current_delay *= 2
                    current_delay = min(current_delay, max_delay)

        return wrapper

    return decorator


def strip_emoji(string: str) -> str:
    return re.sub(EMOJI_PATTERN, '', string)


EMOJI_PATTERN = re.compile(
    '['
    '\U0001f600-\U0001f64f'  # emoticons
    '\U0001f300-\U0001f5ff'  # symbols & pictographs
    '\U0001f680-\U0001f6ff'  # transport & map symbols
    '\U0001f1e0-\U0001f1ff'  # flags (iOS)
    '\U00002702-\U000027b0'
    '\U000024c2-\U0001f251'
    ']+',
    re.UNICODE,
)
