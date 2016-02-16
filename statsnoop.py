#!/usr/bin/python
# @lint-avoid-python-3-compatibility-imports
#
# statsnoop Trace stat() syscalls.
#           For Linux, uses BCC, eBPF. Embedded C.
#
# USAGE: statsnoop [-h] [-t] [-x] [-p PID]
#
# Copyright 2016 Netflix, Inc.
# Licensed under the Apache License, Version 2.0 (the "License")
#
# 08-Feb-2016   Brendan Gregg   Created this.
# 16-Feb-2016   Allan McAleavy updated for BPF_PERF_OUTPUT

from __future__ import print_function
from bcc import BPF
import argparse
import ctypes as ct

# arguments
examples = """examples:
    ./statsnoop           # trace all stat() syscalls
    ./statsnoop -t        # include timestamps
    ./statsnoop -x        # only show failed stats
    ./statsnoop -p 181    # only trace PID 181
"""
parser = argparse.ArgumentParser(
    description="Trace stat() syscalls",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog=examples)
parser.add_argument("-t", "--timestamp", action="store_true",
    help="include timestamp on output")
parser.add_argument("-x", "--failed", action="store_true",
    help="only show failed stats")
parser.add_argument("-p", "--pid",
    help="trace this PID only")
args = parser.parse_args()
debug = 0

# define BPF program
bpf_text = """
#include <uapi/linux/ptrace.h>

struct val_t {
    u32 pid;
    u64 ts;
    char comm[16];
    const char * fname;
};

struct data_t {
    u32 pid;
    u64 ts;
    u64 delta;
    int ret;
    char comm[16];
    char fname[255];
};

BPF_HASH(args_filename, u32, const char *);
BPF_HASH(infobyreq, u32,struct val_t);
BPF_PERF_OUTPUT(events);

int trace_entry(struct pt_regs *ctx, const char __user *filename)
{
    struct val_t val = {};
    u32 pid = bpf_get_current_pid_tgid();

    FILTER
    if  (bpf_get_current_comm(&val.comm, sizeof(val.comm)) == 0) {
        val.pid = bpf_get_current_pid_tgid();
        val.ts = bpf_ktime_get_ns();
        val.fname = filename;
        infobyreq.update(&pid, &val);
    }

    return 0;
};

int trace_return(struct pt_regs *ctx)
{
    u32 pid = bpf_get_current_pid_tgid();
    struct val_t *valp;
    struct data_t data = {};

    u64 tsp = bpf_ktime_get_ns();

    valp = infobyreq.lookup(&pid);
    if (valp == 0) {
        // missed entry
        return 0;
    }
    bpf_probe_read(&data.comm,sizeof(data.comm), valp->comm);
    bpf_probe_read(&data.fname,sizeof(data.fname),(void *)valp->fname);
    data.pid = valp->pid;
    data.delta = tsp - valp->ts;
    data.ts = tsp /1000;
    data.ret = ctx->ax;

    //bpf_trace_printk("%d %s \\n", ret, data.fname);
    args_filename.delete(&pid);
    events.perf_submit(ctx,&data,sizeof(data));
    infobyreq.delete(&pid);

    return 0;
}
"""
if args.pid:
    bpf_text = bpf_text.replace('FILTER',
        'if (pid != %s) { return 0; }' % args.pid)
else:
    bpf_text = bpf_text.replace('FILTER', '')
if debug:
    print(bpf_text)

# initialize BPF
b = BPF(text=bpf_text)
b.attach_kprobe(event="sys_stat", fn_name="trace_entry")
b.attach_kprobe(event="sys_statfs", fn_name="trace_entry")
b.attach_kprobe(event="sys_newstat", fn_name="trace_entry")
b.attach_kretprobe(event="sys_stat", fn_name="trace_return")
b.attach_kretprobe(event="sys_statfs", fn_name="trace_return")
b.attach_kretprobe(event="sys_newstat", fn_name="trace_return")

class Data(ct.Structure):
    _fields_ = [
        ("pid", ct.c_ulonglong),
        ("ts", ct.c_ulonglong),
        ("delta", ct.c_ulonglong),
        ("ret", ct.c_int),
        ("comm", ct.c_char * 16),
        ("fname", ct.c_char * 255)
    ]

# header
if args.timestamp:
    print("%-14s" % ("TIME(s)"), end="")
print("%-6s %-16s %4s %3s %s" % ("PID", "COMM", "FD", "ERR", "PATH"))

# process event
def print_event(cpu, data, size):
    event = ct.cast(data, ct.POINTER(Data)).contents

    print("%-6d %-16s %4d %3d %s" % (event.pid, event.comm, event.ret, event.ret, event.fname))

# loop with callback to print_event
b["events"].open_perf_buffer(print_event)
while 1:
    b.kprobe_poll()

