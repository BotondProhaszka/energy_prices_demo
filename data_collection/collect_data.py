import os
from entsoe import EntsoePandasClient
import pandas as pd

from sqlalchemy import create_engine

COUNTY_CODES = ['FR', 'NL', 'BE', 'HU', 'RO'] # List of country codes to collect data for
START_DATE = '2020-01-01' # Start date for data collection (00:00 UTC)
END_DATE = '2020-03-01' # End date for data collection (00:00 UTC)

# Helper functions

def get_api_key():
    API_KEY = None # Set your API key here

    if API_KEY is None:
        try:
            API_KEY = os.environ.get('ENTSOE_API_KEY')
        except Exception as e:
            print(f"Error: {e}")

            raise ValueError('Please set the ENTSOE_API_KEY environment variable or set the my_api_key variable in the code!')
 
    return API_KEY

def get_client(api_key):
    try: 
        client = EntsoePandasClient(api_key)
    except Exception as e:
        print(f"Error in get_client: {e}")
        return None
    print(client)
    return client

def get_filename(country_codes = COUNTY_CODES, start_date=START_DATE, end_date=END_DATE):
    #put the country codes in a string
    country_codes = '-'.join(country_codes)
    filename = f"data/{country_codes}_{start_date}_{end_date}.sqlite"
    return filename

def create_folder(filename):
    try:
        folders = filename.split('/')
        folders = folders[:-1]
        folders = '/'.join(folders)
        if not os.path.exists(folders):
            os.makedirs(folders)
    except Exception as e:
        print(f"Error: {e}")

# Main functions

def run_querry(country_code, client, start_tz, end_tz):
    try:
        df = client.query_day_ahead_prices(country_code, start=start_tz, end=end_tz)        # Data from ENTSO-E
    except Exception as e:
        print(f"Error: {e}")
        return None
    
    df = df.to_frame()

    df = df.rename(columns={0: country_code})
    df['Datetime'] = df.index
    df = df.reset_index(drop=True)

    return df

def save_data(df, filename):
    try:
        engine = create_engine(f'sqlite:///{filename}')
        df.to_sql(filename, engine, if_exists='replace', index=False)
    except Exception as e:
        print(f"Error: {e}")
        return None
    
    return filename

def download_data(client, country_codes = COUNTY_CODES, start_date= START_DATE, end_date= END_DATE):
    filename = get_filename(country_codes, start_date, end_date)

    if os.path.exists(filename):
        print(f"Data already collected in {filename}")
        try:
            df = pd.read_sql(filename, create_engine(f'sqlite:///{filename}'))
            
            #return num rows
            return df.index.size
        
        except Exception as e:
            print(f"Error: {e}")
            return None
    else: 
        create_folder(filename)

    start_tz = pd.Timestamp(START_DATE, tz='UTC')
    end_tz = pd.Timestamp(END_DATE, tz='UTC')

    for country_code in COUNTY_CODES:
        print(f"Collecting data for {country_code}...")
        df_country = run_querry(country_code, client, start_tz, end_tz)
        if country_code == COUNTY_CODES[0]:
            df = df_country
        else:
            df = pd.merge(df, df_country, on='Datetime', how='outer')

    save_data(df, filename)

    return df.index.size

# Main code

if __name__ == '__main__':
    api_key = get_api_key()
    client = get_client(api_key)
    print(client)
    size = download_data(client)
    print(f'There are {size} rows in the dataset.')
