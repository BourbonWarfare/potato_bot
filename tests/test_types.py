import uuid

import pytest

from bw.discord.types import ForumId
from bw.missions.types import (
    IterationUuid,
    MissionTypeTag,
    MissionUuid,
    UserUuid,
)
from bw.session.types import (
    DiscordSnowflake,
    OAuthRefreshToken,
    OAuthToken,
    SessionToken,
)


SAMPLE_UUID_STR = '550e8400-e29b-41d4-a716-446655440000'
SAMPLE_UUID = uuid.UUID(SAMPLE_UUID_STR)


# ---- DiscordSnowflake ------------------------------------------------------


def test__discord_snowflake__accepts_str__is_str_instance():
    snowflake = DiscordSnowflake('123456789')
    assert isinstance(snowflake, str)
    assert snowflake == '123456789'


def test__discord_snowflake__accepts_int__casts_to_str():
    snowflake = DiscordSnowflake(123456789)
    assert isinstance(snowflake, str)
    assert snowflake == '123456789'


def test__discord_snowflake__repr__shows_wrapped_value():
    assert repr(DiscordSnowflake('42')) == "DiscordSnowflake('42')"


def test__discord_snowflake__str__returns_underlying_value():
    assert str(DiscordSnowflake(42)) == '42'


def test__discord_snowflake__f_string__interpolates_underlying_value():
    assert f'id={DiscordSnowflake(42)}' == 'id=42'


def test__discord_snowflake__equals_raw_string():
    assert DiscordSnowflake('99') == '99'


def test__discord_snowflake__hashable_as_dict_key():
    table = {DiscordSnowflake('1'): 'one'}
    assert table[DiscordSnowflake('1')] == 'one'
    assert table['1'] == 'one'


# ---- OAuthToken / OAuthRefreshToken / SessionToken -------------------------


@pytest.mark.parametrize('wrapper', [OAuthToken, OAuthRefreshToken, SessionToken])
def test__token_wrappers__accept_str__are_str_instances(wrapper):
    token = wrapper('secret')
    assert isinstance(token, str)
    assert token == 'secret'


@pytest.mark.parametrize(
    'wrapper, expected_prefix',
    [
        (OAuthToken, 'OAuthToken'),
        (OAuthRefreshToken, 'OAuthRefreshToken'),
        (SessionToken, 'SessionToken'),
    ],
)
def test__token_wrappers__repr__shows_class_name(wrapper, expected_prefix):
    assert repr(wrapper('xyz')) == f"{expected_prefix}('xyz')"


def test__oauth_token__bearer_header_f_string():
    assert f'Bearer {OAuthToken("abc")}' == 'Bearer abc'


# ---- ForumId ---------------------------------------------------------------


def test__forum_id__accepts_int__is_int_instance():
    forum = ForumId(7)
    assert isinstance(forum, int)
    assert forum == 7


def test__forum_id__accepts_string_digits__casts_to_int():
    forum = ForumId('42')
    assert isinstance(forum, int)
    assert forum == 42


def test__forum_id__repr__shows_int_value():
    assert repr(ForumId(7)) == 'ForumId(7)'


def test__forum_id__equals_raw_int():
    assert ForumId('100') == 100


def test__forum_id__hashable_as_dict_key():
    table = {ForumId(1): 'one'}
    assert table[ForumId(1)] == 'one'
    assert table[1] == 'one'


# ---- MissionTypeTag --------------------------------------------------------


def test__mission_type_tag__accepts_int_and_string_digits():
    assert MissionTypeTag(5) == 5
    assert MissionTypeTag('5') == 5
    assert isinstance(MissionTypeTag('5'), int)


def test__mission_type_tag__repr__shows_int_value():
    assert repr(MissionTypeTag(3)) == 'MissionTypeTag(3)'


# ---- UUID-based wrappers ---------------------------------------------------

UUID_WRAPPERS = [
    (IterationUuid, 'IterationUuid'),
    (MissionUuid, 'MissionUuid'),
    (UserUuid, 'UserUuid'),
]


@pytest.mark.parametrize('wrapper, _name', UUID_WRAPPERS)
def test__uuid_wrappers__accept_str__are_uuid_instances(wrapper, _name):
    value = wrapper(SAMPLE_UUID_STR)
    assert isinstance(value, uuid.UUID)
    assert str(value) == SAMPLE_UUID_STR


@pytest.mark.parametrize('wrapper, _name', UUID_WRAPPERS)
def test__uuid_wrappers__accept_uuid_instance(wrapper, _name):
    value = wrapper(SAMPLE_UUID)
    assert isinstance(value, uuid.UUID)
    assert str(value) == SAMPLE_UUID_STR
    assert value == SAMPLE_UUID


@pytest.mark.parametrize('wrapper, _name', UUID_WRAPPERS)
def test__uuid_wrappers__accept_bytes(wrapper, _name):
    value = wrapper(SAMPLE_UUID.bytes)
    assert isinstance(value, uuid.UUID)
    assert str(value) == SAMPLE_UUID_STR


@pytest.mark.parametrize('wrapper, _name', UUID_WRAPPERS)
def test__uuid_wrappers__accept_hex_without_dashes(wrapper, _name):
    value = wrapper(SAMPLE_UUID.hex)
    assert str(value) == SAMPLE_UUID_STR


@pytest.mark.parametrize('wrapper, name', UUID_WRAPPERS)
def test__uuid_wrappers__repr__shows_canonical_form(wrapper, name):
    assert repr(wrapper(SAMPLE_UUID_STR)) == f"{name}('{SAMPLE_UUID_STR}')"


@pytest.mark.parametrize('wrapper, _name', UUID_WRAPPERS)
def test__uuid_wrappers__str_round_trips_to_canonical_form(wrapper, _name):
    assert str(wrapper(SAMPLE_UUID_STR)) == SAMPLE_UUID_STR


@pytest.mark.parametrize('wrapper, _name', UUID_WRAPPERS)
def test__uuid_wrappers__equals_raw_uuid(wrapper, _name):
    assert wrapper(SAMPLE_UUID_STR) == SAMPLE_UUID


@pytest.mark.parametrize('wrapper, _name', UUID_WRAPPERS)
def test__uuid_wrappers__cross_input_equivalence(wrapper, _name):
    from_str = wrapper(SAMPLE_UUID_STR)
    from_uuid = wrapper(SAMPLE_UUID)
    from_bytes = wrapper(SAMPLE_UUID.bytes)
    from_hex = wrapper(SAMPLE_UUID.hex)
    assert from_str == from_uuid == from_bytes == from_hex


@pytest.mark.parametrize('wrapper, _name', UUID_WRAPPERS)
def test__uuid_wrappers__hashable_as_dict_key(wrapper, _name):
    table = {wrapper(SAMPLE_UUID_STR): 'value'}
    assert table[wrapper(SAMPLE_UUID_STR)] == 'value'
    assert table[SAMPLE_UUID] == 'value'


def test__uuid_wrappers__different_classes_compare_equal_for_same_value():
    assert MissionUuid(SAMPLE_UUID_STR) == IterationUuid(SAMPLE_UUID_STR)
    assert MissionUuid(SAMPLE_UUID_STR) == UserUuid(SAMPLE_UUID_STR)
