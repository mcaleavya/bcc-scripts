BCC Scripts 
===========

<b> cachestat </b>

Show % cache read & write hit 

A collection of learning BCC. Examples taken from Brendan Gregg 

<pre>
USAGE: ./cachestat [-T] [ interval [count] ]

show Linux page cache hit/miss statistics

optional arguments:

  -T                    include timestamp on output
 


examples:
    ./cachestat             # run with default options of 5 seconds delay forever
    ./cachestat -T          # run with default options of 5 seconds delay forever with timestamps
    ./cachestat  1          # print every second hit/miss stats
    ./cachestat -T 1        # include timestamps with one second samples

</pre>


<pre>
# ./cachestat 1
    HITS   MISSES  DIRTIES READ_HIT% WRITE_HIT%   BUFFERS_MB  CACHED_MB
       0       58        0     0.0%   100.0%            0      11334
  146113        0        0   100.0%     0.0%            0      11334
  244143        0        0   100.0%     0.0%            0      11334
  216833        0        0   100.0%     0.0%            0      11334
  248209        0        0   100.0%     0.0%            0      11334
  205825        0        0   100.0%     0.0%            0      11334
  286654        0        0   100.0%     0.0%            0      11334
  275850        0        0   100.0%     0.0%            0      11334
  272883        0        0   100.0%     0.0%            0      11334
  261633        0        0   100.0%     0.0%            0      11334
  252826        0        0   100.0%     0.0%            0      11334
  235253       70        3   100.0%     0.0%            0      11335
  204946        0        0   100.0%     0.0%            0      11335
       0        0        0     0.0%     0.0%            0      11335
       0        0        0     0.0%     0.0%            0      11335
       0        0        0     0.0%     0.0%            0      11335

Above shows the reading of a 12GB file already cached in the OS page cache and again below with timestamps.

Command used to generate the activity
# dd if=/root/mnt2/testfile of=/dev/null bs=8192
1442795+0 records in
1442795+0 records out
11819376640 bytes (12 GB) copied, 3.9301 s, 3.0 GB/s

</pre>

<pre>
# ./cachestat -T 1
TIME         HITS   MISSES  DIRTIES READ_HIT% WRITE_HIT%   BUFFERS_MB  CACHED_MB
16:07:10        0        0        0     0.0%     0.0%            0      11336
16:07:11        0        0        0     0.0%     0.0%            0      11336
16:07:12   117849        0        0   100.0%     0.0%            0      11336
16:07:13   212558        0        0   100.0%     0.0%            0      11336
16:07:14   302559        1        0   100.0%     0.0%            0      11336
16:07:15   309230        0        0   100.0%     0.0%            0      11336
16:07:16   305701        0        0   100.0%     0.0%            0      11336
16:07:17   312754        0        0   100.0%     0.0%            0      11336
16:07:18   308406        0        0   100.0%     0.0%            0      11336
16:07:19   298185        0        0   100.0%     0.0%            0      11336
16:07:20   236128        0        0   100.0%     0.0%            0      11336
16:07:21   257616        0        0   100.0%     0.0%            0      11336
16:07:22   179792        0        0   100.0%     0.0%            0      11336

Command used to generate the activity
# dd if=/root/mnt2/testfile of=/dev/null bs=8192
1442795+0 records in
1442795+0 records out
11819376640 bytes (12 GB) copied, 3.9301 s, 3.0 GB/s.
</pre>

