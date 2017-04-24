import pandas as pd


file_location = "../test_resources/test_network.xlsx"
resulta = pd.read_excel(file_location, sheetname=None)

print resulta.keys()

pipe_data_frame = resulta['Pipe']
assert isinstance(pipe_data_frame, pd.DataFrame)
print pipe_data_frame.info()

print "second pipe"
print type(pipe_data_frame['Pipe'][0])
print type(pipe_data_frame['Pipe'][1])

print pipe_data_frame.shape[0]
print pipe_data_frame.columns[1]
