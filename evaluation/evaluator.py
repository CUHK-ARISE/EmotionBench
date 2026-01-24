import json
from pathlib import Path
from typing import Dict, List
from statistics import mean
from copy import deepcopy


def load_jsonl(file_path: str) -> List[Dict]:
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data


def load_questionnaire(questionnaire_name: str) -> Dict:
    questionnaire_path = Path("data") / "questionnaires.json"
    with open(questionnaire_path, 'r', encoding='utf-8') as f:
        questionnaires = json.load(f)
    
    if questionnaire_name not in questionnaires:
        raise ValueError(f"Questionnaire '{questionnaire_name}' not found in {questionnaire_path}")
    return questionnaires[questionnaire_name]


def compute_category_score(response: Dict, category_questions: List[int], reverse_scaling: List[int], max_score: int) -> float:
    score = 0
    for q_id in category_questions:
        q_str = str(q_id)
        if q_str not in response:
            continue
        value = response[q_str]
        if q_id in reverse_scaling:
            value = max_score + 1 - value
        score += value
    return score


def compute_average_scores(responses: List[Dict], questionnaire: Dict) -> Dict[str, float]:
    categories = questionnaire['categories']
    reverse_scaling = questionnaire.get('reverse_scaling', [])
    max_score = questionnaire['max_score']
    compute_mode = questionnaire.get('compute_mode', 'SUM')
    category_scores = {}
    
    for cat_name, cat_questions in categories.items():
        scores = []
        for response in responses:
            score = compute_category_score(response, cat_questions, reverse_scaling, max_score)
            scores.append(score)
        
        avg_score = mean(scores) if scores else 0.0
        
        if compute_mode == 'SUM*2':
            avg_score *= 2
        
        category_scores[cat_name] = round(avg_score, 2)
    
    return category_scores


def evaluate_responses(input_file: str) -> List[Dict]:
    data = load_jsonl(input_file)
    results = []
    
    for item in data:
        questionnaire_name = item['questionnaire']
        questionnaire = load_questionnaire(questionnaire_name)
        avg_scores = compute_average_scores(item['responses'], questionnaire)
        result = deepcopy(item)
        del result['responses']
        result['scores'] = avg_scores
        results.append(result)
    return results


def save_jsonl(data: List[Dict], output_file: str):
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
