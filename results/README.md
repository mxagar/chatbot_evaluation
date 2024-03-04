# Results

This folder should contain the result of using `chatbot_evaluation` on a dataset.

That result is usually a CSV with a flexible schema as follows:

```
index                           : int
question                        : string
reference_answer                : string
predicted_answer                : string
duration                        : float (seconds)
<scorer_type>_<score>           : float; each scorer type ("dummy", "bert", "sbert", "llm") can have an entry
chatbot_type                    : string ("dummy", "api", "lib")
dataset_path                    : string
scorers                         : string of List[str] ("dummy", "bert", "sbert", "llm")
<scorer>_params                 : string of dict; each scorer type ("dummy", "bert", "sbert", "llm") can have an entry
param_<n>                       : additional user-defined parameters
```
