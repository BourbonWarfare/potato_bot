import logging.config

import bw.bot
import bw.log
from bw.bot import PotatoBot
from bw.environment import ENVIRONMENT


def main():
    logging.config.dictConfig(bw.log.config())
    client = PotatoBot.setup()
    client.run(ENVIRONMENT.discord_token())


if __name__ == '__main__':
    main()
