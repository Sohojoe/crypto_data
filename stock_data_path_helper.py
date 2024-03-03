from pathlib import Path
from datetime import datetime
import re

class StockDataPathHelper:
    # Mapping of time periods to folder names

    def __init__(self, root_folder):
        self.root_folder = Path(root_folder)

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
        product = path.parts[-3]
        time_period_folder = path.parts[-2]
        file_name = path.name
        # Convert folder name to time period
        time_period = time_period_folder
        # Extract start and end times from file name
        start_str, end_str = file_name.split(' to ')
        start_time = datetime.strptime(start_str, '%Y-%m-%d %H-%M-%S')
        end_time = datetime.strptime(end_str, '%Y-%m-%d %H-%M-%S')
        return start_time, end_time, product, time_period

    def query_data_structure(self):
        data_structure = {}
        for product_folder in self.root_folder.iterdir():
            if product_folder.is_dir():
                product = product_folder.name
                data_structure[product] = {}
                for platform_folder in product_folder.iterdir():
                    if platform_folder.is_dir():
                        platform = platform_folder.name
                        data_structure[product][platform] = {}
                        for period_folder in platform_folder.iterdir():
                            if period_folder.is_dir():
                                time_period = period_folder.name
                                data_structure[product][platform][time_period] = []
                                for file in period_folder.iterdir():
                                    if file.is_file():
                                        data_structure[product][platform][time_period].append(file.name)
        return data_structure
