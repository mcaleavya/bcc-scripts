BCC Scripts 
===========

<b> cachestat </b>

Show cache hit/miss ratios

A collection of learning BCC. Examples taken from Brendan Gregg 

<pre>
[root@localhost ~]# ./cachestat
    HITS   MISSES  DIRTIES    RATIO   BUFFERS_MB  CACHED_MB
       1        0        0   100.0%            0         85
       1        0        0   100.0%            0         85
       1        0        0   100.0%            0         85
       1        0        0   100.0%            0         85
</pre>

<pre>
[root@localhost ~]# ./cachestat -T
TIME         HITS   MISSES  DIRTIES    RATIO   BUFFERS_MB  CACHED_MB
13:57:21        1        0        0   100.0%            0         85
13:57:22        1        0        0   100.0%            0         85
13:57:23        1        0        0   100.0%            0         85
13:57:24        1        0        0   100.0%            0         85
13:57:25      -18        0       18   100.0%            0         64
13:57:26        1        0        0   100.0%            0         64
13:57:27        1        0        0   100.0%            0         64
13:57:28        1        0        0   100.0%            0         64
13:57:29     -274     1048     1015   -36.0%            0         72
13:57:30      775        0     1015   100.0%            0         76
13:57:31      754        0     1015   100.0%            0         80
13:57:32      775        0     1015   100.0%            0         84
13:57:33      791        0     1015   100.0%            0         88

</pre>
