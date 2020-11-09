import sys
"""
Driver code for discrete time simulator
"""
from scheduling_algorithms import *


def help_():
    s = "this program takes 4 arguments and should be executed as\npython main.py arg1 arg2 arg3 arg4\n" \
        "arg1: integer 1-3 representing the desired scheduling algorithm. \t1) FCFS \t2) STRF \t3) RR\n" \
        "arg2: integer 1-30, average arrival rate (average processes per second)\n" \
        "arg3: float, average burst time (0.06 is recommended)\n" \
        "arg4: float, time quantum for RR (0.04 is recommended and this argument may be omitted if arg1 is not 3)\n"
    print(s)
    exit(0)


def main():
    if not (len(sys.argv) == 5 or (len(sys.argv) == 4 and sys.argv[1] != 3)):
        help_()
        exit(0)

    algorithm = int(sys.argv[1])
    arrival_rate = int(sys.argv[2])
    avg_burst = float(sys.argv[3])
    quantum = 0
    if sys.argv[1] == '3':
        quantum = float(sys.argv[4])

    print(algorithm, arrival_rate, avg_burst, quantum)
    s = None
    if algorithm == 1:
        s = FCFS(arrival_rate=arrival_rate, avg_service_time=avg_burst, quantum=quantum)
    elif algorithm == 2:
        s = STRF(arrival_rate=arrival_rate, avg_service_time=avg_burst, quantum=quantum)
    elif algorithm == 3:
        s = RR(arrival_rate=arrival_rate, avg_service_time=avg_burst, quantum=quantum)
    else:
        help_()

    s.run_sim()
    s.stats()
    metrics = s.collect_metrics()

    for key in metrics.keys():
        print(f'{key}: {metrics[key]}')


if __name__ == '__main__':
    main()

