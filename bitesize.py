#!/usr/bin/python
#
# bitehist.py   Block I/O size histogram.
#               For Linux, uses BCC, eBPF. See .c file.
#
# USAGE: bitesize
# Ctrl-C will print the partially gathered histogram then exit.
#
# Copyright (c) 2016 Allan McAleavy
# Licensed under the Apache License, Version 2.0 (the "License")
#
# 05-Feb-2016 Allan McAleavy ran pep8 against file

from bcc import BPF
from time import sleep

# load BPF program
b = BPF(src_file="bitesize.c")
b.attach_kprobe(event="blk_account_io_start", fn_name="trace_pid_start")
b.attach_kprobe(event="blk_account_io_completion", fn_name="do_count")

print("Tracing... Hit Ctrl-C to end.")

# trace until Ctrl-C
dist = b.get_table("dist")

try:
        sleep(99999999)
except KeyboardInterrupt:
        print
        dist.print_log2_hist("Kbytes", "Process Name:")
