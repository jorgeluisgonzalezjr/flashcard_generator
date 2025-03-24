import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)  # take environment variables from .env.

# Create a function to get the client, making it easier to mock or intercept in tests
def get_openai_client():
    return OpenAI(
        base_url=os.getenv("OPENAI_API_BASE"),
        api_key=os.getenv("OPENAI_API_KEY")
    )

# Default client for normal usage
client = get_openai_client()

def generate_flashcards(user_prompt, existing_cards_csv=None):
    """
    Make flashcards based on user prompt, with optional context from existing cards.
    
    Args:
        user_prompt (str): The user's prompt for what flashcards to generate
        existing_cards_csv (str, optional): CSV string of existing flashcards
    
    Returns:
        str: CSV formatted string of generated flashcards
    """
    #if there exist already flashcards provide them as an example
    if existing_cards_csv:
        context = (f"Use these set of flashcards as an example when generating flashcards:\n {existing_cards_csv}")

    #assign a role to be able to generate the flashcards
    messages = [
        {"role": "system", "content": """You are a helpful flashcard generator.
Generate flashcards in CSV format with 'front,back' as headers using Markdown Language.
Each card should have a question on the front and answer on the back.
Generate exactly 3 cards for each request.
 Strictly follow the CSV format. With each deck user should be able to save/delete content and use them for study mode."""},
         #ask the user to give a prompt to generate the flalshcards
        {"role": "user", "content": f"Generate new flashcards based on the following prompt:\n{user_prompt}"}
    ]

    #API call to OpenAI completition endpoint
    response = client.chat.completions.create(
        model="gpt-35-turbo-16k",
        messages=messages,
        temperature=0.3,
    )
    
    if response.choices is None or len(response.choices) == 0:
        return ""  # Return an empty string if the response is None or empty

    csv_data = response.choices[0].message.content.strip()

    rows = [line.split(",") for line in csv_data.split("\n") if line.strip()] # split csv string into one line

    cleaned_rows = [row[:2] for row in rows if len(row) >= 2] # ensures we have only 2 columns for cards

    csv_data = "\n".join([",".join(row) for row in cleaned_rows]) # joins all rows into one csv document
    
    if response.choices is None or len(response.choices) == 0:
        return "front,back\n"  # Return a valid CSV string with just the header

    return csv_data 

# user_prompt = "Create 5 flashcards about Chemistry"
# existing_cards_csv = None  # Optionally provide existing cards as context
# result = generate_flashcards(user_prompt, existing_cards_csv)
# print(result)