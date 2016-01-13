BCC Scripts 
===========

<b> cachestat </b>

Show % cache read & write hit 

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
    HITS   MISSES  DIRTIES READ HIT% WRITE HIT%   BUFFERS_MB  CACHED_MB
       0        0        0     0.0%     0.0%            0        134
       0        0        0     0.0%     0.0%            0        134
       0        0        0     0.0%     0.0%            0        134
       0        0        0     0.0%     0.0%            0        134
     709        0        0   100.0%     0.0%            0        126
     241        0        0   100.0%     0.0%            0        126
    1666     3332     1666     0.0%    33.3%            0        132
     898      768      384    30.9%    23.0%            0        134
       0        0        0     0.0%     0.0%            0        134
       0        0        0     0.0%     0.0%            0        134
       0        0        0     0.0%     0.0%            0        134
</pre>

<pre>
[root@localhost bcc]# ./cachestat -T 
TIME         HITS   MISSES  DIRTIES READ HIT% WRITE HIT%   BUFFERS_MB  CACHED_MB
21:53:49        0        0        0     0.0%     0.0%            0        134
21:53:50        0        0        0     0.0%     0.0%            0        134
21:53:51      708        0        0   100.0%     0.0%            0        126
21:53:52     1916     3832     1916     0.0%    33.3%            0        133
21:53:53      619      268      134    54.7%    15.1%            0        134
21:53:54      720        0        0   100.0%     0.0%            0        126
21:53:55      241        0        0   100.0%     0.0%            0        126
21:53:56     1734     3468     1734     0.0%    33.3%            0        132
21:53:57      818      632      316    34.6%    21.8%            0        134
21:53:58        0        0        0     0.0%     0.0%            0        134
21:53:59        0        0        0     0.0%     0.0%            0        134

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
