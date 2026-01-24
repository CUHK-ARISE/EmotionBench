import json
import numpy as np
import scipy.stats as stats

from pathlib import Path
from statistics import mean, stdev
from typing import Dict, List, Tuple


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


def compute_scores(responses: List[Dict], category_questions: List[int], reverse_scaling: List[int], scale: int) -> List[float]:
    scores = []
    for response in responses:
        score = 0
        for q_id in category_questions:
            q_str = str(q_id)
            if q_str not in response:
                continue
            
            value = response[q_str]
            
            if q_id in reverse_scaling:
                value = scale + 1 - value
            
            score += value
        
        scores.append(score)
    
    return scores


def perform_f_test(scores1: List[float], scores2: List[float], significance_level: float) -> Tuple[float, float, bool]:
    n1, n2 = len(scores1), len(scores2)
    std1, std2 = stdev(scores1), stdev(scores2)
    
    # Add epsilon to prevent zero standard deviation
    epsilon = 1e-8
    std1 += epsilon
    std2 += epsilon
    
    # F-test
    if std1 > std2:
        f_value = std1 ** 2 / std2 ** 2
        df1, df2 = n1 - 1, n2 - 1
    else:
        f_value = std2 ** 2 / std1 ** 2
        df1, df2 = n2 - 1, n1 - 1
    
    p_value = (1 - stats.f.cdf(f_value, df1, df2)) * 2
    equal_var = p_value > significance_level
    
    return f_value, p_value, equal_var


def perform_t_test(scores1: List[float], scores2: List[float], equal_var: bool, significance_level: float) -> Tuple[float, float, str]:
    mean1, mean2 = mean(scores1), mean(scores2)
    std1, std2 = stdev(scores1), stdev(scores2)
    n1, n2 = len(scores1), len(scores2)
    
    # Add epsilon to prevent zero standard deviation
    epsilon = 1e-8
    std1 += epsilon
    std2 += epsilon
    
    t_value, p_value = stats.ttest_ind_from_stats(
        mean1, std1, n1, mean2, std2, n2, equal_var=equal_var
    )
    
    if p_value > significance_level:
        conclusion = "equal"
    elif t_value > 0:
        conclusion = "greater"
    else:
        conclusion = "less"
        
    return t_value, p_value, conclusion


def analyze_condition(control_data: List[Dict], target_data: List[Dict], questionnaire: Dict, significance_level: float) -> Dict:
    results = {}

    # Extract all responses
    control_responses = []
    for item in control_data:
        control_responses.extend(item['responses'])
    
    target_responses = []
    for item in target_data:
        target_responses.extend(item['responses'])
    
    # Get questionnaire configuration
    categories = questionnaire['categories']
    reverse_scaling = questionnaire.get('reverse_scaling', [])
    max_score = questionnaire['max_score']
    
    # Analyze each category
    for cat_name, cat_questions in categories.items():
        # Compute scores
        control_scores = compute_scores(control_responses, cat_questions, reverse_scaling, max_score)
        target_scores = compute_scores(target_responses, cat_questions, reverse_scaling, max_score)
        
        # Statistics
        control_mean = mean(control_scores)
        control_std = stdev(control_scores)
        control_n = len(control_scores)
        
        target_mean = mean(target_scores)
        target_std = stdev(target_scores)
        target_n = len(target_scores)
        
        # Hypothesis testing
        f_value, f_pvalue, equal_var = perform_f_test(target_scores, control_scores, significance_level)
        t_value, t_pvalue, conclusion = perform_t_test(target_scores, control_scores, equal_var, significance_level)
        
        results[cat_name] = {
            'control': {
                'mean': control_mean,
                'std': control_std,
                'n': control_n
            },
            'target': {
                'mean': target_mean,
                'std': target_std,
                'n': target_n
            },
            'mean_diff': target_mean - control_mean,
            'f_test': {
                'f_value': f_value,
                'p_value': f_pvalue,
                'equal_variance': equal_var
            },
            't_test': {
                't_value': t_value,
                'p_value': t_pvalue,
                'conclusion': conclusion,
                'test_type': 'equal_variance' if equal_var else 'welch'
            }
        }
    return results


def analyze_by_emotion(control_data: List[Dict], target_data: List[Dict], questionnaire: Dict, significance_level: float) -> Dict:
    emotions = {}
    emotion_results = {}
    
    for item in target_data:
        emotion = item.get('emotion', 'Unknown')
        if emotion not in emotions:
            emotions[emotion] = []
        emotions[emotion].append(item)
    
    for emotion, emotion_data in emotions.items():
        emotion_results[emotion] = analyze_condition(
            control_data, emotion_data, questionnaire, significance_level
        )
    
    return emotion_results


def convert_to_serializable(obj):
    if isinstance(obj, dict):
        return {key: convert_to_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(item) for item in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.bool_):
        return bool(obj)
    else:
        return obj


def create_json_results(overall_results: Dict, emotion_results: Dict, significance_level: float, metadata: Dict = None) -> Dict:
    json_output = {
        'metadata': metadata or {},
        'significance_level': significance_level,
        'overall_comparison': overall_results,
        'emotion_specific_comparisons': emotion_results
    }
    json_output = convert_to_serializable(json_output)
    return json_output


def format_markdown_from_json(json_results: Dict) -> str:
    output = []
    significance_level = json_results['significance_level']
    overall_results = json_results['overall_comparison']
    emotion_results = json_results['emotion_specific_comparisons']
    output.append("# Results Analysis")
    
    # Add metadata if available
    if json_results.get('metadata'):
        metadata = json_results['metadata']
        output.append("-" * 80)
        output.append("## Metadata")
        output.append("-" * 80)
        for key, value in metadata.items():
            output.append(f"- **{key}**: {value}")
    
    # Overall results
    output.append("-" * 80)
    output.append("## Overall Comparison")
    output.append("-" * 80)
    
    for cat_name, results in overall_results.items():
        output.append(f"\n### {cat_name}")
        
        control = results['control']
        target = results['target']
        
        output.append("**Statistics:**")
        output.append(f"- Control: mean={control['mean']:.2f}, std={control['std']:.2f}, n={control['n']}")
        output.append(f"- Target:  mean={target['mean']:.2f}, std={target['std']:.2f}, n={target['n']}")
        output.append(f"- Difference: {results['mean_diff']:+.2f}")
        
        # F-test
        f_test = results['f_test']
        output.append("")
        output.append("**F-Test (Variance Equality):**")
        output.append(f"- F-value: {f_test['f_value']:.4f}")
        output.append(f"- P-value: {f_test['p_value']:.4f}")
        output.append(f"- Equal variance: {'Yes' if f_test['equal_variance'] else 'No'} (α={significance_level})")
        
        # T-test
        t_test = results['t_test']
        output.append("")
        output.append(f"**T-Test ({t_test['test_type'].replace('_', ' ').title()}):**")
        output.append(f"- T-value: {t_test['t_value']:.4f}")
        output.append(f"- P-value: {t_test['p_value']:.4f}")
        
        if t_test['conclusion'] == 'equal':
            output.append(f"- Conclusion: No significant difference (p > {significance_level})")
            output.append(f"- Target ≈ Control")
        elif t_test['conclusion'] == 'greater':
            output.append(f"- Conclusion: Target significantly GREATER than Control (p < {significance_level})")
            output.append(f"- Target > Control ({results['mean_diff']:+.2f})")
        else:
            output.append(f"- Conclusion: Target significantly LESS than Control (p < {significance_level})")
            output.append(f"- Target < Control ({results['mean_diff']:+.2f})")
    
    # Emotion-specific results
    if emotion_results:
        output.append("-" * 80)
        output.append("## Emotion-Specific Comparisons")
        output.append("-" * 80)
        for emotion, results_dict in emotion_results.items():
            output.append(f"### {emotion}")
            for cat_name, results in results_dict.items():
                output.append(f"\n#### {cat_name}")
                control = results['control']
                target = results['target']
                t_test = results['t_test']
                output.append(f"- Control: {control['mean']:.2f} ± {control['std']:.2f} (n={control['n']})")
                output.append(f"- {emotion}: {target['mean']:.2f} ± {target['std']:.2f} (n={target['n']})")
                output.append(f"- Difference: {results['mean_diff']:+.2f}")
                
                if t_test['conclusion'] == 'equal':
                    output.append(f"- No significant difference (p={t_test['p_value']:.4f})")
                elif t_test['conclusion'] == 'greater':
                    output.append(f"    - ↑ Significantly HIGHER (p={t_test['p_value']:.4f})")
                else:
                    output.append(f"    - ↓ Significantly LOWER (p={t_test['p_value']:.4f})")
            output.append("-" * 80)
        output.append("## Summary Table")
        output.append("-" * 80)
        categories = list(overall_results.keys())
        header = "| Emotion | " + " | ".join(categories) + " |"
        separator = "|" + "|".join(["---"] * (len(categories) + 1)) + "|"
        output.append(header)
        output.append(separator)
        
        # Add Overall row first
        row_values = ["**Overall**"]
        for cat_name in categories:
            results = overall_results[cat_name]
            mean_diff = results['mean_diff']
            t_test = results['t_test']
            p_value = t_test['p_value']
            
            # Format cell: mean_diff with significance indicator
            if t_test['conclusion'] == 'equal':
                cell = f"{mean_diff:+.2f} (ns)"
            elif t_test['conclusion'] == 'greater':
                if p_value < 0.001:
                    cell = f"{mean_diff:+.2f} ***"
                elif p_value < 0.01:
                    cell = f"{mean_diff:+.2f} **"
                elif p_value < 0.05:
                    cell = f"{mean_diff:+.2f} *"
                else:
                    cell = f"{mean_diff:+.2f} (ns)"
            else:  # less
                if p_value < 0.001:
                    cell = f"{mean_diff:+.2f} ***"
                elif p_value < 0.01:
                    cell = f"{mean_diff:+.2f} **"
                elif p_value < 0.05:
                    cell = f"{mean_diff:+.2f} *"
                else:
                    cell = f"{mean_diff:+.2f} (ns)"
            row_values.append(cell)
        
        row = "| " + " | ".join(row_values) + " |"
        output.append(row)
        
        # Create table rows for each emotion
        if emotion_results:
            for emotion, results_dict in emotion_results.items():
                row_values = [emotion]
                for cat_name in categories:
                    results = results_dict[cat_name]
                    mean_diff = results['mean_diff']
                    t_test = results['t_test']
                    p_value = t_test['p_value']
                    
                    # Format cell: mean_diff with significance indicator
                    if t_test['conclusion'] == 'equal':
                        cell = f"{mean_diff:+.2f} (ns)"
                    elif t_test['conclusion'] == 'greater':
                        if p_value < 0.001:
                            cell = f"{mean_diff:+.2f} ***"
                        elif p_value < 0.01:
                            cell = f"{mean_diff:+.2f} **"
                        elif p_value < 0.05:
                            cell = f"{mean_diff:+.2f} *"
                        else:
                            cell = f"{mean_diff:+.2f} (ns)"
                    else:  # less
                        if p_value < 0.001:
                            cell = f"{mean_diff:+.2f} ***"
                        elif p_value < 0.01:
                            cell = f"{mean_diff:+.2f} **"
                        elif p_value < 0.05:
                            cell = f"{mean_diff:+.2f} *"
                        else:
                            cell = f"{mean_diff:+.2f} (ns)"
                    row_values.append(cell)
                row = "| " + " | ".join(row_values) + " |"
                output.append(row)
        
        output.append("")
        output.append("*Note: * p<0.05, ** p<0.01, *** p<0.001, ns = not significant*")
        output.append("*Values represent mean difference (Target - Control)*")
    
    return "\n".join(output)


def run_analysis(args):
    # Load data
    control_data = load_jsonl(args.control_file)
    target_data = load_jsonl(args.target_file)
    questionnaire = load_questionnaire(args.questionnaire)
    
    # Analyze overall
    overall_results = analyze_condition(control_data, target_data, questionnaire, args.significance_level)
    emotion_results = {}
    if args.by_emotion:
        emotion_results = analyze_by_emotion(control_data, target_data, questionnaire, args.significance_level)
    
    # Create metadata
    metadata = {
        'control_file': args.control_file,
        'target_file': args.target_file,
        'questionnaire': args.questionnaire,
        'number_of_control_samples': len(control_data[0]["responses"]),
        'number_of_situations': len(target_data),
        'average_responses_per_situation': mean([len(item["responses"]) for item in target_data])
    }
    
    json_path = args.target_file.replace('.jsonl', '_analysis.json')
    json_results = create_json_results(overall_results, emotion_results, args.significance_level, metadata)
    markdown_path = args.target_file.replace('.jsonl', '_analysis.md')
    markdown_text = format_markdown_from_json(json_results)
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_results, f, indent=2, ensure_ascii=False)
        
    with open(markdown_path, 'w', encoding='utf-8') as f:
        f.write(markdown_text)
        
    print(f"Results saved to: {json_path} and {markdown_path}")
