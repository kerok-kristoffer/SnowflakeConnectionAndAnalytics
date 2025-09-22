#!/usr/bin/env python
import os
import snowflake.connector

from walmart.settings import SNOWFLAKE

ctx = snowflake.connector.connect(
    user='kristofferkero',
    password=SNOWFLAKE['password'],
    account='MBZIHTP-GZ32300',
    warehouse='COMPUTE_WH',
    database='WALMART_DB',
    schema='GOLD',
    session_parameters={
        'QUERY_TAG': 'Test connection from a Python script'
    }
)
cs = ctx.cursor()
try:
    cs.execute("SELECT COUNT(*) FROM WALMART_WEEKLY_REPORTS_FACT;")

    # to load data from a file in local filesystem to snowflake table
        # cs.execute("PUT file:///tmp/data/file* @%test_table")
        # cs.execute("COPY INTO test_table")
    one_row = cs.fetchone()
    print(one_row[0])
finally:
    cs.close()
ctx.close()