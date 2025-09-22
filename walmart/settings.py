import os
from dotenv import load_dotenv

load_dotenv()

SNOWFLAKE = {
    "account":   os.getenv("SF_ACCOUNT"),
    "user":      os.getenv("SF_USER"),
    "password":  os.getenv("SF_PASSWORD"),
    "warehouse": os.getenv("SF_WAREHOUSE"),
    "database":  os.getenv("SF_DB", "WALMART_DB"),
    "schema":    os.getenv("SF_SCHEMA",   "GOLD"),
    "role":      os.getenv("SF_ROLE"),
    "output_dir": os.getenv("SF_OUTPUT", "/tmp/snowflake"),
    "engine": None
}