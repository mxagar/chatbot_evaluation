# Chatbot Evaluation

This repository contains a simple chatbot evaluation package which can be used to score chatbots using a dataset of predefined and rated chat sessions.

## Table of Contents

- [Chatbot Evaluation](#chatbot-evaluation)
  - [Table of Contents](#table-of-contents)
  - [File Structure and Package Overview](#file-structure-and-package-overview)
  - [Setup](#setup)
  - [Data Input, Dataset](#data-input-dataset)
  - [Chatbot Integration](#chatbot-integration)
  - [Scorer Integration](#scorer-integration)
  - [Configuration YAML](#configuration-yaml)
  - [Further Implementation Notes](#further-implementation-notes)
    - [Metrics](#metrics)
    - [Parameters to Consider](#parameters-to-consider)
  - [Intereting Links](#intereting-links)
  - [Authorship](#authorship)

## File Structure and Package Overview

The package is composed by the following files:

```
.
│   config_eval.yaml                        # Cofiguration YAML
│   evaluate.py                             # User script-based entrypoint
│   pyproject.toml
│   README.md
│   requirements.in                         # Dependencies
│   requirements.txt
│
├───assets/
├───chatbot_evaluation/                     # Package folder
│   │   chatbot.py                          # Chatbot definitions
│   │   core.py                             # Common structures
│   │   dataset.py                          # Dataset loading
│   │   evaluation.py                       # Evaluation
│   │   persistence.py                      # Store results
│   │   scoring.py                          # Scorer definitions
│   └───__init__.py
│
├───data/
│   │   chat_history_dummy.csv              # Dummy dataset with chat history format
│   │   qa_pairs_dummy.csv                  # Dummy dataset with Q-A pair format
│   │   check_data.py
│   │   convert_data.py
│   │   create_history_dummy_dataset.py
│   └───README.md
│
├───notebooks/
│       README.md
│       result_evaluation.ipynb
│       scoring_tests.ipynb
│       simple_service_tests.ipynb
│
├───results
│       README.md
│
├───tests/                                  # Pytest testing
│   │   config_test.yaml
│   │   conftest.py
│   │   test_evaluation.py
│   └───__init__.py
│
└───utils
        README.md
```

The package is contained mainly in `chatbot_evaluation/`; the modules of the package are extendable.

The tests are implemented in [`./tests/test_evaluation.py`](./tests/test_evaluation.py).

A simple usage script is provided in [`evaluate.py`](./evaluate.py).

## Setup

In order to use the package, first, you need to set a Python environment and then install the dependencies.
You can install the package, although it's not necessary if you use it from the repository folder.
A quick recipe to getting started by using [conda](https://conda.io/projects/conda/en/latest/index.html) is the following:

```bash
# Set proxy, if required

# Create environment, e.g., with conda, to control Python version
conda create -n chat-eval python=3.10 pip
conda activate chat-eval

# Install pip-tools
python -m pip install -U pip-tools

# Generate pinned requirements.txt
pip-compile requirements.in

# Install pinned requirements, as always
python -m pip install -r requirements.txt

# If required, add new dependencies to requirements.in and sync
# i.e., update environment
pip-compile requirements.in
pip-sync requirements.txt
python -m pip install -r requirements.txt

# Optional: To install the package
python -m pip pip install .

# Optional: if you's like to export you final conda environment config
conda env export > environment.yml
# Optional: If required, to delete the conda environment
conda remove --name chat-eval --all
```

Once everything is installed, we can use the package as follows:

```bash
# Get a dataset with the propper format -> see data/README.md
# Set a configuration YAML -> config_eval.yaml
# Run evaluate.py
python evaluate.py --config_path ./config_eval.yaml --dataset_path ./data/chat_history_dummy.csv
```

The results should be placed in the `./results/` folder.

## Data Input, Dataset

Currently two dataset formats are supported.
See [`./data/README.md`](./data/README.md) for more information.

## Chatbot Integration

At the moment, these chatbots have been defined after deriving `AbstractChatBot`:

- `ChatBotDummy`: it randomly selects an answer from a predefined list, i.e., a list of answers taken from the fed dataset.
- `ChatBotAPI`: it sends questions to a remote API, e.g. OpenAI's ChatGPT. However, this class needs to be slightly adapted to the use-case.
- `ChatBotLib`: it can connect to a local LLM using a library; **note that this class needs to be implemented yet**.

Further chatbots can be easily defined by copy-pasting any of the above; then, the `evaluation.load_chatbot()` interface needs to be extended.

## Scorer Integration

At the moment, these scorers have been defined after deriving `AbstractScorer`:

- `ScorerDummy`: it randomly scores the similarity between a reference and predicted answer/string.
- `ScorerBERT`: it scores the similarity between a reference and predicted answer/string using the [BERT-score](https://github.com/Tiiiger/bert_score) package.
- `ScorerBERT`: it scores the similarity between a reference and predicted answer/string using the [sentence-transformers](https://www.sbert.net/) package; text embeddings are computed and then the cosine similarity is obtained.
- `ScorerLLM`: This scorer predicts the similarity score between a predicted and reference string by asking a LLM; **note that this class needs to be implemented yet**.

Further scorers can be easily defined by copy-pasting any of the above; then, the `evaluation.load_scorers()` interface needs to be extended.

## Configuration YAML

In the following, an exemplary configuration YAML is shown:

```yaml
chatbot_type: "api"  # Options: "dummy", "api", "lib" (if implemented)
dataset_path: "./data/chat_history_dummy.csv"

# Configuration for ChatBotAPI
api:
  url: "api.example.com"
  token_type: "Bearer"

# "dummy", bert-score: "bert", sentence-transformers: "sbert", llm: "llm" (if implemented)
scorers:
  - "dummy"
  - "bert"
  - "sbert"

# Configuration for BERT-scorer
bert:
  lang: "en"  # "de", "en"

# Configuration for SBERT-scorer (sentence-transformers)
sbert:
  model_name: "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Optional chatbot parameters
chatbot_params:
  param_1: "value_1"
  param_2: "value_2"
  param_3: "value_3"
```

The configuration file is loaded in [`evaluation.py`](./chatbot_evaluation/evaluation.py) and its content can be easily extended.
The values of the configuration file are copied to the results CSV.

## Further Implementation Notes

### Metrics

- [x] Time to provide the answer (several queries necessary?)
- [x] Answer BERT-score wrt. target/reference
- [x] Answer SBERT-score wrt. target
- [ ] Answer length (tokens)

### Parameters to Consider

- [ ] App service type (e.g., capacity, vCPU, RAM, ...)
- [ ] Chatbot model and version (thus, context length), e.g., gpt-35-turbo-0613, ...
- [ ] Temperature: 0.7, ...
- [ ] Prompts

## Intereting Links

- [Azure OpenAI Service REST API reference](https://learn.microsoft.com/en-us/azure/ai-services/openai/reference)
- [Metric: bert_score](https://huggingface.co/spaces/evaluate-metric/bertscore)
- [OpenAI Prompting guide](https://platform.openai.com/docs/guides/prompt-engineering/strategy-test-changes-systematically)
- [CRUD-RAG: A Comprehensive Chinese Benchmark for Retrieval-Augmented Generation of Large Language Models](https://arxiv.org/abs/2401.17043)

## Authorship

Mikel Sagardia, 2024.  
