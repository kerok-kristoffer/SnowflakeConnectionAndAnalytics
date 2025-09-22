# run_reports.py
import pandas as pd

from db import read_df, disconnect_sf_engine
from transforms import add_year_week_month, bin_store_size
from charts import (
    weekly_sales_by_store_and_holiday,
    weekly_sales_vs_temperature_by_year,
    weekly_sales_by_store_size,
    save_plotly,
    monthly_sales_by_store_type,
    yearly_markdown_sales_by_store,
    sales_by_store_type,
    sales_by_store_and_type,
    sales_by_store_and_type_facet,
    fuel_price_by_year,
    fuel_price_by_month,
    sales_by_time,
    sales_by_cpi,
    sales_by_dept
)
from walmart.settings import SNOWFLAKE

# 1) Weekly sales by store & holiday
sql_sales_holiday = """
SELECT
  f.store_id,
  d.is_holiday,
  f.store_weekly_sales
FROM WALMART_DB.GOLD.WALMART_WEEKLY_REPORTS_FACT f
JOIN WALMART_DB.GOLD.WALMART_DATE_DIM d
  ON d.date_id = f.date_id
WHERE d."REPORT_DATE" BETWEEN :start_date AND :end_date
"""
print("Generating reports...")
print("1) Weekly sales by store & holiday")
df1 = read_df(sql_sales_holiday, {"start_date":"2012-01-01", "end_date":"2012-12-31"})
fig1 = weekly_sales_by_store_and_holiday(df1)
save_plotly(fig1, "weekly_sales_by_store_and_holiday_2012", SNOWFLAKE["output_dir"])
print("done.")

# 2) Weekly sales vs temperature by year
sql_sales_temp = """
SELECT
  d."REPORT_DATE"            AS report_date,
  f.store_weekly_sales,
  f.store_temperature
FROM WALMART_DB.GOLD.WALMART_WEEKLY_REPORTS_FACT f
JOIN WALMART_DB.GOLD.WALMART_DATE_DIM d
  ON d.date_id = f.date_id
WHERE d."REPORT_DATE" BETWEEN :start_date AND :end_date
  AND f.store_weekly_sales IS NOT NULL
  AND f.store_temperature  IS NOT NULL
"""
print("2) Weekly sales vs temperature by year")
df2 = read_df(sql_sales_temp, {"start_date":"2011-01-01", "end_date":"2012-12-31"})
df2 = add_year_week_month(df2, date_col="report_date")
fig2 = weekly_sales_vs_temperature_by_year(df2)
save_plotly(fig2, "weekly_sales_vs_temperature_by_year_2011_2012", SNOWFLAKE["output_dir"])
print("done.")

# 3) Weekly sales by store size (binned)
sql_sales_size = """
SELECT
  SUM(f.store_weekly_sales) AS total_weekly_sales,
  s.store_size
FROM WALMART_DB.GOLD.WALMART_WEEKLY_REPORTS_FACT f
JOIN WALMART_DB.GOLD.WALMART_STORE_DIM s
  ON s.store_id = f.store_id
WHERE f.store_weekly_sales IS NOT NULL
  AND s.store_size IS NOT NULL
GROUP BY s.store_size
"""
print("3) Weekly sales by store size")
df3 = read_df(sql_sales_size, {"start_date":"2011-01-01", "end_date":"2012-12-31"})
print("store_size min:", df3["store_size"].min())
print("store_size max:", df3["store_size"].max())
# df3 = bin_store_size(df3, col="store_size")
# print(df3["store_size_bin"].value_counts(dropna=False))
# print(df3.head())
df3.sort_values("store_size", ascending=True, inplace=True)

fig3 = weekly_sales_by_store_size(df3)
save_plotly(fig3, "weekly_sales_by_store_size", SNOWFLAKE["output_dir"])
print("done.")


# 4 <Monthly> sales by store type and month
sql_sales_type = """
    SELECT SUM(f.store_weekly_sales) AS total_weekly_sales,
            s.store_type,
            d.report_date
    FROM WALMART_WEEKLY_REPORTS_FACT f
    JOIN WALMART_STORE_DIM s
        ON s.store_id = f.store_id
    JOIN WALMART_DATE_DIM d
        ON d.date_id = f.date_id
    GROUP BY s.store_type, d.report_date
    ORDER BY s.store_type, d.report_date
"""
df4 = read_df(sql_sales_type)
df4 = add_year_week_month(df4, date_col="report_date")

df4 = df4.groupby(["store_type", "month"], as_index=False).agg(
    total_monthly_sales=("total_weekly_sales", "sum")
)

fig4 = monthly_sales_by_store_type(df4)
save_plotly(fig4, "monthly_sales_by_store_type", SNOWFLAKE["output_dir"])
print("done.")

# 5 markdown sales by year

sql_markdown_sales = """
    WITH src AS (
        SELECT YEAR(d.report_date) AS year,
        f.markdown1,
        f.markdown2,
        f.markdown3,
        f.markdown4,
        f.markdown5,
        f.store_id AS store_id
        FROM WALMART_WEEKLY_REPORTS_FACT f
        JOIN WALMART_DATE_DIM d
            ON f.date_id = d.date_id
    )

    SELECT year,
    markdown_type,
    SUM(markdown_sum) AS total_markdown_amount,
    store_id
    FROM src
    UNPIVOT (
        markdown_sum FOR markdown_type IN (markdown1, markdown2, markdown3, markdown4, markdown5)
    )
    GROUP BY store_id, markdown_type, year
    ORDER BY store_id, year, markdown_type
"""

df5 = read_df(sql_markdown_sales)
fig5 = yearly_markdown_sales_by_store(df5)


save_plotly(fig5, "sql_markdown_sales", SNOWFLAKE["output_dir"])
print("done.")


# # 6 weekly sales by store type
sql_sales_store_type = """
    SELECT  s.store_type, s.store_id,
            SUM(f.STORE_WEEKLY_SALES) AS total_weekly_sales
    FROM WALMART_DB.GOLD.WALMART_WEEKLY_REPORTS_FACT f
    JOIN WALMART_DB.GOLD.WALMART_STORE_DIM s
        ON f.store_id = s.store_id
    JOIN WALMART_DB.GOLD.WALMART_DATE_DIM d
        ON d.date_id = f.date_id
    WHERE f.STORE_WEEKLY_SALES IS NOT NULL
    GROUP BY s.store_type, s.store_id
    ORDER BY store_type, total_weekly_sales
"""

df6 = read_df(sql_sales_store_type)
df6["store_id"] = df6["store_id"].astype(str) # convert to string for better plotting
df6_by_type = df6.groupby("store_type", as_index=False).agg(
    total_weekly_sales=("total_weekly_sales", "sum")
)
fig6 = sales_by_store_type(df6_by_type)
fig6b = sales_by_store_and_type(df6)
fig6c = sales_by_store_and_type_facet(df6)
save_plotly(fig6, "weekly_sales_by_store_type", SNOWFLAKE["output_dir"])
save_plotly(fig6b, "sales_by_store_and_type", SNOWFLAKE["output_dir"])
save_plotly(fig6c, "sales_by_store_and_type_facet", SNOWFLAKE["output_dir"])
print("done.")



# # 7 fuel price by year

sql_fuel_price = """
    SELECT d.report_date,
           f.fuel_price
    FROM WALMART_DB.GOLD.WALMART_WEEKLY_REPORTS_FACT f
    JOIN WALMART_DB.GOLD.WALMART_DATE_DIM d
        ON d.date_id = f.date_id
    WHERE f.fuel_price IS NOT NULL
"""

df7 = read_df(sql_fuel_price)
df7 = add_year_week_month(df7, date_col="report_date")
df7_by_year = df7.groupby("year", as_index=False).agg(
    avg_fuel_price=("fuel_price", "mean")
)
fig7 = fuel_price_by_year(df7_by_year)
df7_by_month = df7.groupby(["year", "month"], as_index=False).agg(
    avg_fuel_price=("fuel_price", "mean")
)
df7_by_month["year_month"] = df7_by_month["year"].astype(str) + "-" + df7_by_month["month"].astype(str).str.zfill(2)

print(df7_by_month.head(15))
fig7b = fuel_price_by_month(df7_by_month)
save_plotly(fig7, "fuel_price_by_year", SNOWFLAKE["output_dir"])
save_plotly(fig7b, "fuel_price_by_month", SNOWFLAKE["output_dir"])
print("done.")


# 8 weekly sales by year, month and date

sql_sales_by_date = """
    SELECT  d.report_date,
            f.store_weekly_sales
    FROM WALMART_DB.GOLD.WALMART_WEEKLY_REPORTS_FACT f
    JOIN WALMART_DB.GOLD.WALMART_DATE_DIM d
        ON d.date_id = f.date_id
    WHERE f.store_weekly_sales IS NOT NULL
"""

df8 = read_df(sql_sales_by_date)
df8 = add_year_week_month(df8, date_col="report_date")

df8_by_year = df8.groupby("year", as_index=False).agg(
    total_weekly_sales=("store_weekly_sales", "sum")
)
df8_by_month = df8.groupby(["month"], as_index=False).agg(
    total_weekly_sales=("store_weekly_sales", "sum")
)
df8['day'] = pd.to_datetime(df8['report_date']).dt.day
df8_by_date = df8.groupby(["day"], as_index=False).agg(
    total_weekly_sales=("store_weekly_sales", "sum")
)
fig8 = sales_by_time(df8_by_year, "year")
fig8b = sales_by_time(df8_by_month, "month")
fig8c = sales_by_time(df8_by_date, "day")
save_plotly(fig8, "weekly_sales_by_year", SNOWFLAKE["output_dir"])
save_plotly(fig8b, "weekly_sales_by_month", SNOWFLAKE["output_dir"])
save_plotly(fig8c, "weekly_sales_by_day", SNOWFLAKE["output_dir"])
print("done.")


# 9 weekly sales by cpi


sql_sales_by_cpi = """
    SELECT  f.cpi,
            f.store_weekly_sales
    FROM WALMART_DB.GOLD.WALMART_WEEKLY_REPORTS_FACT f
    WHERE f.store_weekly_sales IS NOT NULL
"""

df9 = read_df(sql_sales_by_cpi)
df9_by_cpi = df9.groupby(["cpi"], as_index=False).agg(
    total_weekly_sales=("store_weekly_sales", "sum")
)
fig9 = sales_by_cpi(df9_by_cpi)
save_plotly(fig9, "weekly_sales_by_cpi", SNOWFLAKE["output_dir"])
print("done.")



# 10 sales by department

sql_sales_by_dept = """
    SELECT  s.DEPT_ID,
            SUM(f.store_weekly_sales) AS total_weekly_sales
    FROM WALMART_DB.GOLD.WALMART_WEEKLY_REPORTS_FACT f
    JOIN WALMART_DB.GOLD.WALMART_STORE_DIM s
        ON s.dept_id = f.dept_id
    WHERE f.store_weekly_sales IS NOT NULL
    GROUP BY s.dept_id
    ORDER BY total_weekly_sales DESC
"""

df10 = read_df(sql_sales_by_dept)

fig10 = sales_by_dept(df10)
save_plotly(fig10, "weekly_sales_by_dept", SNOWFLAKE["output_dir"])
print("done.")


print("All reports generated.")
# disconnect from Snowflake
disconnect_sf_engine()
print("Finished.")
