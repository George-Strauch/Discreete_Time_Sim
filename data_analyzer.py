"""
this python script will take the data collected by the data collection script
and create plots.
THIS WILL NOT RUN ON TSXT SERVER
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

data = np.array(pd.read_csv('data.csv', header=None))

#
plt.plot(range(30), data.T[4][:30], color='r', label='FCFS')
plt.plot(range(30), data.T[4][30:60], color='g', label='STRF')
plt.plot(range(30), data.T[4][60:90], color='b', label='RR')
plt.title('turnaround time')
plt.xlabel('lambda')
plt.ylabel('time (seconds)')
plt.legend()
plt.savefig('ges71_turnaround_time.png', bbox_inches='tight')
plt.show()




plt.plot(range(30), data.T[5][:30], color='r', label='FCFS')
plt.plot(range(30), data.T[5][30:60], color='g', label='STRF')
plt.plot(range(30), data.T[5][60:90], color='b', label='RR')
plt.title('throughput')
plt.xlabel('lambda')
plt.ylabel('processes per second')
plt.legend()
plt.savefig('ges71_throughput.png', bbox_inches='tight')
plt.show()


plt.plot(range(30), data.T[7][:30], color='r', label='FCFS')
plt.plot(range(30), data.T[7][30:60], color='g', label='STRF')
plt.plot(range(30), data.T[7][60:90], color='b', label='RR')
plt.title('average number of time events in the queue')
plt.xlabel('lambda')
plt.ylabel('time events in queue')
plt.legend()
plt.savefig('ges71_avge_time_events.png', bbox_inches='tight')
plt.show()