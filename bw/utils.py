import itertools
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
    all_groups: list[dict] = orbat['groups']
    id_to_name_map = {}
    for group in all_groups:
        for member in group['members']:
            id_to_name_map[member['steam_id']] = member['name']

    def side_to_string(side: str, groups: list[dict[str, Any]]) -> str:
        if len(groups) == 0:
            return ''

        return f'**{side}**\n' + '\n'.join(
            [
                f'{group["name"]}: {id_to_name_map.get(group["leader"], "Unknown")} (_leading {len(group["members"]) - 1}_)'
                for group in groups
            ]
        )

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


def orbat_diff_to_string(starting_orbat: dict[str, Any], final_orbat: dict[str, Any]) -> str:
    all_members: list[dict[str, Any]] = list(
        itertools.chain(
            *[group['members'] for group in starting_orbat['groups']],
            *[group['members'] for group in final_orbat['groups']],
        )
    )
    id_to_name_map: dict[str, str] = {}
    for member in all_members:
        id_to_name_map[member['steam_id']] = member['name']

    starting_groups: list[dict[str, Any]] = starting_orbat['groups']
    groups_in_start: set[str] = {group['name'] for group in starting_groups}

    final_groups: list[dict[str, Any]] = final_orbat['groups']
    groups_in_final: dict[str, int] = {group['name']: idx for idx, group in enumerate(final_groups)}

    destroyed_groups: list[(dict[str, Any])] = []
    reinforced_groups: list[dict[str, Any]] = []
    existing_groups: list[tuple[dict[str, Any], dict[str, Any]]] = []

    for group in starting_groups:
        group_name: str = group['name']
        if group_name in groups_in_final:
            final_group_idx = groups_in_final[group_name]
            final_group = final_groups[final_group_idx]
            existing_groups.append((group, final_group))
        else:
            destroyed_groups.append(group)

    for group in final_groups:
        group_name: str = group['name']
        if group_name not in groups_in_start:
            reinforced_groups.append(group)

    final_strs: list[str] = []
    for side, name in [('WEST', 'BluFor'), ('EAST', 'OpFor'), ('GUER', 'IndFor'), ('CIV', 'Civilian')]:
        side_existing_groups: list[tuple[dict[str, Any], dict[str, Any]]] = [
            (starting_group, final_group) for starting_group, final_group in existing_groups if starting_group['side'] == side
        ]
        side_reinforced_groups: list[dict[str, Any]] = [group for group in reinforced_groups if group['side'] == side]
        side_destroyed_groups: list[dict[str, Any]] = [group for group in destroyed_groups if group['side'] == side]

        existing_group_strs: list[str] = []
        for starting_group, final_group in side_existing_groups:
            member_delta = len(final_group['members']) - len(starting_group['members'])
            if member_delta < 0:
                delta_str = f'lost {abs(member_delta)}'
            elif member_delta > 0:
                delta_str = f'gained {abs(member_delta)}'
            else:
                delta_str = f'kept {len(starting_group["members"])}'

            existing_group_strs.append(
                f'{starting_group["name"]}: {id_to_name_map.get(final_group["leader"], "Unknown")} '
                f'(_{delta_str}, leading {len(final_group["members"]) - 1}_)'
            )
        existing_group_str = '\n'.join(existing_group_strs)

        reinforced_group_str: str = '\n'.join(
            [
                f'{group["name"]}: {id_to_name_map.get(group["leader"], "Unknown")} (_leading {len(group["members"]) - 1}_)'
                for group in side_reinforced_groups
            ]
        )

        destroyed_group_str: str = '\n'.join(
            [f'{group["name"]}: {len(group["members"])} killed' for group in side_destroyed_groups]
        )

        to_join = []
        if existing_group_str:
            to_join.append(existing_group_str)

        if reinforced_group_str:
            to_join.append('\n_Reinforced_')
            to_join.append(reinforced_group_str)

        if destroyed_group_str:
            to_join.append('\n_Destroyed_')
            to_join.append(destroyed_group_str)

        if to_join:
            final_strs.append(f'**{name}**\n' + '\n'.join(to_join))

    return '\n\n'.join(final_strs)


def recruits_in_orbats(*orbats: dict[str, Any]) -> list[str]:
    seen_recruits: set[str] = set()
    for orbat in orbats:
        all_groups: list[dict] = orbat['groups']
        for group in all_groups:
            for member in group['members']:
                if not member['is_member']:
                    seen_recruits.add(member['name'])

    return sorted(list(seen_recruits))


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
