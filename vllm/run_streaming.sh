token=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
python server.py --host 127.0.0.1 --model /vllm/Llama-2-13b-chat-hf --block-size 16 &
server_pid=$!
sleep 30 && python client.py --input-file shuffled_6000.json --host 127.0.0.1 --delay 1.18
wait $server_pid

mv trace.txt llama-2-13B-6000-118.txt