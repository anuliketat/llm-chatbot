# GPT-3 Fine-Tuned Chatbot

This repository contains code and examples for a GPT-3 based fine-tuned chatbot. The repository includes scripts for fine-tuning the model, a Jupyter notebook demonstrating the chatbot, and necessary datasets.

## Repository Structure

- `README.md`: This file. Contains an overview of the project and usage instructions.
- `requirements.txt`: Python dependencies required for running the code.
- `.gitignore`: Specifies files and directories to be ignored by git.
- `LICENSE`: License file for the project.
- `notebooks/`: Contains Jupyter notebooks.
  - `chatbot_demo.ipynb`: Jupyter notebook demonstrating the chatbot.
- `scripts/`: Contains Python scripts.
  - `fine_tune_model.py`: Script for fine-tuning the GPT-3 model.
- `data/`: Contains dataset files.
  - `train.jsonl`: Training data used for fine-tuning the model.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/anuliketat/llm-chatbot.git
   cd llm-chatbot
   ```
   
2. Create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

4. Fine-Tuning the Model
To fine-tune the GPT-3 model, use the llm_finetuned.py script:

Make sure you have your OpenAI API key set as an environment variable:

```bash
export OPENAI_API_KEY='your-api-key'
```

Run the fine-tuning script:

```bash
python scripts/fine_tune_model.py
```

This will fine-tune the GPT-3 model using the dataset provided in data/training_data.jsonl.

## Using the Chatbot
To interact with the chatbot, open the notebooks/Chatbot_Example.ipynb Jupyter notebook and follow the instructions inside.

Start Jupyter Notebook:

```bash
jupyter notebook
```

Open Chatbot_Example.ipynb and run the cells to interact with the chatbot.
