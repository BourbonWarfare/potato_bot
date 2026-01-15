import bw.log
import logging
from bw.environment import ENVIRONMENT
from bw.bot import PotatoBot


def main():
    logging.config.dictConfig(bw.log.config())
    client = PotatoBot.setup()
    client.run(ENVIRONMENT.discord_token())


if __name__ == '__main__':
    main()
