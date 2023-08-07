import openai
import os
import pandas as pd
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)
import time
from tqdm import tqdm


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def chat(
    model,           # gpt-4, gpt-4-0314, gpt-4-32k, gpt-4-32k-0314, gpt-3.5-turbo, gpt-3.5-turbo-0301
    messages,        # [{"role": "system"/"user"/"assistant", "content": "Hello!", "name": "example"}]
    temperature=0,   # [0, 2]: Lower values -> more focused and deterministic; Higher values -> more random.
    n=1,             # Chat completion choices to generate for each input message.
    max_tokens=1024, # The maximum number of tokens to generate in the chat completion.
    delay=5          # Seconds to sleep after each request.
):
    time.sleep(delay)
    
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
        n=n,
        max_tokens=max_tokens
    )
    
    if n == 1:
        return response['choices'][0]['message']['content']
    else:
        return [i['message']['content'] for i in response['choices']]


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def completion(
    model,           # text-davinci-003, text-davinci-002, text-curie-001, text-babbage-001, text-ada-001
    prompt,          # The prompt(s) to generate completions for, encoded as a string, array of strings, array of tokens, or array of token arrays.
    temperature=0,   # [0, 2]: Lower values -> more focused and deterministic; Higher values -> more random.
    n=1,             # Completions to generate for each prompt.
    max_tokens=1024, # The maximum number of tokens to generate in the chat completion.
    delay=10         # Seconds to sleep after each request.
):
    time.sleep(delay)
    
    response = openai.Completion.create(
        model=model,
        prompt=prompt,
        temperature=temperature,
        n=n,
        max_tokens=max_tokens
    )
    
    if n == 1:
        return response['choices'][0]['text']
    else:
        response = response['choices']
        response.sort(key=lambda x: x['index'])
        return [i['text'] for i in response['choices']]


def convert_results(result, column_header):
    result = result.strip()  # Remove leading and trailing whitespace
    try:
        result_list = [int(element.strip()[-1]) for element in result.split('\n') if element.strip()]
    except:
        result_list = ["" for element in result.split('\n')]
        print(f"Unable to capture the responses on {column_header}.")
        
    return result_list


def example_generator(questionnaire, args):
    testing_file = args.testing_file
    model = args.model
    openai.organization = args.openai_organization
    openai.api_key = args.openai_key

    # Read the existing CSV file into a pandas DataFrame
    testing_df = pd.read_csv(testing_file)
    headers = testing_df.columns.tolist()

    questions_list = {f'order-{header[-1]}': '\n'.join(testing_df[header].astype(str)) for header in headers if header.startswith("question")}
    testing_list = [{"key":header, "scenario":testing_df[header].iloc[0]} for header in headers if not header.startswith(("question", "order"))]
    
    for test_case in tqdm(testing_list):
        result = ''
        order_key = test_case["key"].split('_')[-1]
        prompt = questions_list[order_key].replace('SCENARIO', test_case["scenario"])
        
        if model == 'text-davinci-003':
            inputs = prompt
            result = completion(model, inputs)
        elif model in ['gpt-3.5-turbo', 'gpt-4']:
            inputs = [
                {"role": "system", "content": questionnaire["inner_setting"]},
                {"role": "user", "content": prompt}
            ]
            result = chat(model, inputs)
        else:
            raise ValueError("The model is not supported or does not exist.")
        
        result.strip()
        
        results_list = convert_results(result, test_case["key"])
        
        output_df = pd.read_csv(testing_file)
        output_df[test_case["key"]] = [test_case["scenario"]] + results_list
        output_df.to_csv(testing_file, index=False)
    
        # Write the prompts and results to the file
        os.makedirs("prompts", exist_ok=True)
        os.makedirs("responses", exist_ok=True)
        with open(f'prompts/{model}-{test_case["key"].split("_")[0]}.txt', "a") as file:
            file.write(f'{inputs}\n====\n')
        with open(f'responses/{model}-{test_case["key"].split("_")[0]}.txt', "a") as file:
            file.write(f'{result}\n====\n')

