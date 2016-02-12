#!/usr/bin/python
# @lint-avoid-python-3-compatibility-imports
#
# biosnoop  Trace block device I/O and print details including issuing PID.
#       For Linux, uses BCC, eBPF.
#
# This uses in-kernel eBPF maps to cache process details (PID and comm) by I/O
# request, as well as a starting timestamp for calculating I/O latency.
#
# Copyright (c) 2015 Brendan Gregg.
# Licensed under the Apache License, Version 2.0 (the "License")
#
# 16-Sep-2015   Brendan Gregg   Created this.
# 11-Feb-2016   Allan McAleavy  updated for BPF_PERF_OUTPUT


from __future__ import print_function
from bcc import BPF
import ctypes as ct

# load BPF program
b = BPF(text="""
#include <uapi/linux/ptrace.h>
#include <linux/blkdev.h>

struct val_t {
    u32 pid;
    char name[TASK_COMM_LEN];
};

struct key_t {
    u32 pid;
    u64 rwflag;
    u64 delta;
    u64 sector;
    u64 len; 
    char disk_name[DISK_NAME_LEN];
    char name[16];
};


BPF_HASH(start, struct request *);
BPF_HASH(infobyreq, struct request *, struct val_t);
BPF_PERF_OUTPUT(events);

// cache PID and comm by-req
int trace_pid_start(struct pt_regs *ctx, struct request *req)
{
    struct val_t val = {};

    if (bpf_get_current_comm(&val.name, sizeof(val.name)) == 0) {
        val.pid = bpf_get_current_pid_tgid();
        infobyreq.update(&req, &val);
    }
    return 0;
}

// time block I/O
int trace_req_start(struct pt_regs *ctx, struct request *req)
{
    u64 ts;

    ts = bpf_ktime_get_ns();
    start.update(&req, &ts);

    return 0;
}

// output
int trace_req_completion(struct pt_regs *ctx, struct request *req)
{
    u64 *tsp, delta;
    u32 *pidp = 0;
    struct val_t *valp;
    struct key_t key ={};

    // fetch timestamp and calculate delta
    tsp = start.lookup(&req);
    if (tsp == 0) {
        // missed tracing issue
        return 0;
    }
    key.delta = bpf_ktime_get_ns() - *tsp;

    //
    // Fetch and output issuing pid and comm.
    // As bpf_trace_prink() is limited to a maximum of 1 string and 2
    // integers, we'll use more than one to output the data.
    //

    valp = infobyreq.lookup(&req);
      
    if (valp == 0) {
	key.len = req->__data_len;
	strcpy(key.name,"?");
    } else {
	key.pid = valp->pid;
        key.len = req->__data_len;
	key.sector = req->__sector;
	bpf_probe_read(&key.name, sizeof(key.name), valp->name);
	bpf_probe_read(&key.disk_name, sizeof(key.disk_name), req->rq_disk->disk_name);
    }

    // output remaining details

    if (req->cmd_flags & REQ_WRITE) {
        key.rwflag=1;	
    } else {
	key.rwflag=0;
    }
    events.perf_submit(ctx,&key,sizeof(key));
    start.delete(&req);
    infobyreq.delete(&req);

    return 0;
}
""", debug=0)
b.attach_kprobe(event="blk_account_io_start", fn_name="trace_pid_start")
b.attach_kprobe(event="blk_start_request", fn_name="trace_req_start")
b.attach_kprobe(event="blk_mq_start_request", fn_name="trace_req_start")
b.attach_kprobe(event="blk_account_io_completion",
    fn_name="trace_req_completion")


TASK_COMM_LEN = 16  # linux/sched.h
DISK_NAME_LEN = 32  # linux/genhd.h

class Data(ct.Structure):
    _fields_ = [
        ("pid", ct.c_ulonglong),
        ("rwflag", ct.c_ulonglong),
        ("delta", ct.c_ulonglong),
        ("sector", ct.c_ulonglong),
        ("len", ct.c_ulonglong),
        ("disk_name", ct.c_char * DISK_NAME_LEN ),
        ("name", ct.c_char * TASK_COMM_LEN)
    ]
# header
print("%-14s %-14s %-6s %-7s %-2s %-9s %-7s %7s" % ("TIME(s)", "COMM", "PID",
    "DISK", "T", "SECTOR", "BYTES", "LAT(ms)"))
start_ts = 0
rwflg = ""

# format output

# process event
def print_event(cpu, data, size):
    event = ct.cast(data, ct.POINTER(Data)).contents
    if event.rwflag == 1:
       rwflg = "W"
    if event.rwflag == 0:
       rwflg = "R"
    
    print("%-14.9f %-14.14s %-6s %-7s %-2s %-9s %-7s %7.2f" % (
        start_ts,event.name , event.pid, event.disk_name, rwflg, event.sector,
        event.len,event.delta/100000))
    

b["events"].open_perf_buffer(print_event)
while 1:
  b.kprobe_poll() 
