import re


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
