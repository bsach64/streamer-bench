#!/bin/bash

# Cedana Benchmark Script
# Captures checkpoint, restore, and total timing data for different compression methods and stream counts

set -e

# Configuration
RUNS=${RUNS:-1}  # Number of runs per test (default: 1)
OUTPUT_FILE="timing_results.csv"
SYSTEM_INFO_FILE="system_info.txt"
JOB_BASE="test-job-$(date +%s)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if stress.py exists
if [ ! -f "stress.py" ]; then
    echo -e "${RED}Error: stress.py not found in current directory${NC}"
    exit 1
fi

# Check if cedana daemon is running
if ! pgrep -f "cedana daemon" > /dev/null; then
    echo -e "${YELLOW}Starting cedana daemon...${NC}"
    make cedana start
    sleep 3
fi

# Capture system information
capture_system_info() {
    echo "=== System Information ===" > "$SYSTEM_INFO_FILE"
    echo "Timestamp: $(date -Iseconds)" >> "$SYSTEM_INFO_FILE"
    echo "" >> "$SYSTEM_INFO_FILE"

    echo "=== Hardware Information ===" >> "$SYSTEM_INFO_FILE"
    echo "CPU:" >> "$SYSTEM_INFO_FILE"
    if command -v lscpu >/dev/null 2>&1; then
        lscpu | grep -E "(Model name|CPU\(s\)|Thread|Core|Socket|MHz)" >> "$SYSTEM_INFO_FILE"
    else
        cat /proc/cpuinfo | grep -E "(processor|model name|cpu MHz)" | head -10 >> "$SYSTEM_INFO_FILE"
    fi
    echo "" >> "$SYSTEM_INFO_FILE"

    echo "Memory:" >> "$SYSTEM_INFO_FILE"
    if command -v free >/dev/null 2>&1; then
        free -h >> "$SYSTEM_INFO_FILE"
    else
        cat /proc/meminfo | head -10 >> "$SYSTEM_INFO_FILE"
    fi
    echo "" >> "$SYSTEM_INFO_FILE"

    echo "Storage:" >> "$SYSTEM_INFO_FILE"
    df -h . >> "$SYSTEM_INFO_FILE"
    if command -v lsblk >/dev/null 2>&1; then
        echo "" >> "$SYSTEM_INFO_FILE"
        lsblk >> "$SYSTEM_INFO_FILE"
    fi
    echo "" >> "$SYSTEM_INFO_FILE"

    echo "=== Software Environment ===" >> "$SYSTEM_INFO_FILE"
    echo "OS:" >> "$SYSTEM_INFO_FILE"
    if [ -f /etc/os-release ]; then
        cat /etc/os-release | grep -E "(NAME|VERSION)" >> "$SYSTEM_INFO_FILE"
    else
        uname -a >> "$SYSTEM_INFO_FILE"
    fi
    echo "" >> "$SYSTEM_INFO_FILE"

    echo "Kernel: $(uname -r)" >> "$SYSTEM_INFO_FILE"
    echo "" >> "$SYSTEM_INFO_FILE"

    echo "CRIU:" >> "$SYSTEM_INFO_FILE"
    if command -v criu >/dev/null 2>&1; then
        criu --version | head -1 >> "$SYSTEM_INFO_FILE"
    else
        echo "CRIU not found" >> "$SYSTEM_INFO_FILE"
    fi
    echo "" >> "$SYSTEM_INFO_FILE"

    echo "Cedana:" >> "$SYSTEM_INFO_FILE"
    if command -v cedana >/dev/null 2>&1; then
        cedana --version 2>/dev/null || echo "Version command failed" >> "$SYSTEM_INFO_FILE"
    else
        echo "Cedana not found in PATH" >> "$SYSTEM_INFO_FILE"
    fi
    echo "" >> "$SYSTEM_INFO_FILE"

    echo "=== Runtime Context ===" >> "$SYSTEM_INFO_FILE"
    echo "System Load:" >> "$SYSTEM_INFO_FILE"
    uptime >> "$SYSTEM_INFO_FILE"
    echo "" >> "$SYSTEM_INFO_FILE"

    echo "Available Memory:" >> "$SYSTEM_INFO_FILE"
    free -h | grep "Mem:" >> "$SYSTEM_INFO_FILE"
    echo "" >> "$SYSTEM_INFO_FILE"

    echo "Power Settings:" >> "$SYSTEM_INFO_FILE"
    if command -v cpupower >/dev/null 2>&1; then
        cpupower frequency-info | grep -E "(governor|min|max)" || echo "Unable to get CPU power info" >> "$SYSTEM_INFO_FILE"
    else
        echo "cpupower not available" >> "$SYSTEM_INFO_FILE"
    fi
}

# Capture system information at the start
echo -e "${YELLOW}Capturing system information...${NC}"
capture_system_info
echo -e "${GREEN}System info saved to: $SYSTEM_INFO_FILE${NC}"
echo ""

echo -e "${GREEN}Starting Cedana benchmarks...${NC}"
echo "Job base: $JOB_BASE"
echo "Runs per test: $RUNS"
echo "Output file: $OUTPUT_FILE"
echo ""

# Create CSV header
echo "compression,streams,checkpoint_time,restore_time,total_time,timestamp,run_number" > "$OUTPUT_FILE"

# Test configurations
COMPRESSIONS=("none" "tar" "gzip" "lz4" "zlib")
# COMPRESSIONS=("none")
STREAM_COUNTS=(0 2 4 8)
# STREAM_COUNTS=(0 4)
# CEDANA_CHECKPOINT_DIR=/home/bsach/Code/dumps/

# Function to extract real time from time -p output
extract_time() {
    local time_output="$1"
    if [[ -z "$time_output" ]]; then
        echo ""
        return 1
    fi
    local time=$(echo "$time_output" | awk '/^real/ {print $2}')
    # Validate that it's a valid number
    if [[ "$time" =~ ^[0-9]+(\.[0-9]+)?$ ]]; then
        echo "$time"
    else
        echo ""
        return 1
    fi
}

# Function to run a single test
run_test() {
    local compression="$1"
    local streams="$2"
    local run_num="$3"

    echo "Testing: $compression compression with $streams streams (run $run_num/$RUNS)"

    # Create unique job name for this run
    local job_name="${JOB_BASE}-${compression}-${streams}-run${run_num}"
    local dir_path="s3://bhavik-streamer-bench/${JOB_NAME}"

    # Start the managed job
    echo "  Starting job: $job_name"
    cedana run process python3 stress.py --jid "$job_name"
    sleep 1

    # Make sure the job is running
    if ! cedana job list | grep -q "$job_name"; then
        echo -e "${RED}Error: Failed to start job $job_name${NC}"
        return 1
    fi

    # Checkpoint timing
    local checkpoint_cmd="cedana dump job $job_name --compression $compression --streams $streams --dir $dir_path"
    # local checkpoint_cmd="cedana dump job $job_name --compression $compression --streams $streams"
    local checkpoint_output
    echo "STARTING CHECKPOINT"
    checkpoint_output=$({ time -p $checkpoint_cmd; } 2>&1)
    echo "FINISHED CHECKPOINT"
    local checkpoint_time
    checkpoint_time=$(extract_time "$checkpoint_output")

    # Validate checkpoint time
    if [[ -z "$checkpoint_time" ]]; then
        echo "ERROR: Failed to extract checkpoint time from: $checkpoint_output" >&2
        cedana job kill "$job_name" 2>/dev/null || true
        return 1
    fi

    # Restore timing
    local restore_cmd="cedana restore job $job_name"
    local restore_output
    echo "STARTING RESTORE"
    restore_output=$({ time -p $restore_cmd; } 2>&1)
    echo "FINISHED RESTORE"
    local restore_time
    restore_time=$(extract_time "$restore_output")

    # Validate restore time
    if [[ -z "$restore_time" ]]; then
        echo "ERROR: Failed to extract restore time from: $restore_output" >&2
        cedana job kill "$job_name" 2>/dev/null || true
        return 1
    fi

    # Calculate total time
    local total_time
    if [[ -n "$checkpoint_time" && -n "$restore_time" ]]; then
        total_time=$(echo "$checkpoint_time + $restore_time" | bc -l)
    else
        echo "ERROR: Failed to extract timing data - checkpoint: '$checkpoint_time', restore: '$restore_time'" >&2
        # Cleanup job on error
        cedana job kill "$job_name" 2>/dev/null || true
        return 1
    fi

    # Get timestamp
    local timestamp
    timestamp=$(date -Iseconds)

    # Save to CSV
    echo "$compression,$streams,$checkpoint_time,$restore_time,$total_time,$timestamp,$run_num" >> "$OUTPUT_FILE"

    printf "  Checkpoint: %s s, Restore: %s s, Total: %s s\n" "$checkpoint_time" "$restore_time" "$total_time"

    # Cleanup this job
    cedana job kill "$job_name" 2>/dev/null || true
    cedana job delete "$job_name" 2>/dev/null || true
    rm -rf /tmp/dump-process-*

    # Wait between runs
    sleep 1
}

# Main benchmark loop
#
#
for ((run=1; run<=RUNS; run++)); do
    echo -e "${YELLOW}=== RUN: $run ===${NC}"
    for compression in "${COMPRESSIONS[@]}"; do
        echo -e "${YELLOW}=== Testing with $compression compression ===${NC}"

        for streams in "${STREAM_COUNTS[@]}"; do
            echo -e "${YELLOW}=== Testing with $streams stream(s)===${NC}"
                run_test "$compression" "$streams" "$run"

        echo ""
        done
    done
done

# Cleanup any remaining jobs
# echo -e "${YELLOW}Cleaning up any remaining jobs...${NC}"
# cedana job list | grep "$JOB_BASE" | awk '{print $2}' | xargs -r -I {} cedana job kill "{}" 2>/dev/null || true

echo -e "${GREEN}Benchmarks completed!${NC}"
echo "Results saved to: $OUTPUT_FILE"
echo "System info saved to: $SYSTEM_INFO_FILE"

# Show summary
echo ""
echo "=== Summary ==="
echo "Total tests run: $((${#COMPRESSIONS[@]} * ${#STREAM_COUNTS[@]} * RUNS))"
echo "Data points collected: $(($(wc -l < "$OUTPUT_FILE") - 1))"
echo ""

# Calculate averages if multiple runs
if [ "$RUNS" -gt 1 ]; then
    echo "=== Average Times ==="
    python3.14 -c "
import pandas as pd
import numpy as np

# Read CSV and clean data
df = pd.read_csv('$OUTPUT_FILE')
# Convert timing columns to numeric, invalid values become NaN
for col in ['checkpoint_time', 'restore_time', 'total_time']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Remove rows with NaN timing data
df_clean = df.dropna(subset=['checkpoint_time', 'restore_time', 'total_time'])
if len(df_clean) < len(df):
    print(f'Warning: Removed {len(df) - len(df_clean)} rows with invalid timing data')

avg = df_clean.groupby(['compression', 'streams'])[['checkpoint_time', 'restore_time', 'total_time']].mean().round(3)
print(avg.to_string())
"
fi

echo -e "${GREEN}Run 'python3 plot_timings.py' to generate visualization${NC}"
