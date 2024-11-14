import os
import pandas as pd
from sqlalchemy import create_engine, inspect

COLUMNS = {}

# helper functions

def get_path(foldername, filename):
    running_dir = os.getcwd()
    parent_dir = os.path.dirname(running_dir)
    full_filename = os.path.join(parent_dir, foldername, filename)
    full_filename = full_filename.replace('\\', '/')
    full_filename = full_filename[0].upper() + full_filename[1:]

    create_folder(full_filename)
    return full_filename

def get_in_filename():
    filename = 'data/FR-NL-BE-HU-RO_2020-01-01_2020-03-01.sqlite'
    full_filename = get_path('data_collection', filename)
    return full_filename

def get_out_filename():
    filename = 'data/final.sqlite'
    full_filename = get_path('data_processing', filename)
    return full_filename

def create_folder(filename):
    try:
        folders = filename.split('/')
        folders = folders[:-1]
        folders = '/'.join(folders)
        if not os.path.exists(folders):
            os.makedirs(folders)
    except Exception as e:
        print(f"Error: {e}")

def get_engine(filename):
    try:
        engine = create_engine(f'sqlite:///{filename}')
        print(engine)
    except Exception as e:
        print(f"Error: {e}")
        raise ValueError('Error creating engine')
    return engine

def get_table_names(engine):
    try:
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        print(f"Table names: {table_names}")
    except Exception as e:
        print(f"Error: {e}")
        raise ValueError('Error getting table names')
    return table_names

def get_data(engine, table_name):
    try:
        df = pd.read_sql_table(table_name, engine)
    except Exception as e:
        print(f"Error: {e}")
        raise ValueError('Error getting df')
    return df

def preprocess_data(df):
    try:
        df['Datetime'] = pd.to_datetime(df['Datetime'])
        df = df.set_index('Datetime')
    except Exception as e:
        print(f"Error: {e}")
        raise ValueError('Error preprocessing df')
    return df

def get_country_codes(df):
    try:
        country_codes = df.columns.unique() 
    except Exception as e:
        print(f"Error: {e}")
        raise ValueError('Error getting country codes')
    return country_codes

def add_column_to_dict(col_name, description, columns=COLUMNS):
    columns[col_name] = description
    return columns

def save_to_sqlite(dfs, filename):
    try:
        engine = get_engine(filename)
        for key, df in dfs.items():
            df.to_sql(key, engine, if_exists='replace')
    except Exception as e:
        print(f"Error: {e}")
        raise ValueError('Error saving to sqlite')
    return None

# process df

def date_process(df):
    try:
        df['Month'] = df.index.month
        df['Day'] = df.index.day
        df['Hour'] = df.index.hour
        df['AM/PM'] = df.index.strftime('%p')
    except Exception as e:
        print(f"Error: {e}")
        raise ValueError('Error df processing')
    return df

def moving_average(df, column_names):
    try:
        for col in column_names:
            df[f'{col}_7d_MA'] = df[col].rolling(window=7*24, min_periods=1).mean()  # 7 napos mozgóátlag
            df[f'{col}_30d_MA'] = df[col].rolling(window=30*24, min_periods=1).mean()  # 30 napos mozgóátlag
            add_column_to_dict(f'{col}_7d_MA', f'7 day moving average of {col}')
            add_column_to_dict(f'{col}_30d_MA', f'30 day moving average of {col}')
    except Exception as e:
        print(f"Error: {e}")
        raise ValueError('Error calculating moving average')
    return df

def weekly_means(df, column_names):
    try:
        for col in column_names:
            df[f'{col}_weekly_mean'] = df[col].rolling(window=7*24, min_periods=1).mean()
            add_column_to_dict(f'{col}_weekly_mean', f'Weekly mean of {col}')
    except Exception as e:
        print(f"Error: {e}")
        raise ValueError('Error calculating weekly means')
    return df

def weekly_min_max_values(df, column_names):
    try:
        for col in column_names:
            df[f'{col}_weekly_min'] = df[col].rolling(window=7*24, min_periods=1).min()
            df[f'{col}_weekly_max'] = df[col].rolling(window=7*24, min_periods=1).max()
            add_column_to_dict(f'{col}_weekly_min', f'Weekly min of {col}')
            add_column_to_dict(f'{col}_weekly_max', f'Weekly max of {col}')
    except Exception as e:
        print(f"Error: {e}")
        raise ValueError('Error calculating min max values')
    return df

def pct_changes(df, column_names):
    try:
        for col in column_names:
            df[f'{col}_daily_pct_change'] = df[col].pct_change(periods=24) * 100  # Daily
            df[f'{col}_weekly_pct_change'] = df[col].pct_change(periods=7*24) * 100  # Weekly
            df[f'{col}_monthly_pct_change'] = df[col].pct_change(periods=30*24) * 100  # Monthly
            add_column_to_dict(f'{col}_daily_pct_change', f'Daily percentage change of {col}')
            add_column_to_dict(f'{col}_weekly_pct_change', f'Weekly percentage change of {col}')
            add_column_to_dict(f'{col}_monthly_pct_change', f'Monthly percentage change of {col}')
    except Exception as e:
        print(f"Error: {e}")
        raise ValueError('Error calculating percentage changes')
    return df

def volatility(df, column_names):
    try:
        for col in column_names:
            df[f'{col}_daily_volatility'] = df[col].pct_change(periods=24).rolling(window=24, min_periods=1).std() * 100  # Daily
            df[f'{col}_weekly_volatility'] = df[col].pct_change(periods=7*24).rolling(window=7*24, min_periods=1).std() * 100  # Weekly
            df[f'{col}_monthly_volatility'] = df[col].pct_change(periods=30*24).rolling(window=30*24, min_periods=1).std() * 100  # Monthly
            add_column_to_dict(f'{col}_daily_volatility', f'Daily volatility of {col}')
            add_column_to_dict(f'{col}_weekly_volatility', f'Weekly volatility of {col}')
            add_column_to_dict(f'{col}_monthly_volatility', f'Monthly volatility of {col}')
    except Exception as e:
        print(f"Error: {e}")
        raise ValueError('Error calculating volatility')
    return df

def peaks(df, column_names):
    try:
        for col in column_names:
            df[f'{col}_peak_hours'] = df[col].rolling(window=24, min_periods=1).max()
            df[f'{col}_peak_weeks'] = df[col].rolling(window=7*24, min_periods=1).max()
            add_column_to_dict(f'{col}_peak_hours', f'Peak hours of {col}')
            add_column_to_dict(f'{col}_peak_weeks', f'Peak weeks of {col}')
    except Exception as e:
        print(f"Error: {e}")
        raise ValueError('Error calculating peak hours')
    return df

def get_anomalies(df, column_names):
    anomalies = pd.DataFrame()
    for col in column_names:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        anomalies[col] = df[(df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))][col]
    return anomalies

def correlation_matrix(df):
    try:
        df2 = df.copy()
        df2['AM/PM'] = df2['AM/PM'].map({'AM': 0, 'PM': 1})
        corr = df2.corr()
    except Exception as e:
        print(f"Error: {e}")
        raise ValueError('Error calculating correlation matrix')
    return corr

def process_all_data(df, column_names):
    df = date_process(df)
    df = moving_average(df, column_names)
    df = weekly_means(df, column_names)
    df = weekly_min_max_values(df, column_names)
    df = pct_changes(df, column_names)
    df = volatility(df, column_names)
    df = peaks(df, column_names)
    return df

# Main code

def main():
    filename = get_in_filename()
    out_file_name = get_out_filename()

    if os.path.exists(out_file_name):
        print(f"Data already processed in {filename}")
        return None
    
    engine = get_engine(filename)
    table_names = get_table_names(engine)
    df = get_data(engine, table_names[0])
    df = preprocess_data(df)

    country_codes = get_country_codes(df)
    column_names = country_codes

    df = process_all_data(df, column_names)

    anomalies = get_anomalies(df, column_names)
    corr = correlation_matrix(df)

    dfs = {
        'df': df,
        'anomalies': anomalies,
        'corr': corr
    }
    save_to_sqlite(dfs, out_file_name)

    print(COLUMNS.keys())

if __name__ == '__main__':
    main()