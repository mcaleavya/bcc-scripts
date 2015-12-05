BCC Scripts 
===========

<b> cachestat </b>

Show cache hit/miss ratios

A collection of learning BCC. Examples taken from Brendan Gregg 

<pre>
usage: cachestat [-h] [-i INTERVAL] [-T] [-L]

show Linux page cache hit/miss statistics

optional arguments:
  -h, --help            show this help message and exit
  -i INTERVAL, --interval INTERVAL
                        summary interval, seconds
  -T, --timestamp       include timestamp on output
  -L, --latency         include latency historgrams on output experimental

examples:
    ./cachestat -i 1        # print every second hit/miss stats
    ./cachestat -L -i 1     # show latency for each function access
    ./cachestat -T -i 1     # include timestamps

</pre>


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

<pre>
[root@henky bcc]# ./cachestat -L
Latency Histogram for Page Cache Function Access

Function = add_to_page_cache_lru
     usecs               : count     distribution
         0 -> 1          : 50       |****************************************|
         2 -> 3          : 22       |*****************                       |
         4 -> 7          : 8        |******                                  |

Function = account_page_dirtied
     usecs               : count     distribution
         0 -> 1          : 79       |****************************************|
         2 -> 3          : 1        |                                        |

Function = mark_page_accessed
     usecs               : count     distribution
         0 -> 1          : 723      |****************************************|
         2 -> 3          : 3        |                                        |
Detaching...
</pre>
