"""This script is the main app
which uses the chatbot_evaluation package.

Usage:
    
    python evaluate.py --config_path path/to/my/config.yaml --dataset_path path/to/my/dataset.csv --output_dir dir/of/results --output_filename results.csv
    python evaluate.py --config_path ./config_eval.yaml --dataset_path ./data/chat_history_dummy.csv
    python evaluate.py

Then, look at the output_dir, e.g., ./results/

Author: Mikel Sagardia
Date: 2024-02-28
"""
import argparse
from chatbot_evaluation.evaluation import (
    run_evaluation,
    load_config,
    load_dataset
)
from chatbot_evaluation.persistence import log_evaluation_results

OUTPUT_DIR = './results'
OUTPUT_FILENAME = 'evaluation_results.csv'
CONFIG_PATH = './config_eval.yaml'
DATASET_PATH = './data/chat_history_dummy.csv'
#DATASET_PATH = './data/qa_pairs_dummy.csv'


def main():
    # Create the parser
    parser = argparse.ArgumentParser(description="Run chatbot evaluation.")
    
    # Add the arguments
    parser.add_argument('--config_path', '-c', type=str, default=CONFIG_PATH, help="Path to the configuration file. Default: 'config_eval.yaml'.")
    parser.add_argument('--dataset_path', '-d', type=str, default=DATASET_PATH, help="Path to the dataset file. Default: 'chat_history_dummy.csv'.")
    parser.add_argument('--output_dir', '-o', type=str, default=OUTPUT_DIR, help="Directory where results are output. Default: './results'.")
    parser.add_argument('--output_filename', '-f', type=str, default=OUTPUT_FILENAME, help="Filename of the results CSV. Default: 'evaluation_results.csv'.")

    # Parse the arguments
    args = parser.parse_args()

    # Call the run_evaluation function with parsed arguments
    config = load_config(filepath=args.config_path)
    dataset = load_dataset(config=config)
    results = run_evaluation(config=config, dataset=dataset)
    print(results)
    
    # Persistence of the results
    log_evaluation_results(results=results,
                           config=config,
                           output_directory=args.output_dir,
                           output_filename=args.output_filename)

if __name__ == "__main__":
    main()
