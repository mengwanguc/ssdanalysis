import pandas as pd
import sys
# prob[i,j] means the probability 

num_disks_per_node = int(sys.argv[1])
num_nodes_per_rack = int(sys.argv[2])
num_disks_per_rack = num_disks_per_node * num_nodes_per_rack


df = pd.read_csv ('../clusters/d{}n{}.csv'.format(num_disks_per_node, num_nodes_per_rack))

sorted_df = df.sort_values(by='fail_time')
pd.set_option('display.max_columns', None)
sorted_df.to_string(index=False)

from datetime import datetime, timedelta
current_time = None
prev_time = -1

window = 1/4 # 15min

intervals = []
disk_bursts = []
burst = {'disks':[], 'racks':[]}
first_row = True
for index, row in sorted_df.iterrows():
  current_time = row['fail_time']
  interval = (current_time - prev_time)
  # print("current time: {}, prev time: {}, interval: {}".format(
  #     current_time, prev_time, interval
  # ))
  intervals.append(interval)
  prev_time = current_time
  # print(interval)

  disk = row['disk_total_id']
  rack = disk // num_disks_per_rack

  if interval < window:
    burst['disks'].append(disk)
    burst['racks'].append(rack)
    # print(interval)
  else:
    if first_row:
      burst['disks'].append(disk)
      burst['racks'].append(rack)
      first_row = False
    else:
      disk_bursts.append(burst)
      burst = {'disks':[], 'racks':[]}
      burst['disks'].append(disk)
      burst['racks'].append(rack)

disk_bursts.append(burst)

intervals.sort()

burst_counts_by_disk_rack = {}
for bur in disk_bursts:
  disk_count = len(bur['disks'])
  rack_count = len(list(dict.fromkeys(bur['racks'])))
  key = (rack_count, disk_count)
  if key in burst_counts_by_disk_rack:
    burst_counts_by_disk_rack[key] += 1
  else:
    burst_counts_by_disk_rack[key] = 1


print(burst_counts_by_disk_rack)



import matplotlib.pyplot as plt
import matplotlib
import math
figure, axes = plt.subplots()

axes.set_aspect( 1 )
x_range = [0.8,500]
y_range = [0.8,500]
axes.set_xlim(x_range)
axes.set_ylim(y_range)


def cal_radius(count):
  # slope = 11.8
  slope = 20
  # intercept = 2.4
  intercept = 4
  return slope * math.log10(count) + intercept

for burst in burst_counts_by_disk_rack:
  count = burst_counts_by_disk_rack[burst]
  radius = cal_radius(count)
  axes.plot(burst[0], burst[1],1,marker='o',ms=radius,mfc='None',mec='black')


plt.plot(x_range, y_range, linewidth=0.4, color='green')

plt.text(100, 15, "1 occurances")
axes.plot(50, 15.5,1,marker='o',ms=cal_radius(1),mfc='None',mec='black')
plt.text(100, 8, "10 occurances")
axes.plot(50, 8.3,1,marker='o',ms=cal_radius(10),mfc='None',mec='black')
plt.text(100, 4, "100 occurances")
axes.plot(50, 4.15,1,marker='o',ms=cal_radius(100),mfc='None',mec='black')
plt.text(100, 1.5, "1000 occurances")
axes.plot(50, 1.55,marker='o',ms=cal_radius(1000),mfc='None',mec='black')


plt.legend()
plt.xlabel('Number of racks affected')
plt.xscale("log")
plt.ylabel('Number of drives affected')
plt.yscale("log")
plt.title('Frequency of failure bursts\nEack rack has {} nodes. Each node has {} disks. \nA rack has {} disks.'
                .format(num_disks_per_node, num_nodes_per_rack, num_disks_per_rack))
axes.set_xticks([1,2,5,10,20,50,100,200,500])
axes.set_yticks([1,2,5,10,20,50,100,200,500])
axes.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
axes.get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())

figure.set_size_inches(8, 8)
figure.set_dpi(100)
plt.show()

plt.savefig('circles/d{}n{}.png'.format(num_disks_per_node, num_nodes_per_rack))