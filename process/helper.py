import os
import json
from typing import Dict, List
from jinja2 import Environment, FileSystemLoader
from pathlib import Path


def get_questionnaire(name: str) -> Dict:
    """ Load questionnaire data from a JSON file. """
    filepath = Path("data") / "questionnaires.json"
    if os.path.exists(filepath):
        with open(filepath, "r") as file:
            questionnaires = json.load(file)
        return questionnaires.get(name, {})
    else:
        raise FileNotFoundError(f"Questionnaire file not found at {filepath}")


def get_situations(emotions: List[str], filepath: str) -> List[Dict[str, str]]:
    """ Load situations data from a JSON file. """
    filepath = Path(filepath)
    if os.path.exists(filepath):
        filtered_situations = []
        with open(filepath, "r") as file:
            for line in file:
                situation = json.loads(line)
                if situation["emotion"] in emotions:
                    filtered_situations.append(situation)
        return filtered_situations
    else:
        raise FileNotFoundError(f"Situations file not found at {filepath}")


def formulate_prompt(
    instruction: str,
    scale_descriptions: str,
    min_score: int,
    max_score: int,
    question_list: str,
    situation: str = None,
) -> str:
    """ Formulate the prompt for the LLM based on the situation and questionnaire details.

    Args:
        instruction: The questionnaire instruction
        scale_descriptions: Description of the rating scale
        min_score: Minimum score value
        max_score: Maximum score value
        question_list: Formatted list of questions
        situation: Optional situation text. If None, uses control template without situation.
    """
    # Select template based on whether we have a situation (control mode or not)
    template_name = "control.j2" if situation is None else "prompt.j2"
    prompt_path = Path("data") / template_name
    
    if os.path.exists(prompt_path):
        template_dir = os.path.dirname(prompt_path)
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template(os.path.basename(prompt_path))
    else:
        raise FileNotFoundError(f"Prompt template file not found at {prompt_path}")
    
    template_vars = {
        "instruction": instruction,
        "scale_descriptions": scale_descriptions,
        "min_score": min_score,
        "max_score": max_score,
        "question_list": question_list
    }
    
    if situation is not None:
        template_vars["situation"] = situation
    
    prompt = template.render(**template_vars).strip()
    return prompt