import os

import dotenv
import logging

# needed for local development; Inside docker the .env is loaded anyway.
dotenv.load_dotenv()

# Root logger configuration
level = logging.getLevelName(os.environ.get('LOG_LEVEL', 'DEBUG').upper())

logger = logging.getLogger(__name__)
logger.setLevel(level=level)

stdout = logging.StreamHandler()
stdout.setLevel(level=level)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s')
stdout.setFormatter(formatter)

logger.addHandler(stdout)
