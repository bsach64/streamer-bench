#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#define TARGET_RAM_GB 0.5

__global__ void memory_compute_kernel(unsigned char* data, int size) {
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    int stride = blockDim.x * gridDim.x;
    
    unsigned long long sum = 0;
    while (true) {
        // Force memory access with computation
        for (int i = tid; i < size; i += stride) {
            sum += data[i];
            sum = sum % (1ULL << 32);  // Prevent overflow
        }
        
        // Prevent compiler optimization
        if (sum == 0) {
            data[0] = 1;
        }
    }
}

void cuda_hybrid_load(size_t shared_size) {
    unsigned char *gpu_data;
    unsigned char *host_data;
    
    // Allocate GPU memory
    cudaMalloc(&gpu_data, shared_size);
    printf("Process %d allocated %.2f MB on GPU\n", getpid(), shared_size / 1024.0 / 1024.0);
    
    // Create host data and copy to GPU
    host_data = (unsigned char*)malloc(shared_size);
    for (size_t i = 0; i < shared_size; i++) {
        host_data[i] = rand() % 256;
    }
    cudaMemcpy(gpu_data, host_data, shared_size, cudaMemcpyHostToDevice);
    
    // Launch kernel
    int block_size = 256;
    int grid_size = (shared_size + block_size - 1) / block_size;
    
    printf("Launching CUDA kernel with %d blocks, %d threads per block\n", grid_size, block_size);
    
    memory_compute_kernel<<<grid_size, block_size>>>(gpu_data, shared_size);
    cudaDeviceSynchronize();
    
    // Cleanup
    cudaFree(gpu_data);
    free(host_data);
}

int main() {
    size_t bytes_per_core = (size_t)(TARGET_RAM_GB * 1024 * 1024 * 1024);
    printf("Press Ctrl+C to stop.\n");
    
    try {
        cuda_hybrid_load(bytes_per_core);
        while (true) {
            sleep(1);
        }
    } catch (...) {
        printf("\nStopping CUDA workload...\n");
    }
    
    return 0;
}