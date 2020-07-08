# -*- coding: utf-8 -*-
"""
A module for multithreading data processing in OpenTabulate.

Created and written by Maksym Neyra-Nesterenko, with support and funding from the
Center for Special Business Projects (CSBP) at Statistics Canada.
"""
import logging
import os
import signal
from copy import deepcopy
from threading import Thread, Event
from queue import Queue, Empty

from opentabulate.main.main_funcs import process
from opentabulate.main.thread_exception import ThreadInterruptError

class ThreadPool():
    """
    A custom thread pool class. The pool creates a fixed number (specified by the 
    user) of worker threads, each of which process data tasks independently from a 
    queue.

    The pool has __enter__ and __exit__ methods so it can be loaded into its own
    context (e.g. used in a 'with' statement).

    Attributes:
        workers (list): a list of threading.Thread objects, i.e. consisting of
            worker threads.
        rcodes (list): return codes for each data task completed by a thread.
        task_queue (queue.Queue): a thread-safe queue accessible by each worker
            thread.
        interrupt (threading.Event): an interrupt event used to cleanly terminate
            the worker threads.
    """
    def __init__(self, tasks, num_threads=1):
        """
        Initialize thread pool by loading task queue and worker threads.

        Args:
            tasks (list): list of Source objects
            num_threads (int): number of worker threads to initialize

        Raises:
            AssertionError: number of worker threads specified must be > 0.
        """
        self.workers = list()
        self.rcodes = [None] * len(tasks)
        self.task_queue = Queue()
        self.interrupt = Event()

        assert (num_threads > 0), "Number of threads must be > 0"
        
        for _ in range(num_threads):
            self.workers.append(Thread(target=self._process_jobs))

        for j in range(len(tasks)):
            self.task_queue.put((tasks[j], j)) # (Source, idx)

    def execute_threads(self):
        """Execute tasks on worker threads until queue is empty."""
        for w in self.workers:
            w.start()
        
        self.task_queue.join()

        for w in self.workers:
            w.join()

    def get_rcodes(self):
        """
        Obtain return codes from tasks completed by worker threads. The order
        of the return codes is preserved and matches that of the input argument 
        'tasks' in self.__init__(.).
        """
        return deepcopy(self.rcodes)

    def _signal_handler(self, signum, frame):
        """If interrupt signal is heard, set interrupt flag."""
        self.interrupt.set()
        logging.error('Interrupt signal %s caught' % signum)

    def _process_jobs(self):
        """Worker thread function."""
        while True:
            source, idx, rcode = None, None, None
            try:
                source, idx = self.task_queue.get(block=False)
                if not self.interrupt.is_set():
                    rcode = process(source, self.interrupt)
                else:
                    rcode = None
            except Empty:
                break
            
            self.rcodes[idx] = rcode
            self.task_queue.task_done()

    def __enter__(self):
        signal.signal(signal.SIGINT, self._signal_handler)
        return self

    def __exit__(self, exc_type, exc_value, tb):
        signal.signal(signal.SIGINT, signal.default_int_handler)