from pathlib import Path


def test__channel_webhook_creation__only_happens_in_temporary_webhook_manager():
    offenders = []
    for path in Path('bw').rglob('*.py'):
        if path == Path('bw/commands/webhooks.py'):
            continue
        if '.create_webhook(' in path.read_text(encoding='utf-8'):
            offenders.append(str(path))

    assert offenders == []
