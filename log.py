import os
import logging
import logging.config


LOG_SETTINGS = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'detailed',
            'stream': 'ext://sys.stdout',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'detailed',
            'filename': '/var/log/cdsstack/controller.log',
            'mode': 'a',
            'maxBytes': 20971520,
            'backupCount': 5,
        },

    },
    'formatters': {
        'detailed': {
            'format': '%(asctime)s %(levelname)s %(process)d \
%(name)s.%(lineno)d %(message)s',
        },
        'email': {
            'format': 'Timestamp: %(asctime)s\nModule: %(module)s\n'
            'Line: %(lineno)d\nMessage: %(message)s',
        },
    },
    	'loggers': {
     'controller': {
            'level': 'DEBUG',
            'handlers': ['file', 'console']
            },
    }
}


def setup(path='/var/log/cdsstack'):
    if not os.path.exists(path):
        os.makedirs(path)
    logging.config.dictConfig(LOG_SETTINGS)
    logger = logging.getLogger('controller')
    return logger
