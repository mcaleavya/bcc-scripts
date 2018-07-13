#!/usr/bin/python
# @lint-avoid-python-3-compatibility-imports
#
# qos     implement a dynamic qos for using cgroups
#         For Linux, uses BCC, eBPF.
#
# USAGE: qos.py [-h] [-qc] [--max] [interval]
# requires a file name qos_setup which can changed with qosfile
# file has format maj:min IOPS
# i.e.  8:0 40000
# Copyright (c) 2018 Allan McAleavy
# Licensed under the Apache License, Version 2.0 (the "License")

from __future__ import print_function
from bcc import BPF
from time import sleep, strftime
import argparse
import signal
import math
import collections


# arguments
examples = """examples:
    ./qos            # block device I/O QOS, 1 second refresh
    ./qos --max 5000 # set max IOP limit for average I/O size lookup
    ./qos 5          # 5 second summaries
    ./qos --qc 5     # check for qos every 5 seconds
"""
parser = argparse.ArgumentParser(
    description="Block device (disk) I/O by process and QOS",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog=examples)
parser.add_argument("-max", "--max", default=4000,
            help="maximum IOPS")
parser.add_argument("interval", nargs="?", default=1,
    help="output interval, in seconds")
parser.add_argument("count", nargs="?", default=99999999,
    help="number of outputs")
parser.add_argument("-qc", "--qc", default=5,
                    help="QOS checktime")
parser.add_argument("--ebpf", action="store_true",
    help=argparse.SUPPRESS)
args = parser.parse_args()
interval = int(args.interval)
countdown = int(args.count)
checktime = int(args.qc)

# linux stats
diskstats = "/proc/diskstats"
rfile = "/sys/fs/cgroup/blkio/blkio.throttle.read_iops_device"
wfile = "/sys/fs/cgroup/blkio/blkio.throttle.write_iops_device"
qosfile = "/root/bcc/tools/qos_setup"

# signal handler
def signal_ignore(signal, frame):
    print()

def write_qos(dsk, typ, max_iops, sleepcnt):
    if sleepcnt > checktime:
        reload_qos(dsk)
        if typ == "W":
            with open(wfile, "w") as tf:
                tf.write("%s %d" % (dsk, max_iops))
                tf.close()
        if typ == "R":
            with open(rfile, "w") as tf:
                tf.write("%s %d" % (dsk, max_iops))
                tf.close()

# load qos settings at start
diskqos = {}
with open(qosfile) as stats:
    for line in stats:
        a = line.split()
        diskqos[str(a[0])] = a[1]

def reload_qos(dsk):
    with open(qosfile) as stats:
        for line in stats:
            a = line.split()
            diskqos[str(a[0])] = a[1]

def do_qos(avg, iops, typ, dsk, sleepcnt):
    if dsk in diskqos:
        max_iops = int(diskqos[dsk])
    else:
        max_iops = int(args.max_iops)
    costs = {4:100, 8:160, 16:270, 32:500, 64:1000, 128:1950, 256:3900, 512:7600, 1024:15000}
    od = collections.OrderedDict(sorted(costs.items()))
    average_iopsize = float(avg) / 1024
    hbsize = 0
    if average_iopsize >= 1:
        hbsize = int(pow(2, math.ceil(math.log(average_iopsize, 2))))
    if hbsize < 4:
        hbsize = 4
    lbsize = (hbsize / 2)
    if lbsize < 4:
        lbsize = 4
    lbcost = od[lbsize]
    hbcost = od[hbsize]

    costep = float(hbcost - lbcost) / float(lbsize)
    curcost = ((average_iopsize - lbsize) * costep) + lbcost
    max_iops = (od[4] / float(curcost) * max_iops)
    write_qos(dsk, typ, max_iops, sleepcnt)
    return max_iops


# load BPF program
bpf_text = """
#include <uapi/linux/ptrace.h>
#include <linux/blkdev.h>

// the key for the output summary
struct info_t {
    int rwflag;
    int major;
    int minor;
};

// the value of the output summary
struct val_t {
    u64 bytes;
    u32 io;
};

BPF_HASH(counts, struct info_t, struct val_t);

int trace_req_start(struct pt_regs *ctx, struct request *req)
{

    struct val_t *valp, zero = {};
    struct info_t info = {};
    info.major = req->rq_disk->major;
    info.minor = req->rq_disk->first_minor;

#ifdef REQ_WRITE
    info.rwflag = !!(req->cmd_flags & REQ_WRITE);
#elif defined(REQ_OP_SHIFT)
    info.rwflag = !!((req->cmd_flags >> REQ_OP_SHIFT) == REQ_OP_WRITE);
#else
    info.rwflag = !!((req->cmd_flags & REQ_OP_MASK) == REQ_OP_WRITE);
#endif
    if( info.major > 0 )
    {
       valp = counts.lookup_or_init(&info, &zero);
       valp->bytes += req->__data_len;
       valp->io++;
    }
    return 0;
}
"""

if args.ebpf:
    print(bpf_text)
    exit()

b = BPF(text=bpf_text)
b.attach_kprobe(event="blk_start_request", fn_name="trace_req_start")
b.attach_kprobe(event="blk_mq_start_request", fn_name="trace_req_start")

print('Tracing... Output every %d secs. Hit Ctrl-C to end' % interval)

disklookup = {}
with open(diskstats) as stats:
    for line in stats:
        a = line.split()
        disklookup[a[0] + ":" + a[1]] = a[2]

exiting = 0
sleepcnt = 0
diskname = "???"
wiops = 0
riops = 0
ravg = 0
wavg = 0
rqos = 0
wqos = 0
wbytes = 0
rbytes = 0
print("%-8s %-5s %-8s %-8s %-8s %-8s %-8s %-8s %-8s %-8s" %
     ("TIME", "DISK", "RIOPS", "R MB/s", "R_AvgIO", "R_QOS",
         "WIOPS", "W_AvgIO", "W MB/s", "W_QOS"))
while 1:
    try:
        sleep(interval)
    except KeyboardInterrupt:
        exiting = 1

    counts = b.get_table("counts")
    line = 0
    for k, v in sorted(counts.items(), key=lambda counts: counts[1].bytes):
        disk = str(k.major) + ":" + str(k.minor)
        if disk in disklookup:
            diskname = disklookup[disk]
        else:
            diskname = "???"

        if v.io and v.bytes >= 1 and diskname is not "???":
            if k.rwflag == 1:
                wiops = v.io
                wavg = (v.bytes / wiops)
                wbytes = v.bytes
                wqos = do_qos(wavg, wiops, "W", disk, sleepcnt)
            else:
                riops = v.io
                ravg = (v.bytes / riops)
                rbytes = v.bytes
                rqos = do_qos(ravg, riops, "R", disk, sleepcnt)

    print("%-8s %-5s %-8d %-8d %-8d %-8d %-8d %-8d %-8d %-8d" %
         (strftime("%H:%M:%S"), diskname, riops, rbytes / 1048576, ravg / 1024,
             rqos, wiops, wavg / 1024, wbytes / 1048576, wqos))

    counts.clear()
    wiops = 0
    riops = 0
    ravg = 0
    wavg = 0
    rqos = 0
    wqos = 0
    wbytes = 0
    rbytes = 0
    if sleepcnt > checktime:
        sleepcnt = 0
    else:
        sleepcnt = sleepcnt + 1
    countdown -= 1
    if exiting or countdown == 0:
        print("Detaching...")
        exit()
