from stock_data_path_helper import StockDataPathHelper

path_helper = StockDataPathHelper('data')

fred = path_helper.query_data_structure()
print("---done---")