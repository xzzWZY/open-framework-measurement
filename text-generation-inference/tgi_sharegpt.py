import requests
import time
import json
import logging
import threading
import argparse
import numpy as np

logger = logging.getLogger('text_generation_measure')
logging.basicConfig(level=logging.INFO)

def send_request_to_docker(request_id, input_text, log_file, url="http://127.0.0.1:8080/generate_stream"):
    payload = {
        "inputs": input_text,
        "parameters": {"max_new_tokens": 1024}
    }
    headers = {'Content-Type': 'application/json'}

    try:
        with requests.post(url, json=payload, headers=headers, stream=True) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith('data:'):
                        json_data = json.loads(decoded_line[len('data:'):])
                        timestamp = time.time()
                        generated_text = json_data.get("generated_text")
                        logger.info(f"Request ID: {request_id}; Time: {timestamp}; Output: {generated_text}")
                        with open(log_file, "a") as file:
                            file.write(f"Request ID: {request_id}; Time: {timestamp}; Output: {generated_text}\n")
    except requests.RequestException as e:
        logger.error(f'HTTP Request failed: {e}')

def main(input_file, sleep_time, period_time=20):
    print(f"sleep_time: {sleep_time}")
    print(f"period_time: {period_time}")
    log_file = "response_log.txt"

    # 从文件中读取输入
    with open(input_file, 'r') as file:
        data = json.load(file)

    threads = []
    request_id = 1
    start_time = time.time()

    for item in data:
        current_time = time.time()
        if (current_time - start_time) > period_time:
            # 开始新的周期
            start_time = current_time

        if (current_time - start_time) <= period_time * 0.7:
            # 周期的前 70% 时间
            input_text = item.get("human", "")
            request_time = time.time()
            logger.info(f"Input Request ID: {request_id}; Time: {request_time}")
            with open(log_file, "a") as file:
                file.write(f"Input Request ID: {request_id}; Time: {request_time}\n")

            # 启动新线程来发送请求
            thread = threading.Thread(target=send_request_to_docker, args=(request_id, input_text, log_file))
            threads.append(thread)
            thread.start()

            request_id += 1
            while True:
                poisson_delay = np.random.poisson(10 * sleep_time / 1.4)
                if 0.2 <= poisson_delay <= 50:
                    break
            time.sleep(poisson_delay / 10)  # 每 sleep_time / 1.4 秒启动一个新线程
        else:
            time.sleep(period_time - (current_time - start_time))


    # 等待所有线程完成
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-file", type=str, default="shuffled_6000.json")
    parser.add_argument("--sleep-time", type=float, default=2.8)
    parser.add_argument("--period", type=float, default=20)
    args = parser.parse_args()
    main(args.input_file, args.sleep_time, args.period)