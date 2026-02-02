import bw.log
import logging.config
from bw.environment import ENVIRONMENT
from bw.bot import PotatoBot
from bw.state import State


def main():
    logging.config.dictConfig(bw.log.config())
    _state = State()
    client = PotatoBot.setup()
    client.run(ENVIRONMENT.discord_token())


if __name__ == '__main__':
    main()
