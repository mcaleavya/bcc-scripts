/*
 * biostat.c    count I/O 
 *              For Linux, uses BCC, eBPF. See the Python front-end.
 *
 * USAGE: biostat.py
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of version 2 of the GNU General Public
 * License as published by the Free Software Foundation.
 *
 */

#include <uapi/linux/ptrace.h>
#include <linux/blkdev.h>

struct key_t {
        u64 ip;
        u64 tp;
        char disk_name[DISK_NAME_LEN];
        u64 rblk;
        u64 wblk;
};

//BPF_TABLE("hash", struct key_t, u64, counts, 256);
BPF_HASH(counts,struct key_t);
BPF_HASH(start, struct request *);

// time block I/O
int trace_req_start(struct pt_regs *ctx, struct request *req)
{
    u64 ts;

    ts = bpf_ktime_get_ns();
    start.update(&req, &ts);

    return 0;
}

int do_count(struct pt_regs *ctx , struct request *req) {
        struct key_t key = {};
        u64 zero = 0, *val, *val2;
        u64 reads = 0;
        unsigned int a;

        key.ip = ctx->ip;

        if (req->cmd_flags & REQ_WRITE) {
        key.tp=1;
          a=req->__data_len;
          key.wblk=a;
          bpf_probe_read(&key.disk_name,sizeof(key.disk_name),req->rq_disk->disk_name);
        } else {
        key.tp=2;
          a=req->__data_len;
          key.rblk=a;
          bpf_probe_read(&key.disk_name,sizeof(key.disk_name),req->rq_disk->disk_name);
        }
           val = counts.lookup_or_init(&key, &reads);
           (*val)++;
        return 0;
}
