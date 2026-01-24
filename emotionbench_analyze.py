import argparse
from evaluation.analysis import run_analysis

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Analyze EmotionBench results by comparing control and target conditions.',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--control-file',
        required=True,
        help='Path to control JSONL file'
    )
    
    parser.add_argument(
        '--target-file',
        required=True,
        help='Path to target JSONL file with emotional situations'
    )
    
    parser.add_argument(
        '--questionnaire',
        default='PANAS',
        help='Questionnaire name (default: PANAS)'
    )
    
    parser.add_argument(
        '--significance-level',
        type=float,
        default=0.05,
        help='Significance level for hypothesis testing (default: 0.05)'
    )
    
    parser.add_argument(
        '--by-emotion',
        action='store_true',
        help='Include emotion-specific comparisons in addition to overall comparison'
    )
    
    args = parser.parse_args()
    
    run_analysis(args)
