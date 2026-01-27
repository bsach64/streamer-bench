## Test Environment Info

Ran all tests on a `g6.2xlarge` ec2 instance.

```
Following Specs:
CPU:
CPU(s):                                  8
On-line CPU(s) list:                     0-7
Model name:                              AMD EPYC 7R13 Processor
BIOS Model name:                         AMD EPYC 7R13 Processor  CPU @ 2.6GHz

Memory: 30Gi

+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 570.211.01             Driver Version: 570.211.01     CUDA Version: 12.8     |
|-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  NVIDIA L4                      Off |   00000000:31:00.0 Off |                    0 |
| N/A   35C    P0             29W /   72W |       0MiB /  23034MiB |      4%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+
```

**Network Speeds**

```
$ speedtest
Retrieving speedtest.net configuration...
Testing from Amazon.com (54.152.26.168)...
Retrieving speedtest.net server list...
Selecting best server based on ping...
Hosted by Shentel (Ashburn, VA) [0.81 km]: 1.348 ms
Testing download speed................................................................................
Download: 2155.12 Mbit/s
Testing upload speed......................................................................................................
Upload: 1809.48 Mbit/s
```

**Disk Speeds**

| Operation Type    | Sub-test      | Throughput (kB/sec) | Throughput (MB/sec) |
| :---------------- | :------------ | :------------------ | :------------------ |
| Sequential Writes | Initial Write | 629,524.62          | ~614.77 MB/s        |
| Sequential Writes | Rewrite       | 867,051.62          | ~846.73 MB/s        |
| Random Reads      | Random Read   | 642,434.19          | ~627.38 MB/s        |
| Random Writes     | Random Write  | 509,545.06          | ~497.60 MB/s        |

Based on the `iozone3` benchmark whose output can be found in `disk_speeds`.

All tests were run 5 times.

## GPU C/R Results

### Minimum Times

![GPU Minimum Times](plots/stream_benchmarks_gpu_min.png)

### Median Times
![GPU Median Times](plots/stream_benchmarks_gpu_median.png)

## CPU C/R Results

### Minimum Times

![CPU Minimum Times](plots/stream_benchmarks_cpu_min.png)

### Median Times
![CPU Minimum Times](plots/stream_benchmarks_cpu_median.png)
