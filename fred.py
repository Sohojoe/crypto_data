from data_manifest import DataManifest

data_manifest = DataManifest('data')

product = data_manifest.products[0]
platform = data_manifest.platforms[0]
time_period = '1H'

for step in data_manifest.stream_data(data_manifest.start_time, product, platform, time_period):
    # step will be an array of floats and ints
    step_as_str = [str(v) for k, v in step.items()]
    print(','.join(step_as_str))

time_period = '1M'
for step in data_manifest.stream_data(data_manifest.start_time, product, platform, time_period):
    # step will be an array of floats and ints
    step_as_str = [str(v) for k, v in step.items()]
    print(','.join(step_as_str))



print("---done---")