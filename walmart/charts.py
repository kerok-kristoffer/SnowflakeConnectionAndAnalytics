import plotly.express as px

def save_plotly(fig, basename: str, outdir="out"):
    import os
    print("Saving report to output directory...")
    os.makedirs(outdir, exist_ok=True)
    html = f"{outdir}/{basename}.html"
    png  = f"{outdir}/{basename}.png"
    fig.write_html(html, include_plotlyjs="cdn")
    # For PNG, kaleido must be installed
    try:
        print("Saving PNG:", png)
        fig.write_image(png, scale=2)     # crisp PNG
        print("Saved PNG:", png)
    except Exception as e:
        print("Error saving PNG:", e)
        png = None
    return html, png

# ---------- Charts ----------

def weekly_sales_by_store_and_holiday(df):
    """
    Expects columns: store_id, is_holiday (bool), store_weekly_sales (numeric)
    """
    agg = (df
        .groupby(["store_id","is_holiday"], as_index=False)["store_weekly_sales"]
        .sum()
    )
    fig = px.bar(
        agg,
        x="store_id",
        y="store_weekly_sales",
        color="is_holiday",
        barmode="group",
        title="Weekly Sales by Store & Holiday",
        labels={"store_id":"Store", "store_weekly_sales":"Weekly Sales (sum)", "is_holiday":"Holiday"}
    )
    fig.update_layout(xaxis_tickangle=-45)
    return fig

def weekly_sales_vs_temperature_by_year(df):
    """
    Expects columns: store_weekly_sales, store_temperature, year
    """
    fig = px.scatter(
        df,
        x="week",
        y="store_weekly_sales",
        color="store_temperature",
        opacity=0.6,
        trendline=None,  # Optional: 'ols' requires statsmodels
        title="Weekly Sales vs Temperature by week",
        labels={"store_temperature":"Temperature", "store_weekly_sales":"Weekly Sales"}
    )
    return fig

def weekly_sales_by_store_size(df):
    """
    Expects columns: store_size, store_weekly_sales
    """
    # Box plot shows distribution across size bins
    fig = px.line(
        df,
        x="store_size",
        y="total_weekly_sales",
        title="Weekly Sales by Store Size (Binned)",
        labels={"store_size":"Store Size", "total_weekly_sales":"Weekly Sales"}
    )
    return fig

def monthly_sales_by_store_type(df):
    """
    Expects columns: month, store_type, store_monthly_sales
    """
    # should have three lines, one per store_type
    fig = px.line(
        df,
        x="month",
        y="total_monthly_sales",
        color="store_type",
        title="Monthly Sales by Store Type",
        labels={"month":"Month", "total_monthly_sales":"Monthly Sales", "store_type":"Store Type"}
    )
    return fig

def yearly_markdown_sales_by_store(df):
    """
    Expects columns: year, markdown_type, total_markdown_amount
    """
    fig = px.bar(
        df,
        x="year",
        y="total_markdown_amount",
        color="markdown_type",
        barmode="group",
        title="Yearly Markdown Sales by Year & store",
        labels={"year":"Year", "total_markdown_amount":"Yearly Markdown Sales"}
    )
    return fig


def sales_by_store_type(df):
    """
    Expects columns: store_type, total_weekly_sales
    """
    fig = px.pie(
        df,
        names="store_type",
        values="total_weekly_sales",
        title="Sales by Store Type",
        labels={"store_type":"Store Type", "total_weekly_sales":"Total Sales"}
    )
    return fig


def sales_by_store_and_type(df):
    """
    Expects columns: store_id, store_type, total_weekly_sales
    """
    fig = px.bar(
        df,
        x="store_type",
        y="total_weekly_sales",
        color="store_id",
        barmode="group",
        title="Sales by Store and Type",
        labels={"store_id":"Store", "total_weekly_sales":"Total Sales", "store_type":"Store Type"}
    )
    # fig.update_layout(xaxis_tickangle=-45)
    return fig


def sales_by_store_and_type_facet(df):
    """
    Expects columns: store_id, store_type, total_weekly_sales
    """
    fig = px.bar(
        df,
        x="store_id",
        y="total_weekly_sales",
        facet_col="store_type",
        facet_col_wrap=3,
        title="Sales by Store and Type (Faceted)",
        text_auto=True,
        labels={"store_id":"Store", "total_weekly_sales":"Total Sales", "store_type":"Store Type"}
    )
    fig.update_layout(xaxis_tickangle=-45)
    return fig


def fuel_price_by_year(df):
    """
    Expects columns: year, avg_fuel_price
    """
    fig = px.line(
        df,
        x="year",
        y="avg_fuel_price",
        title="Average Fuel Price by Year",
        labels={"year":"Year", "avg_fuel_price":"Avg Fuel Price"}
    )
    return fig

def fuel_price_by_month(df):
    """
    Expects columns: month, avg_fuel_price
    """
    fig = px.line(
        df,
        x="year_month",
        y="avg_fuel_price",
        title="Average Fuel Price by Month",
        labels={"month":"Month", "avg_fuel_price":"Avg Fuel Price"}
    )
    return fig


def sales_by_time(df, interval="year"):
    """
    Expects columns: year, month, total_weekly_sales
    """
    #format text by billions
    df["total_weekly_sales_formatted"] = df["total_weekly_sales"].apply(lambda x: f"{x/1e9:.2f}B")
    fig = px.bar(
        df,
        x=interval,
        y="total_weekly_sales",
        text="total_weekly_sales_formatted",
        title="Sales by " + interval.capitalize(),
        labels={interval:interval.capitalize(), "total_weekly_sales":"Total Sales"}
    )
    return fig


def sales_by_cpi(df):
    """
    Expects columns: cpi, total_weekly_sales
    """
    fig = px.scatter(
        df,
        x="cpi",
        y="total_weekly_sales",
        title="Sales by CPI",
        labels={"cpi":"CPI", "total_weekly_sales":"Total Sales"}
    )
    return fig


def sales_by_dept(df):
    """
    Expects columns: dept, total_weekly_sales
    """
    fig = px.bar(
        df,
        x="dept_id",
        y="total_weekly_sales",
        title="Sales by Department",
        labels={"dept":"Department", "total_weekly_sales":"Total Sales"}
    )
    fig.update_layout(xaxis_tickangle=-45)
    return fig





