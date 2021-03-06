#!/usr/bin/python
# @lint-avoid-python-3-compatibility-imports
#
# biostat   Block iostat command
#           For Linux, uses BCC, eBPF. See .c file.
#
# Copyright (c) 2016 Allan McAleavy
# Licensed under the Apache License, Version 2.0 (the "License")
#

from __future__ import print_function
from bcc import BPF
from time import sleep
import signal
import re
# signal handler
def signal_ignore(signal, frame):
    print()


# load BPF program
b = BPF(src_file="bio.c")
b.attach_kprobe(event_re="blk_start_request", fn_name="trace_req_start")
b.attach_kprobe(event_re="blk_account_io_completion", fn_name="do_count")

# header
exiting = 0
writes=0
reads=0
disk=""
wblk=0
rbk=0
wbk=0
wsvc=0
rsvc=0
# output
print("\n%-8s %-8s %-8s %-12s %-12s %-8s %-8s %-12s %-12s" % ( "Device","r/s","w/s","r/Kb","w/Kb","rsz","wsz","r_ms","w_ms"))
while 1:
    try:
        sleep(1)
    except KeyboardInterrupt:
        exiting = 1
        signal.signal(signal.SIGINT, signal_ignore)

    counts = b.get_table("counts")
    for k, v in sorted(counts.items(), key=lambda counts: counts[1].value):
        if k.tp == 1:
            writes=v.value
            wblk = k.wblk
            wbk = float((k.wblk * writes))/1024
            wsvc=k.wsvc
        if k.tp == 2:
            reads=v.value
            rblk = k.rblk
            rbk = float((k.rblk * reads) )/1024
            rsvc=k.rsvc


        pat = re.compile("^[a-z]")
        if pat.match(k.disk_name):
           disk = k.disk_name
           print("%-8s %-8d %-8d %-12.2f %-12.2f %-8d %-8d %-12.2f %-12.2f" % (disk,reads,writes,rbk,wbk,rblk,wblk,rsvc,wsvc))

        counts.clear()
    reads = 0
    writes = 0
    wblk = 0
    rblk = 0
    rbk = 0
    wbk = 0
    wsvc =0
    rsvc=0

    if exiting:
        print("Detaching...")
        exit()
