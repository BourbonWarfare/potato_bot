import pytest

from bw.utils import levenshtein_distance, orbat_diff_to_string, orbat_to_string, recruits_in_orbats, strip_emoji


def member(name: str, steam_id: str, *, is_member: bool = True) -> dict:
    return {'name': name, 'steam_id': steam_id, 'is_member': is_member}


def group(name: str, side: str, leader: str, members: list[dict]) -> dict:
    return {'name': name, 'side': side, 'leader': leader, 'members': members}


def test__strip_emoji__removes_emoji_and_keeps_words():
    assert strip_emoji('📘 Recruit Handbook 😕') == ' Recruit Handbook '


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


def test__orbat_to_string__summarizes_sides_and_spectators():
    orbat = {
        'groups': [
            group('Alpha', 'WEST', '1', [member('Leader', '1'), member('Rifleman', '2')]),
            group('Spectators', 'LOGIC', '3', [member('Spectator', '3')]),
        ]
    }

    assert orbat_to_string(orbat) == '**BluFor**\nAlpha: Leader (_leading 1_)\n\n1 spectators'


def test__orbat_diff_to_string__shows_leader_changes_and_member_delta():
    starting_orbat = {
        'groups': [group('Alpha', 'WEST', '1', [member('Old Lead', '1'), member('Rifleman', '2')])]
    }
    final_orbat = {
        'groups': [group('Alpha', 'WEST', '2', [member('Old Lead', '1'), member('New Lead', '2'), member('Medic', '3')])]
    }

    assert orbat_diff_to_string(starting_orbat, final_orbat) == '**BluFor**\nAlpha: Old Lead -> New Lead (_gained 1, leading 2_)'


def test__recruits_in_orbats__deduplicates_and_sorts_recruits():
    first = {'groups': [group('Alpha', 'WEST', '1', [member('Zulu', '1', is_member=False)])]}
    second = {
        'groups': [
            group('Bravo', 'WEST', '2', [member('Alpha', '2', is_member=False), member('Zulu', '1', is_member=False)])
        ]
    }

    assert recruits_in_orbats(first, second) == ['Alpha', 'Zulu']
