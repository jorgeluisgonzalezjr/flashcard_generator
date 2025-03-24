import gradio as gr
import pandas as pd
import os
from pathlib import Path
from flashcard_generator import generate_flashcards

def load_decks():
    """Load all CSV files from data/ directory as flashcard decks"""
    decks = {}
    data_dir = Path("data")

    if not data_dir.exists():
        return {}

    for file in data_dir.glob("*.csv"):
        deck_name = file.stem
        df = pd.read_csv(file)
        if 'front' in df.columns and 'back' in df.columns:
            decks[deck_name] = df[['front', 'back']].values.tolist()

    return decks

class FlashcardApp:
    def __init__(self):
        self.decks = load_decks()
        self.current_card_index = 0
        self.showing_front = True
    
    def get_deck_names(self):
        return list(self.decks.keys())
    
    def load_card(self, deck_name):
        # Ensure deck_name is a string, not a list
        if isinstance(deck_name, list) and deck_name:
            deck_name = deck_name[0]
            
        if not deck_name or deck_name not in self.decks:
            return "<div class='card-container'>Please select a deck</div>", "0/0"
        
        self.current_card_index = 0
        self.showing_front = True
        current_deck = self.decks[deck_name]
        
        # Handle empty deck case
        if len(current_deck) == 0:
            return "<div class='card-container'>This deck is empty. Add cards in Create Mode.</div>", "0/0"
            
        return (f"<div class='card-container'>{current_deck[0][0]}</div>", 
                f"{self.current_card_index + 1}/{len(current_deck)}")
    
    def flip_card(self, deck_name):
        # Ensure deck_name is a string, not a list
        if isinstance(deck_name, list) and deck_name:
            deck_name = deck_name[0]
            
        if not deck_name or deck_name not in self.decks:
            return "<div class='card-container'>Please select a deck</div>", "0/0"
        
        current_deck = self.decks[deck_name]
        
        # Handle empty deck case
        if len(current_deck) == 0:
            return "<div class='card-container'>This deck is empty. Add cards in Create Mode.</div>", "0/0"
            
        current_card = current_deck[self.current_card_index]
        self.showing_front = not self.showing_front
        
        content = current_card[0] if self.showing_front else current_card[1]
        return (f"<div class='card-container'>{content}</div>",
                f"{self.current_card_index + 1}/{len(current_deck)}")
    
    def navigate_card(self, deck_name, direction):
        # Ensure deck_name is a string, not a list
        if isinstance(deck_name, list) and deck_name:
            deck_name = deck_name[0]
            
        if not deck_name or deck_name not in self.decks:
            return "<div class='card-container'>Please select a deck</div>", "0/0"
        
        current_deck = self.decks[deck_name]
        
        # Handle empty deck case
        if len(current_deck) == 0:
            return "<div class='card-container'>This deck is empty. Add cards in Create Mode.</div>", "0/0"
            
        if direction == "next":
            self.current_card_index = (self.current_card_index + 1) % len(current_deck)
        else:  # previous
            self.current_card_index = (self.current_card_index - 1) % len(current_deck)
        
        self.showing_front = True
        return (f"<div class='card-container'>{current_deck[self.current_card_index][0]}</div>",
                f"{self.current_card_index + 1}/{len(current_deck)}")
    

def add_ai_cards_to_deck(prompt, current_deck_data):
    """
    Add AI-generated flashcards to the current deck
    
    Args:
        prompt (str): User prompt for generating cards
        current_deck_data (list): Current deck data as a list of lists
    
    Returns:
        list: Updated deck data with new flashcards added
    """
    if not prompt:
        return current_deck_data
    
    print(f"Current deck data: {current_deck_data}")
    try:
        # Convert existing cards to CSV string format
        existing_cards_csv = None
        if current_deck_data is not None and (
            (isinstance(current_deck_data, pd.DataFrame) and not current_deck_data.empty) or
            (not isinstance(current_deck_data, pd.DataFrame) and len(current_deck_data) > 0)
        ):
            existing_df = pd.DataFrame(current_deck_data, columns=['front', 'back'])
            existing_cards_csv = existing_df.to_csv(index=False)
        
        # Generate flashcards with context from existing cards
        new_cards_csv = generate_flashcards(prompt, existing_cards_csv)

        # Convert CSV string to DataFrame
        from io import StringIO
        new_cards_df = pd.read_csv(StringIO(new_cards_csv))
        
        # Convert the generated cards to a list of lists
        new_cards = new_cards_df.values.tolist()
        
        # Combine with existing cards - properly handle pandas DataFrame
        if isinstance(current_deck_data, pd.DataFrame):
            # If it's a DataFrame, convert to list of lists
            updated_deck = current_deck_data.values.tolist()
        else:
            # Otherwise use what was provided, or an empty list
            updated_deck = current_deck_data if current_deck_data is not None else []
        
        updated_deck.extend(new_cards)
        
        # Filter out rows where both front and back are empty or just whitespace
        updated_deck = [card for card in updated_deck if 
                       (isinstance(card[0], str) and card[0].strip()) or 
                       (isinstance(card[1], str) and card[1].strip())]
        
        return updated_deck
    
    except pd.errors.ParserError as e:
        # Handle CSV parsing errors
        print(f"Error parsing CSV data: {e}")
        return current_deck_data
    
    except (ValueError, TypeError) as e:
        # Handle other conversion errors
        print(f"Error processing flashcard data: {e}")
        return current_deck_data
    
    except Exception as e:
        # Catch any other unexpected errors
        print(f"Unexpected error adding AI cards: {e}")
        return current_deck_data

def create_interface():
    app = FlashcardApp()
    
    with gr.Blocks(css="""
        .card-container {
            width: 100%;
            min-height: 200px;
            text-align: center;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            background: #f5f5f5;
            border-radius: 8px;
            margin: 20px 0;
            padding: 20px;
            color: #000000;
        }
    """) as interface:
        gr.Markdown("# Flashcard App")
        
        with gr.Tabs():
            with gr.Tab("Study Mode"):
                with gr.Row():
                    deck_dropdown = gr.Dropdown(
                        choices=app.get_deck_names(),
                        label="Select Deck",
                        interactive=True
                    )
                    refresh_btn = gr.Button("🔄 Refresh", scale=1)
                
                card_text = gr.HTML(
                    label="Card Content",
                    value="<div class='card-container'>Select a deck to begin</div>",
                    show_label=False
                )
                
                card_counter = gr.Textbox(
                    label="Card Progress",
                    interactive=False,
                    value="0/0"
                )
                
                with gr.Row():
                    prev_btn = gr.Button("Previous")
                    flip_btn = gr.Button("Flip")
                    next_btn = gr.Button("Next")

            with gr.Tab("Create Mode"):
                with gr.Row():
                    new_deck_name = gr.Textbox(
                        label="New Deck Name",
                        placeholder="Enter deck name",
                        interactive=True
                    )
                    create_deck_btn = gr.Button("Create Deck")

                with gr.Row():
                    create_deck_dropdown = gr.Dropdown(
                        choices=app.get_deck_names(),
                        label="Select Deck to Edit",
                        interactive=True
                    )
                    delete_deck_btn = gr.Button("Delete Deck", variant="stop")
                
                deck_df = gr.Dataframe(
                    headers=["front", "back"],
                    datatype=["str", "str"],
                    label="Edit Deck Content",
                    col_count=(2, "fixed"),
                    interactive=True,
                    value=[]
                )
                
                save_btn = gr.Button("Save Changes")
                
                gr.Markdown("### Generate Cards with AI")
                
                with gr.Row():
                    ai_prompt = gr.Textbox(
                        label="What flashcards would you like to generate?",
                        placeholder="e.g., Add 3 flashcards about Python basics",
                        interactive=True
                    )
                    generate_btn = gr.Button("Generate Cards")
                
                gr.Markdown("""
                Examples:
                - Add flashcards about Python
                - Generate flashcards on history
                - Create cards about science topics
                """)

        # Event handlers for Study Mode
        deck_dropdown.change(
            fn=lambda x: app.load_card(x),
            inputs=[deck_dropdown],
            outputs=[card_text, card_counter]
        )
        
        def refresh_decks(current_deck):
            app.decks = load_decks()
            deck_names = app.get_deck_names()
            
            selected_deck = current_deck if current_deck in deck_names else None
            card_content, counter = app.load_card(selected_deck) if selected_deck else ("<div class='card-container'>Select a deck to begin</div>", "0/0")
            
            return deck_names, selected_deck, card_content, counter

        refresh_btn.click(
            fn=refresh_decks,
            inputs=[deck_dropdown],
            outputs=[deck_dropdown, card_text, card_counter]
        )
        
        flip_btn.click(
            fn=lambda x: app.flip_card(x),
            inputs=[deck_dropdown],
            outputs=[card_text, card_counter]
        )
        
        prev_btn.click(
            fn=lambda x: app.navigate_card(x, "prev"),
            inputs=[deck_dropdown],
            outputs=[card_text, card_counter]
        )
        
        next_btn.click(
            fn=lambda x: app.navigate_card(x, "next"),
            inputs=[deck_dropdown],
            outputs=[card_text, card_counter]
        )

        # Event handlers for Create Mode
        def load_deck_for_editing(deck_name):
            # Ensure deck_name is a string, not a list
            if isinstance(deck_name, list) and deck_name:
                deck_name = deck_name[0]
            
            if not deck_name or deck_name not in app.decks:
                return gr.Dataframe(value=[["", ""]])
            
            deck_data = app.decks[deck_name]
            # Convert the deck data to a list of lists for the dataframe
            df_data = [[card[0], card[1]] for card in deck_data]
            return gr.Dataframe(value=df_data)

        def save_deck_changes(deck_name, data):
            if not deck_name:
                return gr.Dropdown(choices=app.get_deck_names()), gr.Dropdown(choices=app.get_deck_names())
            
            updated_deck = add_ai_cards_to_deck(ai_prompt, data)  # Add this line to include the generated flashcards

            df = pd.DataFrame(updated_deck, columns=['front', 'back'])  # Use the updated_deck instead of data
            os.makedirs('data', exist_ok=True)
            df.to_csv(f'data/{deck_name}.csv', index=False)

            # Reload decks and update dropdowns
            app.decks = load_decks()
            new_choices = app.get_deck_names()
            return gr.Dropdown(choices=new_choices, value=deck_name), gr.Dropdown(choices=new_choices, value=deck_name)

        save_btn.click(
            fn=save_deck_changes,
            inputs=[create_deck_dropdown, deck_df],
            outputs=[deck_dropdown, create_deck_dropdown]
        )

        # Additional event handlers for Create Mode
        def create_new_deck(deck_name):
            if not deck_name:
                return gr.Dropdown(choices=app.get_deck_names()), gr.Dropdown(choices=app.get_deck_names()), ""
            
            # Create empty CSV file
            df = pd.DataFrame(columns=['front', 'back'])
            os.makedirs('data', exist_ok=True)
            df.to_csv(f'data/{deck_name}.csv', index=False)
            
            # Reload decks and update dropdowns
            app.decks = load_decks()
            new_choices = app.get_deck_names()
            return gr.Dropdown(choices=new_choices, value=deck_name), gr.Dropdown(choices=new_choices, value=deck_name), ""

        def delete_deck(deck_name):
            if not deck_name:
                return gr.Dropdown(choices=app.get_deck_names()), gr.Dropdown(choices=app.get_deck_names()), []
            
            # Delete the CSV file
            try:
                os.remove(f'data/{deck_name}.csv')
            except FileNotFoundError:
                pass
            
            # Reload decks and update dropdowns
            app.decks = load_decks()
            new_choices = app.get_deck_names()
            return gr.Dropdown(choices=new_choices), gr.Dropdown(choices=new_choices), []

        create_deck_btn.click(
            fn=create_new_deck,
            inputs=[new_deck_name],
            outputs=[deck_dropdown, create_deck_dropdown, new_deck_name]
        )

        delete_deck_btn.click(
            fn=delete_deck,
            inputs=[create_deck_dropdown],
            outputs=[deck_dropdown, create_deck_dropdown, deck_df]
        )

        # AI flashcard generation handler
        def generate_ai_cards(prompt, deck_data):
            # Handle empty dataframe case
            if deck_data is None or len(deck_data) == 0:
                # Initialize with empty list but proper structure for pandas
                deck_data = []
            
            updated_deck = add_ai_cards_to_deck(prompt, deck_data)
            return gr.Dataframe(value=updated_deck), ""
        
        generate_btn.click(
            fn=generate_ai_cards,
            inputs=[ai_prompt, deck_df],
            outputs=[deck_df, ai_prompt]
        )
    
    return interface

if __name__ == "__main__":
    interface = create_interface()
    interface.launch()