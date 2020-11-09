import numpy as np

"""
event types are as follows:
1) arrival process
2) time slice
3) process termination

event queue is a linked list of events and the processes are handled as a member of an event.
"""


class Process:
    def __init__(self, pid, arrival_time, burst):
        self.pid = pid
        self.time = arrival_time
        self.burst_time = burst
        self.time_remaining = burst
        self.termination_time = 0

    def __str__(self):
        return f"<Process: pid={self.pid}, arrival_time={self.time}, burst_time={self.burst_time}, remaining={self.time_remaining}, termination_time={self.termination_time}>"



class Event:
    def __init__(self, event_type, time, proc):
        self.event_type=event_type
        self.time=time
        self.process=proc
        self.next=None

    def __str__(self):
        return f"type={self.event_type}, time={self.time}, next_exists?={self.next is not None} process={self.process}"



class Scheduler:
    def __init__(self, arrival_rate, avg_burst_time, quantum):
        self.inter_process_arrival_rate = 1/arrival_rate
        self.avg_burst_time = avg_burst_time
        self.quantum = quantum
        self.algorithm = 0

        self.new_processes = []
        self.processes = []
        self.done_processes = []
        self.head_event_queue = None
        self.tail_event_queue = None
        self.current_event = None
        self.clock = 0

        #  metrics
        self.cpu_time = 0
        self.processes_completed = 0
        self.event_counter = 0
        self.time_events_ready = 0 # number of time slice events in the event queue
        self.termination_event_ready = False # can only be one termination events in the queue currently
        self.term_event = None # the termination event object in the queue if it exists
        self.last_time_event = None # last time event object for faster indexing

        self.time_events_handled = 0
        self.arrival_events_handled = 0
        self.termination_events_handled = 0

        # start
        self.add_arrival_events(12000)
        # self.test_queue()


    def test_queue(self):
        i = 0
        tmp= self.head_event_queue
        while True:
            if tmp is None:
                break
            else:
                if i < 500:
                    print(tmp)
                tmp = tmp.next
                i += 1
        print(f'{i} events in LL')


    def collect_metrics(self):
        """
        collects average turnaround time,
        total throughput processes completed per second,
        average wait time,
        average number of processes in queue
        :return: dict {avg_turnaround_time, throughput, avg_wait_time, avg_n_processes_queued}
        """
        waiting_times = []
        turnaround_times = []

        for p in self.done_processes:
            t = p.termination_time - p.time
            turnaround_times.append(t)
            waiting_times.append(t-p.burst_time)

        avg_turnaround_time = sum(turnaround_times)/len(turnaround_times)
        avg_wait_time = sum(waiting_times)/len(waiting_times)
        throughput = self.processes_completed / self.clock
        avg_queue_len = avg_wait_time / self.inter_process_arrival_rate

        d = {"average turnaround time": avg_turnaround_time,
             "throughput": throughput,
             "average wait time": avg_wait_time,
             "average time events in queue": avg_queue_len
             }
        return d


    # writes the metrics as a line in the given data file
    def write_metrics(self, data_file: str):
        metrics = self.collect_metrics()
        line = f"{self.algorithm},{1/self.inter_process_arrival_rate},{self.avg_burst_time},{self.quantum},{metrics['average turnaround time']},{metrics['throughput']},{metrics['average wait time']},{metrics['average time events in queue']}\n"
        with open(data_file, 'a') as f:
            f.write(line)


    # function for generating arrival events to the queue
    def add_arrival_events(self, n_events):
        bursts_times = np.random.exponential(self.avg_burst_time, n_events)
        inter_arrival_times = np.random.poisson(self.inter_process_arrival_rate * 1000, n_events) / 1000

        t = self.clock
        if self.tail_event_queue is not None:
            t = self.tail_event_queue.time

        arrival_times = []
        for i in range(len(inter_arrival_times)):
            t += inter_arrival_times[i]
            arrival_times.append(t)

        next_pid = 0
        if self.tail_event_queue is not None:
            next_pid = self.tail_event_queue.process.pid + 1

        start = 0
        e = 0
        if self.tail_event_queue is not None:
            e = self.tail_event_queue
        else:
            p = Process(pid=next_pid, arrival_time=arrival_times[0], burst=bursts_times[0])
            self.head_event_queue = Event(1, arrival_times[0], p)
            e = self.head_event_queue
            start = 1

        for i in range(start, n_events):
            p = Process(pid=next_pid+i, arrival_time=arrival_times[i], burst=bursts_times[i])
            e.next = Event(event_type=1, time=arrival_times[i], proc=p)
            e = e.next
        self.tail_event_queue = e


    # adds a time event to the queue. dynamically finds the right time for it
    def add_time_event(self, proc):
        self.time_events_ready += 1
        if self.last_time_event is not None:
            event = Event(2, self.last_time_event.time, proc)
            event.next = self.last_time_event.next
            self.last_time_event.next = event
            self.last_time_event = event

        elif self.termination_event_ready:
            event = Event(2, self.term_event.time, proc)
            event.next = self.term_event.next
            self.term_event.next = event
            self.last_time_event = event

        else:
            event = Event(2, self.clock, proc)
            event.next = self.head_event_queue
            self.head_event_queue = event
            self.last_time_event = event

        if self.term_event is not None and self.term_event.time < self.head_event_queue.time:
            print('there was a problem caught in add time event')
            exit(0)


    # adds termination event to the event queue. much of the is error checking
    def add_termination_event(self, time, proc):
        if time < self.clock:
            print("time problem in add term event")
            exit(1)

        if self.termination_event_ready: # there should not be more than 1 termination event in the queue at a time
            print('there is an error in add term event, more than one termination event in queue')
            print(self.term_event)
            print(self.stats())
            exit(1)

        # declare the event
        event = Event(3, time, proc)
        self.term_event = event
        self.termination_event_ready = True

        #  if there are no time events in the queue
        if self.last_time_event is None:
            if self.head_event_queue.time > time: # first check if it belongs in the front
                event.next = self.head_event_queue
                self.head_event_queue = event
                return

            else: # otherwise add it to the ll normally
                tmp = self.head_event_queue
                while True:
                    if tmp is self.tail_event_queue:
                        # add arrival events if none are left
                        self.add_arrival_events(1000)

                    if tmp.next.time > time:
                        event.next = tmp.next
                        tmp.next = event
                        return
                    else:
                        tmp = tmp.next

        else:   # there is a time event in the queue
            # first adjust the time of all time events as no time event should come before the term event
            tmp = self.head_event_queue
            while True:
                if tmp.event_type == 2:
                    tmp.time = time
                    tmp = tmp.next
                else:
                    break

            if self.last_time_event.next is not tmp: # bug check
                print('this is an issue in add term event')
                exit(1)

            # after the term event, the rest of the time events will follow
            event.next = self.head_event_queue
            self.head_event_queue = self.last_time_event.next

            # check if the term event belongs at the front
            if time < self.head_event_queue.time:
                self.last_time_event.next = self.head_event_queue
                self.head_event_queue = event
                return

            else:   #otherwise add to ll normally
                tmp = self.last_time_event
                while True:
                    if tmp is self.tail_event_queue:
                        self.add_arrival_events(1000)

                    if tmp.next.time > time:
                        self.last_time_event.next = tmp.next
                        tmp.next = event
                        break
                    else:
                        tmp = tmp.next


    # handles arrival events
    def handle_arrival_event(self, proc):
        self.arrival_events_handled += 1
        self.add_time_event(proc)


    # handles time slice events
    def handle_time_event(self, proc):
        self.time_events_handled += 1
        self.time_events_ready-=1

        if self.last_time_event.process is proc:
            self.last_time_event = None

        self.cpu_time += proc.burst_time
        t = proc.time_remaining
        proc.time_remaining = 0
        self.add_termination_event(self.clock+t, proc)


    # terminates a done process
    def handle_termination_event(self, proc):
        self.termination_events_handled += 1
        self.termination_event_ready = False
        proc.termination_time = self.clock
        self.done_processes.append(proc)
        self.processes_completed += 1
        self.term_event = None


    # helper function for debugging
    def show_events(self, n):
        print()
        tmp = self.head_event_queue
        for _ in range(n):
            print(tmp)
            tmp = tmp.next
        print()


    # takes the first event off the ll and returns it
    def pop_event(self):
        tmp = self.head_event_queue
        self.head_event_queue = self.head_event_queue.next
        return tmp


    # this is the main function of the sim.
    # runs events until 10,000 processes are done
    def run_sim(self):
        event_menu = {
            1: self.handle_arrival_event,
            2: self.handle_time_event,
            3: self.handle_termination_event
        }

        while True:
            self.current_event = self.pop_event()
            self.clock = self.current_event.time

            func = event_menu[self.current_event.event_type]
            func(self.current_event.process)

            self.event_counter += 1
            if self.processes_completed == 10000:
                break


    # outputs final data
    def stats(self):
        s = f'------------------------------------\n' \
            f'clock={self.clock}\n' \
            f'cpu_time={self.cpu_time}\n' \
            f'time_events_ready={self.time_events_ready}\n' \
            f'termination_event_ready={self.termination_event_ready}\n' \
            f'term_event={self.term_event}\n' \
            f'last_time_event={self.last_time_event}\n' \
            f'events_completed={self.event_counter}\n' \
            f'arrival_events_called={self.arrival_events_handled}\n' \
            f'time_slice_events={self.time_events_handled}\n' \
            f'termination_events_called={self.termination_events_handled}\n' \
            f'processes_completed={self.processes_completed}'
        print(s)
        done_ids = [p.pid for p in self.done_processes[len(self.done_processes)-20:]]
        print("done_recent: ", done_ids)
        print('------------------------------------\n')
        # --------------------------------------------------------


class FCFS(Scheduler):
    '''
    first come first serve. this is the most basic scheduling algorithm
    once a process is created, it is added to the queue without any preemption.
    Scheduler is already FCFS so this is just a shell class that inherits from Scheduler
    '''
    def __init__(self, arrival_rate, avg_service_time, quantum):
        super().__init__(arrival_rate, avg_service_time, quantum)
        self.algorithm = 1

# --------------------------------------------------------


class STRF(Scheduler):
    '''
    Shortest time remaining first. Orders processes by how much time they will
    once a process is created, it is added to the queue in order of how much time it will take.
    '''

    def __init__(self, arrival_rate, avg_service_time, quantum):
        super().__init__(arrival_rate, avg_service_time, quantum)
        self.algorithm = 2


    def add_time_event(self, proc):
        self.time_events_ready += 1
        if self.termination_event_ready:
            event = Event(2, self.term_event.time, proc)
            tmp_event = self.term_event
            while True:
                if tmp_event.next.event_type != 2 or tmp_event.next.process.burst_time > proc.burst_time:
                    event.next = tmp_event.next
                    tmp_event.next = event
                    if tmp_event is self.last_time_event or self.time_events_ready-1 == 0:
                        self.last_time_event = event
                    break
                else:
                    tmp_event = tmp_event.next

        else:
            # first make sure the time event does not belong as the head
            if self.head_event_queue.event_type != 2 or (self.head_event_queue.event_type == 2 and self.head_event_queue.process.burst_time > proc.burst_time):
                event = Event(2, self.clock, proc)
                if self.head_event_queue.event_type !=  2:
                    self.last_time_event = event

                event.next = self.head_event_queue
                self.head_event_queue = event

            else:
                tmp_event = self.head_event_queue
                while True:
                    if tmp_event is self.last_time_event:
                        event = Event(event_type=2, time=tmp_event.time, proc=proc)
                        event.next = self.last_time_event.next
                        self.last_time_event.next = event
                        self.last_time_event = event
                        break

                    elif tmp_event.next.process.burst_time > proc.burst_time:
                        event = Event(2, tmp_event.time, proc)
                        event.next = tmp_event.next
                        tmp_event.next = event
                        break

                    else:
                        tmp_event = tmp_event.next

# --------------------------------------------------------


class RR(Scheduler):
    '''
    Round robbin. This algorithm will only work on a process for a specific amount of time
    then schedules another time event for that process at the end of the queue until it is done
    '''

    def __init__(self, arrival_rate, avg_service_time, quantum):
        super().__init__(arrival_rate, avg_service_time, quantum)
        self.algorithm = 3


    def add_basic_event(self, event:Event, start_on_last=False):
        if start_on_last:
            # first check that there are no bugs:
            if self.last_time_event.time > event.time:
                print('error in add basic event')
                exit(1)

            # next check if it should be put as next
            if self.last_time_event.next.time > event.time:
                event.next = self.last_time_event.next
                self.last_time_event.next = event
                return

            else:
                tmp = self.last_time_event
                while True:
                    if tmp is self.tail_event_queue:
                        self.add_arrival_events(1000)

                    if tmp.next.time > event.time:
                        event.next = tmp.next
                        tmp.next = event
                        return
                    else:
                        tmp = tmp.next

        # end if start on last
        else:   # starting from beginning
            # first check if it belongs as the head
            if self.head_event_queue.time > event.time:
                event.next = self.head_event_queue
                self.head_event_queue = event
                return

            else:
                tmp = self.head_event_queue
                while True:
                    if tmp is self.tail_event_queue:
                        self.add_arrival_events(1000)

                    if tmp.next.time > event.time:
                        event.next = tmp.next
                        tmp.next = event
                        return
                    else:
                        tmp = tmp.next


    def add_time_event(self, proc):
        self.time_events_ready += 1

        if self.last_time_event is not None and proc is not self.last_time_event.process:
            event = Event(2, self.last_time_event.time+self.quantum, proc)
            tt =  self.last_time_event.time+self.quantum
            self.add_basic_event(event, start_on_last=True)
            self.last_time_event = event

        else:
            event = Event(2, self.clock+self.quantum, proc)
            tt = self.clock+self.quantum
            self.add_basic_event(event)
            self.last_time_event = event


    def add_termination_event(self, time, proc):
        if proc.time > time:
            print('process cannot terminate before its arrival')
            print(proc)
            print(time)
            print()
            self.stats()
            for x in self.done_processes:
                print(x)
            exit(1)

        event = Event(3, time, proc)
        self.add_basic_event(event)


    def handle_time_event(self, proc):
        self.time_events_handled += 1
        self.time_events_ready-=1

        if proc.time_remaining > self.quantum:
            self.cpu_time += self.quantum
            proc.time_remaining -= self.quantum
            self.add_time_event(proc)
        else:
            self.cpu_time += proc.time_remaining
            t =  proc.time_remaining
            proc.time_remaining = 0

            if proc is self.last_time_event.process:
                self.last_time_event = None

            self.add_termination_event(self.clock+t, proc)

