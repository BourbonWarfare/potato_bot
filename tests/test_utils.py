import pytest

from bw.utils import levenshtein_distance, orbat_diff_to_string, orbat_to_string, recruits_in_orbats, strip_emoji


def member(name: str, steam_id: str, *, is_member: bool = True) -> dict:
    return {'name': name, 'steam_id': steam_id, 'is_member': is_member}


def group(name: str, side: str, leader: str, members: list[dict]) -> dict:
    return {'name': name, 'side': side, 'leader': leader, 'members': members}


@pytest.fixture
def simple_orbat():
    return {
        'groups': [
            group('Alpha', 'WEST', '1', [member('Leader', '1'), member('Rifleman', '2')]),
            group('Spectators', 'LOGIC', '3', [member('Spectator', '3')]),
        ]
    }


@pytest.fixture
def leader_change_orbats():
    starting_orbat = {
        'groups': [group('Alpha', 'WEST', '1', [member('Old Lead', '1'), member('Rifleman', '2')])]
    }
    final_orbat = {
        'groups': [group('Alpha', 'WEST', '2', [member('Old Lead', '1'), member('New Lead', '2'), member('Medic', '3')])]
    }
    return starting_orbat, final_orbat


@pytest.fixture
def recruit_orbats():
    first = {'groups': [group('Alpha', 'WEST', '1', [member('Zulu', '1', is_member=False)])]}
    second = {
        'groups': [
            group('Bravo', 'WEST', '2', [member('Alpha', '2', is_member=False), member('Zulu', '1', is_member=False)])
        ]
    }
    return first, second


def test__strip_emoji__removes_emoji():
    value_with_emoji = '📘 Recruit Handbook 😕'

    assert len(strip_emoji(value_with_emoji)) < len(value_with_emoji)


@pytest.mark.parametrize(
    ('left', 'right', 'distance'),
    [
        ('kitten', 'sitting', 3),
        ('same', 'same', 0),
        ('', 'abc', 3),
    ],
)
def test__levenshtein_distance__returns_edit_distance(left, right, distance):
    assert levenshtein_distance(left, right) == distance
    assert levenshtein_distance(right, left) == distance


def test__orbat_to_string__returns_summary_for_non_empty_orbat(simple_orbat):
    assert orbat_to_string(simple_orbat)


def test__orbat_diff_to_string__changes_when_leader_changes(leader_change_orbats):
    starting_orbat, final_orbat = leader_change_orbats
    same_leader_orbat = {
        **final_orbat,
        'groups': [{**final_orbat['groups'][0], 'leader': starting_orbat['groups'][0]['leader']}],
    }

    assert orbat_diff_to_string(starting_orbat, final_orbat) != orbat_diff_to_string(starting_orbat, same_leader_orbat)


def test__recruits_in_orbats__deduplicates_and_sorts_recruits(recruit_orbats):
    assert recruits_in_orbats(*recruit_orbats) == ['Alpha', 'Zulu']
