import pandas as pd
import sys
import subprocess

df = pd.read_csv ('../meta.csv')

for index, row in df.iterrows():
    num_disks_per_node = row['#disks/node']
    num_nodes_per_rack = row['#nodes/rack']
    subprocess.run(["python", "plot.py", str(num_disks_per_node), str(num_nodes_per_rack)])