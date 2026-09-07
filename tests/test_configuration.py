import os

import pytest

from bw.configuration import ConfigType, Configuration
from bw.error import ConfigIsNotEnv, ConfigIsNotKeyValue, ConfigurationKeyNotPresent, DuplicateConfigKey, UnknownConfigFileType


@pytest.fixture
def sample_config():
    return Configuration({'one': '1', 'two': '2'})


@pytest.fixture
def config_file(tmp_path):
    def write(name: str, content: str):
        path = tmp_path / name
        path.write_text(content, encoding='utf-8')
        return path

    return write


def test__configuration__require_single_key_returns_value_not_tuple(sample_config):
    assert sample_config.require('one').get() == '1'


def test__configuration__require_multiple_keys_returns_values_in_requested_order(sample_config):
    assert sample_config.require('two', 'one').get() == ('2', '1')


def test__configuration__require_missing_key_raises(sample_config):
    with pytest.raises(ConfigurationKeyNotPresent):
        sample_config.require('missing')


def test__configuration__load_kv_ignores_comments_and_blank_lines_and_lowercases_keys(config_file):
    path = config_file('conf.kv', '\n# comment\nUPPER = value\nflag\n')

    config = Configuration.load_kv(path)

    assert config['upper'] == 'value'
    assert config['flag'] == ''
    assert config.file == path
    assert config.file_type == ConfigType.KEY_VALUE


def test__configuration__load_kv_duplicate_key_raises(config_file):
    with pytest.raises(DuplicateConfigKey):
        Configuration.load_kv(config_file('conf.kv', 'key=value\nkey=other\n'))


def test__configuration__load_rejects_unknown_suffix(config_file):
    with pytest.raises(UnknownConfigFileType):
        Configuration.load(config_file('conf.txt', 'key=value\n'))


def test__configuration__load_env_rejects_non_env_file(config_file):
    with pytest.raises(ConfigIsNotEnv):
        Configuration.load_env(config_file('conf.txt', 'key=value\n'))


def test__configuration__load_kv_rejects_non_kv_file(config_file):
    with pytest.raises(ConfigIsNotKeyValue):
        Configuration.load_kv(config_file('conf.txt', 'key=value\n'))


def test__configuration__environment_overrides_env_file(config_file, monkeypatch):
    path = config_file('settings.env', 'POTATO=value-from-file\n')
    monkeypatch.setitem(os.environ, 'potato', 'value-from-env')

    config = Configuration.load_env(path)

    assert config['potato'] == 'value-from-env'
