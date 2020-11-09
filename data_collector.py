
from scheduling_algorithms import *

avg_arrival_rates = [x for x in range(1,31)]
average_burst = 0.06
q = 0.04
data_file = 'data.csv'

print('starting fcfs')
for i in avg_arrival_rates:
    print("arrival_rate = ", i)
    s = FCFS(i, average_burst, q)
    s.run_sim()
    s.write_metrics(data_file)

print('starting STRF')
for i in avg_arrival_rates:
    print("arrival_rate = ", i)
    s = STRF(i, average_burst, q)
    s.run_sim()
    s.write_metrics(data_file)

print('starting RR')
for i in avg_arrival_rates:
    print("arrival_rate = ", i)
    s = RR(i, average_burst, q)
    s.run_sim()
    s.write_metrics(data_file)