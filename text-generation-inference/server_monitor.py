import pynvml
import time
import argparse

# 初始化NVML
pynvml.nvmlInit()

handle = pynvml.nvmlDeviceGetHandleByIndex(0) 

def get_gpu_compute_usage():
    utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
    return utilization.gpu 

def get_gpu_power_usage():
    power = pynvml.nvmlDeviceGetPowerUsage(handle)
    return power / 1000.0 

def main(out_file: str):
    while True:
        compute_usage = get_gpu_compute_usage()
        power_usage = get_gpu_power_usage()

        with open(out_file, 'a') as f:
            f.write(f"GPU Compute Usage: {compute_usage}%")
            f.write(f"GPU Power Usage: {power_usage} Watts")
            f.write("\n")

        time.sleep(5)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-file", type=str, default="server_metric.txt")
    args = parser.parse_args()
    main(args.out_file)
