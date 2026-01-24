import argparse
from process.runner import run_emotionbench

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    # ----- For running experiments -----
    parser.add_argument("--model",required=True, type=str,
                        help="The name of the model to test")
    
    parser.add_argument("--platform", required=True, type=str,
                        choices=["openai", "anthropic", "deepinfra", "togetherai", "gemini", "openkey"],
                        help="The platform of the model to test")
    
    parser.add_argument("--questionnaire", required=True, type=str,
                        choices=["PANAS", "BFNE", "FSS", "AGQ", "FDS", "BDI", "DASS-21", "GASP", "MJS"],
                        help="Questionnaire to use in the experiment.")
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--control", action="store_true",
                        help="Whether to run the control experiment (without emotional situation).")
    
    group.add_argument("--emotion", type=str,
                        choices=["Anger", "Anxiety", "Depression", "Frustration", "Jealousy", "Guilt", "Fear", "Embarrassment", "ALL"],
                        help="Emotion to use in the experiment.")
    
    parser.add_argument("--situation-source", type=str, default="data/reformatted_situations.jsonl",
                        help="Path to the situation source file. Defaults to 'data/reformatted_situations.jsonl'.")
    
    parser.add_argument("--repeat", "-n", type=int, default=1,
                        help="Number of runs for the same order. Defaults to 1.")
    
    parser.add_argument("--max-workers", type=int, default=1,
                        help="Number of workers to use for parallel processing. Defaults to 1.")
    
    parser.add_argument("--output-name", type=str, default=None,
                        help="Name of this run. Is used to name the result files.")
    
    parser.add_argument("--continuous", action="store_true",
                        help="Resume from existing output file, skipping already completed situations.")
    
    parser.add_argument("--shuffle", action="store_true",
                        help="Whether to shuffle the order of situations.")
    
    args = parser.parse_args()
    
    run_emotionbench(args)
