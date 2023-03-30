
import os

import pandas as pd

csv_path = '../csvoutput'

total_length = 0
for file in os.listdir(csv_path):
    df = pd.read_csv(os.path.join(csv_path, file), index_col=0, header=0)
    total_length += len(df)
    print(df)

print('Total length:', total_length)
