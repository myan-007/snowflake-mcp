import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Snowflake connection settings
SNOWFLAKE_CONFIG = {
    'user': os.environ.get('SNOWFLAKE_USER'),
    'password': os.environ.get('SNOWFLAKE_PASSWORD'),
    'account': os.environ.get('SNOWFLAKE_ACCOUNT'),
    'warehouse': os.environ.get('SNOWFLAKE_WAREHOUSE'),
    'database': os.environ.get('SNOWFLAKE_DATABASE'),
    'schema': os.environ.get('SNOWFLAKE_SCHEMA')
}

# Flask settings
FLASK_CONFIG = {
    'port': int(os.environ.get('PORT', 5000)),
    'debug': os.environ.get('FLASK_DEBUG', 'True').lower() in ('true', '1', 't')
}
