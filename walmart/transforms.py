import pandas as pd

def add_year_week_month(df, date_col="report_date"):
    # Expect a DATE column; compute year & week for grouping
    date = pd.to_datetime(df[date_col])
    df["year"] = date.dt.year
    df["week"] = date.dt.isocalendar().week.astype(int)
    df["month"] = date.dt.month
    return df

def bin_store_size(df, col="store_size"):
    # Bin into quartiles (qcut) or fixed bins (cut); choose one
    # Quartiles adapt to data distribution:
    print("Binning store_size into quartiles")
    # df["store_size_bin"] = pd.qcut(df[col], q=10, labels=["Q1-Small","Q2","Q3", "Q4", "Q5", "Q6", "Q7", "Q8", "Q9", "Q10-Large"])

    # bin_labels = ["Q1-Small", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8", "Q9", "Q10-Large"]
    # df["store_size_bin"] = pd.Categorical(df[col], categories=bin_labels, ordered=True)

    bins = pd.qcut(df[col], 10, duplicates="drop")
    labels = [
        "Q1-Small", "Q2", "Q3", "Q4", "Q5",
        "Q6", "Q7", "Q8", "Q9", "Q10-Large"
    ]
    df["store_size_bin"] = pd.qcut(df[col], q=10, labels=labels, duplicates="drop")
    return df
