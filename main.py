import bw.log
import logging.config
from bw.environment import ENVIRONMENT
import bw.bot
from bw.bot import PotatoBot


def main():
    logging.config.dictConfig(bw.log.config())
    client = PotatoBot.setup()
    client.run(ENVIRONMENT.discord_token())


if __name__ == '__main__':
    main()
