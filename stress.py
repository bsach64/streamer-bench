import time
import os
TARGET_RAM_GB = 0.5  # Set this to your desired memory usage
def hybrid_load(shared_size): # Allocate a large bytearray (this takes up the RAM)
    data = bytearray(shared_size)
    print(f"Process {os.getpid()} allocated {shared_size / 1024**2:.2f} MB")

    while True:
        # This forces the CPU to constantly fetch from RAM. We use a slice and a simple sum to keep the CPU pinned.
        _ = sum(data[::1000])

if __name__ == "__main__":
    bytes_per_core = int((TARGET_RAM_GB * 1024**3))
    print("Press Ctrl+C to stop.")
    try:
        hybrid_load(bytes_per_core)
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping workload...")
