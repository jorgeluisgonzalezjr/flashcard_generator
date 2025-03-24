# flashcard_generator
📌 Overview

This project is an AI-powered flashcard generator that helps users create study flashcards dynamically using OpenAI’s API. The application takes user input, processes it using prompt engineering techniques, and generates educational flashcards with questions and answers to enhance learning.

The application features two modes:

Create Mode: Allows users to generate flashcards based on a given topic using AI-generated content.
Study Mode: Enables users to review previously created flashcards interactively, reinforcing learning.

🚀 Features

Create Mode for generating AI-powered flashcards.
Study Mode for reviewing and practicing flashcards.
Utilizes OpenAI’s API to create concise and informative study material.
Built with Gradio Blocks for an interactive user interface.
Optimized prompt engineering techniques for improved flashcard quality.
🛠️ Technologies Used

🐍 Python

⚙️ Gradio (for UI)

🤖 OpenAI API (for AI-generated content)

📓 Jupyter Notebook (for testing and development)


# Option 1: Using conda:

Install [Anaconda](https://www.anaconda.com/) or [Miniconda](https://www.anaconda.com/docs/getting-started/miniconda/install)

Create and activate the environment:
``` bash
conda env create -f environment.yml
conda activate llm-flashcards

```

# if imports are not working try using line below  to update terminal to grab dependices from environment.yml 
``` bash
conda env update --file environment.yml --prune 
```

Create a .env file in the root directory with your OpenAI credentials:
``` bash
OPENAI_API_KEY=your-api-key-here
OPENAI_API_BASE=your-api-base-here  # Optional if using the default OpenAI endpoint
```

Start the application:
``` python
python app/main.py
```

# Option 2: Using pip:
Create a virtual environment:

``` bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install dependencies:

``` bash
pip install openai python-dotenv pandas gradio vcrpy pytest
```

Configure OpenAI credentials

Start the application:
``` python
python app/main.py
```

