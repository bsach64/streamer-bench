# Old vs New Graphs

- `cuda_stress` has an approximate checkpoint size of `~700MB`; `stress_py` has an approximate checkpoint size of `~500MB`.
- "Without memory limit" refers to Streamer behavior before the memory-limit change (pre-change baseline).

- `GPU == cuda_stress`
- `CPU == stress_py`

## GPU CEDANA STORAGE STREAMS = 2

![GPU Cedana Streams 2](./cedana_cuda_stress_checkpoint_restore_grouped_2streams.png)

## GPU CEDANA STORAGE STREAMS = 4

![GPU Cedana Streams 4](./cedana_cuda_stress_checkpoint_restore_grouped_4streams.png)

## GPU CEDANA STORAGE STREAMS = 8

![GPU Cedana Streams 8](./cedana_cuda_stress_checkpoint_restore_grouped_8streams.png)

## CPU CEDANA STORAGE STREAMS = 2

![CPU Cedana Streams 2](./cedana_stress_py_checkpoint_restore_grouped_2streams.png)

## CPU CEDANA STORAGE STREAMS = 4

![CPU Cedana Streams 4](./cedana_stress_py_checkpoint_restore_grouped_4streams.png)

## CPU CEDANA STORAGE STREAMS = 8

![CPU Cedana Streams 8](./cedana_stress_py_checkpoint_restore_grouped_8streams.png)

## GPU LOCAL STREAMS = 2

![GPU Local Streams 2](./local_cuda_stress_checkpoint_restore_grouped_2streams.png)

## GPU LOCAL STREAMS = 4

![GPU Local Streams 4](./local_cuda_stress_checkpoint_restore_grouped_4streams.png)

## GPU LOCAL STREAMS = 8

![GPU Local Streams 8](./local_cuda_stress_checkpoint_restore_grouped_8streams.png)

## CPU LOCAL STREAMS = 2

![CPU Local Streams 2](./local_stress_py_checkpoint_restore_grouped_2streams.png)

## CPU LOCAL STREAMS = 4

![CPU Local Streams 4](./local_stress_py_checkpoint_restore_grouped_4streams.png)

## CPU LOCAL STREAMS = 8

![CPU Local Streams 8](./local_stress_py_checkpoint_restore_grouped_8streams.png)
