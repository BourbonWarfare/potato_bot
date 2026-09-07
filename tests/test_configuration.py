import os

import pytest

from bw.configuration import ConfigType, Configuration
from bw.error import ConfigIsNotEnv, ConfigIsNotKeyValue, ConfigurationKeyNotPresent, DuplicateConfigKey, UnknownConfigFileType


def test__configuration__require_single_key_returns_value_not_tuple():
    config = Configuration({'one': '1'})

    assert config.require('one').get() == '1'


def test__configuration__require_multiple_keys_returns_values_in_requested_order():
    config = Configuration({'one': '1', 'two': '2'})

    assert config.require('two', 'one').get() == ('2', '1')


def test__configuration__require_missing_key_raises():
    config = Configuration({})

    with pytest.raises(ConfigurationKeyNotPresent):
        config.require('missing')


def test__configuration__load_kv_ignores_comments_and_blank_lines_and_lowercases_keys(tmp_path):
    config_file = tmp_path / 'conf.kv'
    config_file.write_text('\n# comment\nUPPER = value\nflag\n', encoding='utf-8')

    config = Configuration.load_kv(config_file)

    assert config['upper'] == 'value'
    assert config['flag'] == ''
    assert config.file == config_file
    assert config.file_type == ConfigType.KEY_VALUE


def test__configuration__load_kv_duplicate_key_raises(tmp_path):
    config_file = tmp_path / 'conf.kv'
    config_file.write_text('key=value\nkey=other\n', encoding='utf-8')

    with pytest.raises(DuplicateConfigKey):
        Configuration.load_kv(config_file)


def test__configuration__load_rejects_unknown_suffix(tmp_path):
    config_file = tmp_path / 'conf.txt'
    config_file.write_text('key=value\n', encoding='utf-8')

    with pytest.raises(UnknownConfigFileType):
        Configuration.load(config_file)


def test__configuration__load_env_rejects_non_env_file(tmp_path):
    config_file = tmp_path / 'conf.txt'
    config_file.write_text('key=value\n', encoding='utf-8')

    with pytest.raises(ConfigIsNotEnv):
        Configuration.load_env(config_file)


def test__configuration__load_kv_rejects_non_kv_file(tmp_path):
    config_file = tmp_path / 'conf.txt'
    config_file.write_text('key=value\n', encoding='utf-8')

    with pytest.raises(ConfigIsNotKeyValue):
        Configuration.load_kv(config_file)


def test__configuration__environment_overrides_env_file(tmp_path, monkeypatch):
    config_file = tmp_path / 'settings.env'
    config_file.write_text('POTATO=value-from-file\n', encoding='utf-8')
    monkeypatch.setitem(os.environ, 'potato', 'value-from-env')

    config = Configuration.load_env(config_file)

    assert config['potato'] == 'value-from-env'
