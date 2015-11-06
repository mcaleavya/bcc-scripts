#!/usr/bin/python
#!/usr/bin/python
#
# cachestat     Count cache kernel function calls.
#               For Linux, uses BCC, eBPF. See .c file.
#
# USAGE: cachestat
#
# Taken from funccount by Brendan Gregg , this is a rewrite of cachestat from perf to bcc
# https://github.com/brendangregg/perf-tools/blob/master/fs/cachestat
#
# Copyright (c) 2015 Brendan Gregg.
# Licensed under the Apache License, Version 2.0 (the "License")
#
# 09-Sep-2015   Brendan Gregg   Created this.
# 06-Nov-2015   Allan McAleavy 
# 

from __future__ import print_function
from bcc import BPF
from time import sleep, strftime
import argparse
import signal
import re	

# Set global variables to defaults, I have set total and hits to 1 to avoid divide by zero errors.A
# 
mpa=0
mbd=0
apcl=0
apd=0
total=1
misses=0
hits=1

# load BPF program
bpf_text = """
#include <uapi/linux/ptrace.h>
struct key_t {
        u64 ip;
};
BPF_HASH(counts, struct key_t);
int trace_count(struct pt_regs *ctx) {
        struct key_t key = {};
        u64 zero = 0, *val;
        key.ip = ctx->ip;
        val = counts.lookup_or_init(&key, &zero);
        (*val)++;
        return 0;
}
"""
b = BPF(text=bpf_text)
b.attach_kprobe(event="add_to_page_cache_lru", fn_name="trace_count")
b.attach_kprobe(event="mark_page_accessed", fn_name="trace_count")
b.attach_kprobe(event="account_page_dirtied", fn_name="trace_count")
b.attach_kprobe(event="mark_buffer_dirty", fn_name="trace_count")

# header
print("%8s %8s %8s %8s" % ("HITS","MISSES","DIRTIES","RATIO"))
exiting=0


while (1):
        try:
                sleep(1)
        except KeyboardInterrupt:
                exiting=1
                # as cleanup can take many seconds, trap Ctrl-C:
                signal.signal(signal.SIGINT, signal_ignore)


        #print("%-16s %-26s %8s" % ("ADDR", "FUNC", "COUNT"))
        counts = b.get_table("counts")
        for k, v in sorted(counts.items(), key=lambda counts: counts[1].value):
                #print("%-26s %8d" % (b.ksym(k.ip), v.value))
                if re.match ('mark_page_accessed',b.ksym(k.ip)) is not None:
		   mpa=v.value
		   if mpa < 0 : mpa = 0

	        if re.match('mark_buffer_dirty',b.ksym(k.ip)) is not None:
	           mbd=v.value
		   if mbd < 0 : mdb = 0	

		if re.match('add_to_page_cache_lru',b.ksym(k.ip)) is not None:
	    	   apcl=v.value
		   if apcl < 0 : apcl = 0

		if re.match('account_page_dirtied',b.ksym(k.ip)) is not None:
	           apd=v.value
  		   if apd < 0 : apd = 0

                total = mpa - mbd
   	        misses = apcl - apd 

	        if misses < 0: 
                    misses =  0 
	
        counts.clear()
	hits = total - misses
	ratio = 100 * hits / total 
	#print ("hits total %d %d " % (hits , total))
	print ("mpa:%d mbd:%d apcl:%d apd:%d total:%d misses:%d hits:%d ratio:%d" % (mpa,mbd,apcl,apd,total,misses,hits,ratio))        
	print("%8d %8d %8d %7.1f%%" % (hits,misses,mbd,ratio))
        mbd=0
        apcl=0
        apd=0
        total=1
        misses=0
        hits=1


        if exiting:
                print("Detaching...")
                exit()

