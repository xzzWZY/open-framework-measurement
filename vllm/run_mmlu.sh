python server.py --host 127.0.0.1 --model /vllm/Llama-2-13b-chat-hf --block-size 16 &
server_pid=$!

python server_monitor.py --out-file server-metric-03.txt &
monitor_pid=$!

sleep 30

python client.py --host 127.0.0.1 --delay 0.3 &
client_pid=$!
wait $server_pid

mv trace.txt llama-2-13B-mmlu-03.txt

kill $server_pid
kill $client_pid
kill $monitor_pid

python server.py --host 127.0.0.1 --model /vllm/Llama-2-13b-chat-hf --block-size 16 &
server_pid=$!

python server_monitor.py --out-file server-metric-035.txt &
monitor_pid=$!

sleep 30

python client.py --host 127.0.0.1 --delay 0.35 &
client_pid=$!
wait $server_pid

mv trace.txt llama-2-13B-mmlu-035.txt

kill $server_pid
kill $client_pid
kill $monitor_pid
