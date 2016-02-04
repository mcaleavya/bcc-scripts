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

enum stat_types {
        S_MAXSTAT
};

struct key_t {
        u64 ip;
        u64 tp;
        char disk_name[DISK_NAME_LEN];
        u64 rblk;
        u64 wblk;
        u64 wsvc;
        u64 rsvc;
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
        u64 delta;
        u64 *tsp;
        int *b;

        key.ip = ctx->ip;

        tsp = start.lookup(&req);
        if (tsp == 0) {
        // missed tracing issue
        return 0;
        }

        delta = (bpf_ktime_get_ns() - *tsp) /1000000;

        if (req->cmd_flags & REQ_WRITE) {
        key.tp=1;
          a=req->__data_len;
          key.wblk=a;
          key.wsvc = delta;
          bpf_probe_read(&key.disk_name,sizeof(key.disk_name),req->rq_disk->disk_name);
        } else {
        key.tp=2;
          a=req->__data_len;
          key.rblk=a;
          key.rsvc=delta;
          bpf_probe_read(&key.disk_name,sizeof(key.disk_name),req->rq_disk->disk_name);
        }
        start.delete(&req);
        val = counts.lookup_or_init(&key, &reads);
        (*val)++;
        return 0;
}
