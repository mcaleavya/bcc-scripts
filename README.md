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
[root@localhost bcc]# ./cachestat
    HITS   MISSES  DIRTIES    RATIO   BUFFERS_MB  CACHED_MB
     -14        0       14   100.0%            0         70
       0        0        0     0.0%            0         70
      65      512        0    11.3%            0         72
     499      264        0    65.4%            0         73
       0        0        0     0.0%            0         73
</pre>

<pre>
[root@localhost bcc]# ./cachestat -T 
TIME         HITS   MISSES  DIRTIES    RATIO   BUFFERS_MB  CACHED_MB
13:47:28        0        0        0     0.0%            0         73
13:47:29      576       65        0    89.9%            0         74
13:47:30        0        0        0     0.0%            0         74
13:47:31        0        0        0     0.0%            0         74
13:47:32      627        0        0   100.0%            0         74
13:47:33        0        0        0     0.0%            0         74
13:47:34       97      640        0    13.2%            0         76
13:47:35      541       72        0    88.3%            0         76
13:47:36        0        0        0     0.0%            0         76
13:47:37        0        0        0     0.0%            0         76

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
