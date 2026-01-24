import argparse
from pathlib import Path

from evaluation.evaluator import evaluate_responses, save_jsonl


def main():
    parser = argparse.ArgumentParser(
        description='Evaluate EmotionBench responses and compute average scores per situation.'
    )
    parser.add_argument(
        'input_file',
        type=str,
        help='Path to the input JSONL file containing responses'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Path to the output JSONL file (default: input_file with _eval suffix)'
    )
    
    args = parser.parse_args()
    
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Input file '{args.input_file}' not found.")
        return 1
    
    # Determine output path
    if args.output:
        output_path = args.output
    else:
        output_path = str(input_path.parent / f"{input_path.stem}_eval.jsonl")
    
    print(f"Evaluating: {args.input_file}")
    
    results = evaluate_responses(args.input_file)
    
    save_jsonl(results, output_path)
    
    print(f"Results saved to: {output_path}")
    print(f"Processed {len(results)} situations.")
    
    return 0


if __name__ == '__main__':
    exit(main())
