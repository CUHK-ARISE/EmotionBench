# EmotionBench
**RESEARCH USE ONLY. NO COMMERCIAL USE ALLOWED**

Benchmarking LLMs' Empathy Ability.

# Usage
An example run:
```
python run_emotionbench.py \
  --model gpt-3.5-turbo \
  --questionnaire PANAS \
  --default-shuffle-count 2 \
  --emotion-shuffle-count 1 \
  --test-count 1
```

An example result of overall analysis:
| Emotions | Positive Affect | Negative Affect | N |
| :---: |:---: | :---: | :---: |
| Default |43.3 $\pm$ 2.5 | 25.3 $\pm$ 0.6 | 3 |
| Anger | $-$ (-18.8) | $-$ (-0.3) | 2 |
| Anxiety | $-$ (-11.3) | $\downarrow$ (-3.8) | 2 |
| Overall | $-$ (-15.1) | $-$ (-2.1) | 4 |

An example result of specific emotion analysis:
| Factors | Positive Affect | Negative Affect | N |
| :---: |:---: | :---: | :---: |
| Default |43.3 $\pm$ 2.5 | 25.3 $\pm$ 0.6 | 3 |
| Facing Self-Opinioned People | $-$ (-18.8) | $-$ (-0.3) | 2 |
| Overall | $-$ (-18.8) | $-$ (-0.3) | 2 |

## Argument Specification
1. `--questionnaire`: (Required) Select the questionnaire(s) to run. For choises please see the list bellow.

2. `--model`: (Required) The name of the model to test.

3. `--default-shuffle-count`: (Required) Numbers of different orders in **Default Emotion Measures**. If set zero, run only the original order. If set n > 0, run the original order along with its n permutations. Defaults to zero.

4. `--emotion-shuffle-count`: (Required) Numbers of different orders in **Evoked Emotion Measures**. If set zero, run only the original order. If set n > 0, run the original order along with its n permutations. Defaults to zero.

5. `--test-count`: (Required) Numbers of runs for a same order. Defaults to one.

5. `--name-exp`: Name of this run. Is used to name the result files.

6. `--significance-level`: The significance level for testing the difference of means between human and LLM. Defaults to 0.01.

7. `--mode`: For debugging. To choose which part of the code is running.

Arguments related to `openai` API (can be discarded when users customize models):

1. `--openai-organization`: Your organization ID. Can be found in `Manage account -> Settings -> Organization ID`.

2. `--openai-key`: Your API key. Can be found in `View API keys -> API keys`.

## Benchmarking Your Own Model
It is easy! Just replace the function `example_generator` fed into the function `run_psychobench(args, generator)`.

Your customized function `your_generator()` does the following things:

1. Read questions from the file `args.testing_file`. The file locates under `results/` (check `run_psychobench()` in `utils.py`) and has the following format:

| question-0 | order-0 | ... |	General_test-0_order-0 | ... | Anger-0_scenario-0_test-0_order-0 | ... | Anxiety-0_scenario-0_test-0_order-1 |
| --- | --- |--- | --- | --- | --- | --- | --- |
| Prompt: ... | Prompt: ... | ... |  | ... | Imagine... | ... | Imagine... |
| 1. Q1 | 1 | ... | 4 | ... | 3 | ... | 3 |
| 2. Q2 | 2 | ... | 2 | ... | 4 | ... | 3 |
| ... | ... | ... | ... | ... | ... | ... | ... |
| n. Qn | n | ... | 3  | ... | 3 | ... | 1 |


You can read the columns before each column starting with `order-`, which contains the shuffled questions for your input.

2. Call your own LLM and get the results.

3. Fill in the blank in the file `args.testing_file`. **Remember**: No need to map the response to its original order. Our code will take care of it.

Please check `example_generator.py` for datailed information.

## Questionnaire List (Choices for Argument: --questionnaire)
1. Positive And Negative Affect Schedule: `--questionnaire PANAS`
