from sqlalchemy import create_engine, text
from snowflake.sqlalchemy import URL
from settings import SNOWFLAKE

def _snowflake_engine():
    print("Connecting to Snowflake...")
    url = URL(
        account=SNOWFLAKE["account"],          # e.g. 'xy12345.us-east-2.aws'
        user=SNOWFLAKE["user"],
        password=SNOWFLAKE["password"],
        database=SNOWFLAKE["database"],        # 'WALMART_DB'
        schema=SNOWFLAKE["schema"],            # 'GOLD'
        warehouse=SNOWFLAKE["warehouse"],
        role=SNOWFLAKE.get("role"),
    )
    return create_engine(url)                  # dialect is now registered

ENGINE = _snowflake_engine()
SNOWFLAKE["engine"] = ENGINE  # make available for other modules

def query_df(sql: str, params: dict | None = None):
    # parameterized query (avoids SQL injection)
    with ENGINE.connect() as conn:
        return conn.execute(text(sql), params or {}).mappings().all()  # returns rows of dicts

def read_df(sql: str, params: dict | None = None):
    import pandas as pd
    print("Executing SQL:", sql)
    with ENGINE.connect() as conn:
        return pd.read_sql(text(sql), conn, params=params)


def disconnect_sf_engine():
    ENGINE.connect().close()
    ENGINE.dispose()
    print("Disconnected from Snowflake.")