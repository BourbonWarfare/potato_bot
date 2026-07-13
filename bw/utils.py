import re
import functools
import asyncio
import random
from typing import Any


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


def levenshtein_distance(a: str, b: str) -> int:
    if len(a) > len(b):
        a, b = b, a

    distances = range(len(a) + 1)
    for b_index, b_char in enumerate(b):
        new_distances = [b_index + 1]
        for a_index, a_char in enumerate(a):
            if a_char == b_char:
                new_distances.append(distances[a_index])
            else:
                new_distances.append(1 + min(distances[a_index], distances[a_index + 1], new_distances[-1]))
        distances = new_distances
    return distances[-1]


def orbat_to_string(orbat: dict[str, Any]) -> str:
    def side_to_string(side: str, groups: list[dict[str, Any]]) -> str:
        if len(groups) == 0:
            return ''

        return f'{side}\n' + '\n'.join(
            [f'{group["name"]}: {id_to_name_map[group["leader"]]} (leading +{len(group["members"]) - 1})' for group in groups]
        )

    all_groups: list[dict] = orbat['groups']

    id_to_name_map = {}
    for group in all_groups:
        for member in group['members']:
            id_to_name_map[member['steam_id']] = member['name']

    blufor_groups = [group for group in all_groups if group['side'] == 'WEST']
    opfor_groups = [group for group in all_groups if group['side'] == 'EAST']
    indfor_groups = [group for group in all_groups if group['side'] == 'GUER']
    civilian_groups = [group for group in all_groups if group['side'] == 'CIV']
    spectator_groups = [group for group in all_groups if group['side'] == 'LOGIC']

    blufor_string = side_to_string('BluFor', blufor_groups)
    opfor_string = side_to_string('OpFor', opfor_groups)
    indfor_string = side_to_string('IndFor', indfor_groups)
    civilian_string = side_to_string('Civilian', civilian_groups)
    spectator_string = f'{sum([len(group["members"]) for group in spectator_groups])} spectators'

    sides = []
    for string in [blufor_string, opfor_string, indfor_string, civilian_string, spectator_string]:
        if string == '':
            continue
        sides.append(string)

    return '\n\n'.join(sides)


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
