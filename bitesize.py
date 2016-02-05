#!/usr/bin/python
#
# bitesie.py    Block I/O size histogram per process.
#               For Linux, uses BCC, eBPF. See .c file.
#
# Written as a basic example of using a histogram to show a distribution.
#
# The default interval is 1 seconds. A Ctrl-C will print the partially
# gathered histogram then exit.
#
# Copyright (c) 2016 Allan McAleavy.
# Copyright (c) 2015 Brendan Gregg.
# Licensed under the Apache License, Version 2.0 (the "License")
#

from bcc import BPF
from time import sleep

# load BPF program
b = BPF(src_file = "bitesize.c")
b.attach_kprobe(event="blk_account_io_start", fn_name="trace_pid_start")
b.attach_kprobe(event="blk_account_io_completion", fn_name="do_count")


# header
print("Tracing... Hit Ctrl-C to end.")

# trace until Ctrl-C
exiting = 0
dist = b.get_table("dist")
while (1):
    try:
        sleep(1)
    except KeyboardInterrupt:
        exiting = 1
    dist.print_log2_hist("Kbytes", "Process Name")
    dist.clear()

    if exiting :
        exit()

