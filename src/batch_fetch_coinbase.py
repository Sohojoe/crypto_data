import datetime
import http.client
import json
import pandas as pd
from data_manifest import DataManifest

platform = 'coinbase'
time_period_to_seconds = {
    '1T': 60,
    '5T': 300,
    '15T': 900,
    '1H': 3600,
    '4H': 14400,
    '6H': 21600,
    '8H': 28800,
    '12H': 43200,
    '1D': 86400,
    # '2D': 172800,
    # '3D': 259200,
    # '1W': 604800,
    # '1M': 2629746, # Using an average month length
}

def request_data(date: datetime, duration: int, product_id: str, granularity: int):
    # Calculate the maximum duration for a single request based on granularity and limit of 300 time steps
    max_duration = granularity * 300
    data_frames = []  # List to store data frames from each chunk
    
    # Start time for the first chunk
    start_time = int(date.timestamp())
    # End time for the entire request
    final_end_time = start_time + duration
    
    while start_time < final_end_time:
        # Calculate end time for the current chunk without exceeding the final end time
        end_time = min(start_time + max_duration, final_end_time)
        
        # Request data for the current chunk
        df = request_data_single_chunk(start_time, end_time - granularity, product_id, granularity)
        data_frames.append(df)
        
        # Update start time for the next chunk
        start_time = end_time
    
    # Concatenate all data frames into a single DataFrame
    if data_frames:
        df = pd.concat(data_frames, ignore_index=True)
        df = df.sort_values('Time')
        return df
    else:
        df = pd.DataFrame()  # Return an empty DataFrame if no data was fetched
        df = df.sort_values('Time')
        return df

def request_data_single_chunk(start_time: int, end_time: int, product_id: str, granularity: int):
    conn = http.client.HTTPSConnection("api.exchange.coinbase.com")
    payload = ''
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'My-App-Name'
    }
    # Format API request URL with the current chunk's start and end times
    conn.request("GET", f"/products/{product_id}/candles?granularity={granularity}&start={start_time}&end={end_time}", payload, headers)

    res = conn.getresponse()
    data = res.read()

    # Decode the data and convert it into a list
    data_list = json.loads(data.decode("utf-8"))

    # Convert the list into a DataFrame
    df = pd.DataFrame(data_list, columns=['Time', 'Low', 'High', 'Open', 'Close', 'Volume'])

    # Convert the Unix timestamps in the 'Time' column to datetime format
    df['Time'] = pd.to_datetime(df['Time'], unit='s')

    return df

def fetch_time_period_in_year_chunks(start_time: datetime, end_time: datetime, product_id: str, time_period: str):
    granularity:int = time_period_to_seconds[time_period]
    while start_time < end_time:
        # add one year using datetime helpers
        duration = int(start_time.replace(year=start_time.year+1).timestamp()) - int(start_time.timestamp())
        df = request_data(start_time, duration, product_id, granularity)
        path = data_manifest.to_path(start_time, start_time + datetime.timedelta(seconds=duration-granularity), product_id, platform, time_period)
        file_name = path.with_suffix('.csv')
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(file_name, index=False)
        start_time = start_time.replace(year=start_time.year+1)


# one minute, five minutes, fifteen minutes, one hour, six hours, and one day

# time_periods = ['1T', '5T', '15T', '1H', '6H','1D']
time_periods = ['5T', '15T', '1H', '4H', '6H', '8H', '12H', '1D']
product_id:str = "BTC-USD"
for time_period in time_periods:
    data_manifest = DataManifest('data')
    start_time = datetime.datetime(2015, 1, 1, tzinfo=datetime.timezone.utc)
    end_time = datetime.datetime(2025, 1, 1, tzinfo=datetime.timezone.utc)
    fetch_time_period_in_year_chunks(start_time, end_time, product_id, time_period)
