import json
import random
import argparse
import traceback
from tqdm import tqdm
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

from llm import LLMChat, Message, get_platform
from process.helper import get_questionnaire, get_situations, formulate_prompt

MAX_RETRIES = 3
EMOTIONS = ["Anger", "Anxiety", "Depression", "Frustration", "Jealousy", "Guilt", "Fear", "Embarrassment"]


def build_question_tuples(questions: Dict[str, str], shuffle: bool) -> List[Tuple[str, int, str]]:
    """ Returns a list of (raw_id, shuffle_id, text) """
    items = list(questions.items())
    if shuffle:
        random.shuffle(items)
    return [
        (raw_id, idx + 1, text)
        for idx, (raw_id, text) in enumerate(items)
    ]


def request(model: LLMChat, prompt: str) -> Dict[str, Any]:
    """ Sends a request to the LLM and returns the JSON response. Retries on failure. """
    
    def extract_json_snippet(response: str) -> str:
        if "```json" in response and "```" in response:
            return response.split("```json")[-1].split("```")[0].strip()
        return response
    
    for attempt in range(MAX_RETRIES):
        try:
            if model.model_name == "Qwen/Qwen3-32B":
                response = model.chat([
                    Message(role="user", content=prompt),
                    Message(role="assistant", content="</think>")
                ])
            else:
                response = model.chat([
                    Message(role="user", content=prompt)
                ])
            json_response = json.loads(extract_json_snippet(response[0]))
            return json_response
        except Exception as e:
            print(f"Attempt {attempt + 1} failed with error: {type(e).__name__}: {e}")
            print(f"Full traceback:\n{traceback.format_exc()}")
    raise RuntimeError("Max retries exceeded for LLM request.")
    

def process_one_response(
    model: LLMChat,
    questionnaire: Dict[str, Any],
    shuffle: bool,
    situation: Dict[str, str] = None
) -> Dict[str, Any]:
    questions = questionnaire["questions"]
    scaling = questionnaire["scaling"]
    scale_descriptions = ", ".join([f"{k}: {v}" for k, v in scaling.items() if v != ""])
    question_tuples = build_question_tuples(questions, shuffle)
    shuffle_to_raw = {shuffle_id: raw_id for raw_id, shuffle_id, _ in question_tuples}
    
    question_list = "\n".join(
        f"{shuffle_id}. {text}"
        for _, shuffle_id, text in sorted(question_tuples, key=lambda x: x[1])
    )
    
    # Extract situation text if provided, None otherwise (control mode)
    situation_text = situation["text"] if situation is not None else None
    prompt = formulate_prompt(
        instruction=questionnaire["instruction"],
        scale_descriptions=scale_descriptions,
        min_score=questionnaire["min_score"],
        max_score=questionnaire["max_score"],
        question_list=question_list,
        situation=situation_text
    )
    response = request(model, prompt)
    
    # Map shuffle_id back to raw_id
    mapped_response = {}
    for shuffle_id_str, score in response.items():
        shuffle_id = int(shuffle_id_str)
        raw_id = shuffle_to_raw[shuffle_id]
        mapped_response[raw_id] = score
    
    return mapped_response


def load_completed_situations(output_path: Path, n: int) -> set:
    """Load situation IDs that have already been completed from the output file."""
    completed = set()
    if output_path.exists():
        with open(output_path, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if len(entry.get("responses", [])) == n:
                        completed.add(entry.get("situation_id"))
                except json.JSONDecodeError:
                    continue
    return completed


def run_emotionbench(args: argparse.Namespace) -> str:
    
    questionnaire = get_questionnaire(args.questionnaire)
    
    # Handle control mode vs emotion mode
    if args.control:
        situations = [{"situation_id": "control"}]
    else:
        emotions = [args.emotion] if args.emotion != "ALL" else EMOTIONS
        situations = get_situations(emotions, args.situation_source)
    
    model_cls = get_platform(args.platform)
    model = model_cls(model_name=args.model)
    model_wrapper = args.model.split("/")[-1].lower()
    output_dir = Path("results") / model_wrapper
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if args.control:
        output_name = args.output_name if args.output_name else f"{model_wrapper}_{args.questionnaire.lower()}_control"
    else:
        output_name = args.output_name if args.output_name else f"{model_wrapper}_{args.questionnaire.lower()}"
    output_path = output_dir / (output_name + ".jsonl" if not output_name.endswith(".jsonl") else output_name)
    
    n = args.repeat
    shuffle = args.shuffle
    max_workers = args.max_workers
    
    # Continuous mode: filter out already completed situations
    if args.continuous and output_path.exists():
        completed_ids = load_completed_situations(output_path, n)
        original_count = len(situations)
        situations = [s for s in situations if s.get("situation_id") not in completed_ids]
        print(f"Continuous mode: Resuming with {len(situations)} remaining situations (skipped {original_count - len(situations)} completed)")
    elif output_path.exists() and not args.continuous:
        with open(output_path, "w") as f:
            pass
        print(f"Warning: Output file {output_path} already exists. Use --continuous to resume or specify a different output name.")
    
    file_lock = Lock()
    total_tasks = len(situations) * n
    situation_responses = defaultdict(list)
    situation_lock = Lock()
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks and track which situation each belongs to
        future_to_situation_id = {}
        situation_id_to_data = {}
        
        for situation in situations:
            sit_id = id(situation)
            situation_id_to_data[sit_id] = situation
            for _ in range(n):
                # In control mode, pass None for situation; otherwise pass the situation dict
                situation_arg = None if args.control else situation
                future = executor.submit(process_one_response, model, questionnaire, shuffle, situation_arg)
                future_to_situation_id[future] = sit_id
        
        # Process results as they complete
        for future in tqdm(as_completed(future_to_situation_id.keys()),
                          total=total_tasks,
                          desc="Processing responses"):
            response = future.result()
            sit_id = future_to_situation_id[future]
            
            # Add response to the situation's list
            with situation_lock:
                situation_responses[sit_id].append(response)
                
                if len(situation_responses[sit_id]) == n:
                    situation = situation_id_to_data[sit_id]
                    
                    # Build entry based on mode
                    if args.control:
                        entry = {
                            "situation_id": situation["situation_id"],
                            "questionnaire": questionnaire["name"],
                            "responses": situation_responses[sit_id]
                        }
                    else:
                        entry = {
                            **situation,
                            "questionnaire": questionnaire["name"],
                            "responses": situation_responses[sit_id]
                        }
                    
                    with file_lock:
                        with open(output_path, "a") as f:
                            f.write(json.dumps(entry) + "\n")
