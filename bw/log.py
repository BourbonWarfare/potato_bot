from bw.settings import GLOBAL_CONFIGURATION
from bw.environment import ENVIRONMENT, Local

import os
from typing import Any

PRODUCTION_LOG_CONFIG = {
    'root': 'INFO',
    'discord': 'INFO',
    'bw': 'DEBUG',
    'bw.state': 'DEBUG',
    'bw.potbot': 'DEBUG',
    'bw.potbot.command': 'DEBUG',
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
            'discord': {
                'level': 'DEBUG' if isinstance(ENVIRONMENT, Local) else PRODUCTION_LOG_CONFIG['discord'],
                'handlers': ['stdout', 'file'],
            },
            'bw': {
                'level': 'DEBUG' if isinstance(ENVIRONMENT, Local) else PRODUCTION_LOG_CONFIG['bw'],
                'handlers': ['stdout', 'file'],
            },
            'bw.state': {
                'level': 'DEBUG' if isinstance(ENVIRONMENT, Local) else PRODUCTION_LOG_CONFIG['bw.state'],
                'handlers': ['stdout', 'file'],
            },
            'bw.potbot': {
                'level': 'DEBUG' if isinstance(ENVIRONMENT, Local) else PRODUCTION_LOG_CONFIG['bw.potbot'],
                'handlers': ['stdout', 'file'],
            },
            'bw.potbot.command': {
                'level': 'DEBUG' if isinstance(ENVIRONMENT, Local) else PRODUCTION_LOG_CONFIG['bw.potbot.command'],
                'handlers': ['stdout', 'file'],
            },
        },
    }
