from collections import deque
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
from streaming_window import StreamingWindow
import csv

class DataManifest:
    # Mapping of time periods to folder names

    def __init__(self, root_folder):
        self.root_folder = Path(root_folder)
        self.products = None
        self.platforms = None
        self.periods = None
        self.start_time = None
        self.end_time = None
        self.query_data_structure()

    def to_path(self, start_time, end_time, product, platform, time_period):
        # Convert time_period abbreviation to folder name
        folder_name = time_period
        # Format start_time and end_time
        start_str = start_time.strftime('%Y-%m-%d %H-%M-%S')
        end_str = end_time.strftime('%Y-%m-%d %H-%M-%S')
        file_name = f"{start_str} to {end_str}"
        # Construct path
        path = Path(str(self.root_folder), product, platform, folder_name, file_name)
        return path

    def from_path(self, path_str):
        path = Path(path_str)
        # Extract components
        product = path.parts[-4]
        platform = path.parts[-3]
        time_period_folder = path.parts[-2]
        file_name = path.name
        # Convert folder name to time period
        time_period = time_period_folder
        # Extract start and end times from file name
        start_str, end_str = file_name.split(' to ')
        end_str, _ = end_str.split('.csv')
        # start_time = datetime.strptime(start_str, '%Y-%m-%d %H-%M-%S')
        # end_time = datetime.strptime(end_str, '%Y-%m-%d %H-%M-%S')
        start_time = DataManifest.convert_str_to_datetime(start_str)
        end_time = DataManifest.convert_str_to_datetime(end_str)
        return start_time, end_time, product, platform, time_period
    
    @staticmethod
    def convert_str_to_datetime(date_str):
        formats = ["%Y-%m-%d %H-%M-%S", "%Y-%m-%d", "%Y-%m-%d %H:%M:%S"]  # Added format with hyphens
        for fmt in formats:
            try:
                # Attempt to parse the string with the current format
                return datetime.strptime(date_str, fmt).replace(tzinfo=timezone.utc)
            except ValueError:
                # If parsing fails, try the next format
                continue
        # If none of the formats match, raise an error
        raise ValueError("date_str does not match any known format")


    def query_data_structure(self):
        self._data_structure = {}
        product_folders = set([p for p in self.root_folder.iterdir() if p.is_dir()])
        self.products = []
        self.platforms = []
        self.periods = []
        self.start_time = datetime.max.replace(tzinfo=timezone.utc)
        self.end_time = datetime.min.replace(tzinfo=timezone.utc)
        for product_folder in product_folders:
            product = product_folder.name
            self.products.append(product)
            self._data_structure[product] = {}
            platform_folders = set([p for p in product_folder.iterdir() if p.is_dir()])
            for platform_folder in platform_folders:
                platform = platform_folder.name
                self.platforms.append(platform)
                self._data_structure[product][platform] = {}
                period_folders = set([p for p in platform_folder.iterdir() if p.is_dir()])
                for period_folder in period_folders:
                    time_period = period_folder.name
                    self.periods.append(time_period)
                    self._data_structure[product][platform][time_period] = []
                    files = set([f for f in period_folder.iterdir() if f.is_file()])
                    for file in files:
                        start_time, end_time, _, _, _ = self.from_path(file)
                        self.start_time = min(self.start_time, start_time)
                        self.end_time = max(self.end_time, end_time)
                        self._data_structure[product][platform][time_period].append(file.name)
        return self._data_structure




    def stream_data(self,
                start_time,
                product, 
                platform, 
                time_period,
                end_time = None):
        if product in self._data_structure:
            if platform in self._data_structure[product]:
                if time_period in self._data_structure[product][platform]:
                    files = self._data_structure[product][platform][time_period]
                    for file_name in sorted(files):  # Ensure files are processed in chronological order
                        file_path = self.root_folder / product / platform / time_period / file_name
                        file_start_time, file_end_time, _, _, _ = self.from_path(str(file_path))
                        end_time = end_time or self.end_time
                        # Only process files that overlap with the query time range
                        if file_start_time <= end_time and file_end_time >= start_time:
                            with open(file_path, mode='r', encoding='utf-8') as file:
                                reader = csv.DictReader(file)
                                for row in reader:
                                    row_time = DataManifest.convert_str_to_datetime(row['Time'])
                                    if start_time <= row_time <= end_time:
                                        yield row

