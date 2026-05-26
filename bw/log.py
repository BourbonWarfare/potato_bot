from bw.settings import GLOBAL_CONFIGURATION
from bw.environment import ENVIRONMENT, Local

import os
from typing import Any

PRODUCTION_LOG_CONFIG = {
    'root': 'INFO',
    'discord': 'INFO',
    'bw': 'INFO',
    'bw.state': 'INFO',
    'bw.potbot': 'INFO',
    'bw.potbot.command': 'INFO',
    'bw.interface': 'INFO',
    'bw.events': 'DEBUG',
}


def config() -> dict[str, Any]:
    if not os.path.exists('./logs'):
        os.makedirs('./logs')
    return {
        'version': 1,
        'formatters': {
            'default': {'format': '[%(asctime)s] [%(module)s] %(levelname)s: %(message)s', 'datefmt': '%Y-%m-%d %H:%M:%S'}
        },
        'handlers': {
            'stdout': {
                'class': 'logging.StreamHandler',
                'formatter': 'default',
                'stream': 'ext://sys.stdout',
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'default',
                'filename': 'logs/bot.log',
                'backupCount': int(GLOBAL_CONFIGURATION.get('log_backup_count', 3)),
                'maxBytes': int(GLOBAL_CONFIGURATION.get('single_log_size', 1 * 1024 * 1024)),
            },
        },
        'root': {
            'level': 'DEBUG' if isinstance(ENVIRONMENT, Local) else PRODUCTION_LOG_CONFIG['root'],
            'handlers': ['stdout', 'file'],
        },
        'loggers': {
            logger: {
                'level': 'DEBUG' if isinstance(ENVIRONMENT, Local) else level,
            }
            for logger, level in PRODUCTION_LOG_CONFIG.items()
        },
    }
