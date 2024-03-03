from pathlib import Path
from datetime import datetime
import re

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
        start_time = datetime.strptime(start_str, '%Y-%m-%d %H-%M-%S')
        end_time = datetime.strptime(end_str, '%Y-%m-%d %H-%M-%S')
        return start_time, end_time, product, platform, time_period

    def query_data_structure(self):
        self._data_structure = {}
        product_folders = set([p for p in self.root_folder.iterdir() if p.is_dir()])
        self.products = set()
        self.platforms = set()
        self.periods = set()
        self.start_time = datetime.max
        self.end_time = datetime.min
        for product_folder in product_folders:
            product = product_folder.name
            self.products.add(product)
            self._data_structure[product] = {}
            platform_folders = set([p for p in product_folder.iterdir() if p.is_dir()])
            for platform_folder in platform_folders:
                platform = platform_folder.name
                self.platforms.add(platform)
                self._data_structure[product][platform] = {}
                period_folders = set([p for p in platform_folder.iterdir() if p.is_dir()])
                for period_folder in period_folders:
                    time_period = period_folder.name
                    self.periods.add(time_period)
                    self._data_structure[product][platform][time_period] = []
                    files = set([f for f in period_folder.iterdir() if f.is_file()])
                    for file in files:
                        start_time, end_time, _, _, _ = self.from_path(file)
                        self.start_time = min(self.start_time, start_time)
                        self.end_time = max(self.end_time, end_time)
                        self._data_structure[product][platform][time_period].append(file.name)
        return self._data_structure
