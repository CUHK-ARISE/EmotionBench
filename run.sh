# # Generation example
# python run_emotionbench.py \
#   --model gpt-3.5-turbo \
#   --shuffle-count 1 \
#   --mode generation


# Analysis examples
python run_emotionbench.py \
  --model davinci-003 \
  --shuffle-count 1 \
  --mode analysis

python run_emotionbench.py \
  --model gpt-3.5-turbo \
  --shuffle-count 1 \
  --mode analysis

python run_emotionbench.py \
  --model gpt-4 \
  --shuffle-count 1 \
  --mode analysis

python run_emotionbench.py \
  --model llama2-7b \
  --shuffle-count 1 \
  --mode analysis

python run_emotionbench.py \
  --model llama2-13b \
  --shuffle-count 1 \
  --mode analysis

