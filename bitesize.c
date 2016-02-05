/*
 * bitehist.c   Block I/O size histogram.
 *              For Linux, uses BCC, eBPF. See .py file.
 *
 * Copyright (c) 2015 Allan McAleavy
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of version 2 of the GNU General Public
 * License as published by the Free Software Foundation.
 *
 * 05-Feb-2016 Allan McAleavy
 */

#include <uapi/linux/ptrace.h>
#include <linux/blkdev.h>


typedef struct proc_key_t  {
    char name[TASK_COMM_LEN];
    u64 slot;
} disk_key_t;

struct val_t {
    char name[TASK_COMM_LEN];
};

BPF_HISTOGRAM(dist, struct proc_key_t);
BPF_HASH(commbyreq, struct request *, struct val_t);

int trace_pid_start(struct pt_regs *ctx, struct request *req)
{
    struct val_t val = {};
    if (bpf_get_current_comm(&val.name, sizeof(val.name)) == 0) {
        commbyreq.update(&req, &val);
    }
    return 0;
}


int do_count (struct pt_regs *ctx, struct request *req)
{
        struct val_t *valp;

    valp = commbyreq.lookup(&req);
    if ( valp ==  0)  {
       return 0;
    }

    if ( req->__data_len > 0 ) {
        struct proc_key_t key = {.slot = bpf_log2l(req->__data_len / 1024)};
        bpf_probe_read(&key.name, sizeof(key.name),valp->name);
        dist.increment(key);
    }
        return 0;
}
