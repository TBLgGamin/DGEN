import csv
import pandas as pd
import cohere
import os
from dotenv import load_dotenv
from typing import Optional, List
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# Define color constants
PRIMARY_COLOR = Fore.WHITE
ACCENT_COLOR = Fore.CYAN
SECONDARY_COLOR = Fore.LIGHTGREEN_EX

def colored_print(text: str, color: str = Fore.RESET):
    print(f"{color}{text}{Style.RESET_ALL}")

def get_cohere_client() -> Optional[cohere.Client]:
    load_dotenv()
    api_key = os.getenv('COHERE_API_KEY')
    
    while not api_key:
        colored_print("Cohere API key not found in environment variables.", ACCENT_COLOR)
        api_key = input("Please enter your Cohere API key: ").strip()
    
    try:
        return cohere.Client(api_key)
    except cohere.CohereError as e:
        colored_print(f"Error initializing Cohere client: {e}", SECONDARY_COLOR)
        return None

def read_csv_sample(file_path: str, sample_size: int = 5) -> Optional[pd.DataFrame]:
    try:
        df = pd.read_csv(file_path)
        headers = df.columns.tolist()
        sample = df.tail(sample_size)
        return pd.DataFrame([headers] + sample.values.tolist())
    except FileNotFoundError:
        colored_print(f"Error: File '{file_path}' not found.", SECONDARY_COLOR)
    except pd.errors.EmptyDataError:
        colored_print(f"Error: File '{file_path}' is empty.", SECONDARY_COLOR)
    except Exception as e:
        colored_print(f"Error reading CSV file: {e}", SECONDARY_COLOR)
    return None

def analyze_dataset(co: cohere.Client, sample_df: pd.DataFrame, system_prompt: str) -> Optional[str]:
    sample_str = sample_df.to_string(index=False, header=False)
    try:
        response = co.chat(
            model="command-r-plus",
            message=f"Analyze this dataset sample:\n\n{sample_str}",
            temperature=0.1,
            chat_history=[{"role": "SYSTEM", "message": system_prompt}]
        )
        return response.text
    except cohere.CohereError as e:
        colored_print(f"Error during dataset analysis: {e}", SECONDARY_COLOR)
        return None

def expand_dataset(co: cohere.Client, sample_df: pd.DataFrame, analysis: str, system_prompt: str, num_new_rows: int) -> Optional[str]:
    sample_str = sample_df.to_string(index=False, header=False)
    try:
        response = co.chat(
            model="command-r-plus",
            message=f"Based on this sample dataset:\n\n{sample_str}\n\nAnd this analysis:\n{analysis}\n\nGenerate {num_new_rows} new rows for this dataset. Format the output as a CSV string without headers.",
            temperature=1,
            chat_history=[{"role": "SYSTEM", "message": system_prompt}]
        )
        return response.text
    except cohere.CohereError as e:
        colored_print(f"Error during dataset expansion: {e}", SECONDARY_COLOR)
        return None

def append_to_csv(file_path: str, new_data: str) -> None:
    try:
        with open(file_path, 'a', newline='') as f:
            writer = csv.writer(f)
            for row in csv.reader(new_data.splitlines()):
                writer.writerow(row)
    except IOError as e:
        colored_print(f"Error appending to CSV file: {e}", SECONDARY_COLOR)

def get_user_input(prompt: str, input_type: type) -> Optional[any]:
    while True:
        try:
            user_input = input(f"{PRIMARY_COLOR}{prompt}{Style.RESET_ALL}")
            return input_type(user_input)
        except ValueError:
            colored_print(f"Invalid input. Please enter a valid {input_type.__name__}.", SECONDARY_COLOR)
        except KeyboardInterrupt:
            colored_print("\nOperation cancelled by user.", ACCENT_COLOR)
            return None

def main():
    colored_print("Welcome to the Dataset Expander!", PRIMARY_COLOR)
    
    while True:
        co = get_cohere_client()
        if not co:
            colored_print("Failed to initialize Cohere client. Please try again.", SECONDARY_COLOR)
            continue
        break

    while True:
        input_file = get_user_input("Enter the path to your input CSV file: ", str)
        if not input_file:
            return

        sample_df = read_csv_sample(input_file)
        if sample_df is not None:
            break
        colored_print("Please try again with a valid CSV file.", ACCENT_COLOR)

    while True:
        target_rows = get_user_input("Enter the desired number of rows for the expanded dataset: ", int)
        if target_rows is not None and target_rows > 0:
            break
        colored_print("Please enter a positive integer.", ACCENT_COLOR)

    analyzer_prompt = "You are an AI agent that analyzes the csv provided by the user. The focus of your analysis should be on what the data is, how it is formatted, what each column stands for, and how new data should look like."
    expander_prompt = "You are an AI agent that generates new csv rows based on analysis results and sample data. Follow the exact formatting and you should NEVER output any extra text besides the formatted data. No confirmation, nothing JUST THE FORMATTED DATA! Do NOT explain your actions nor use quotations in your response."

    try:
        original_df = pd.read_csv(input_file)
    except Exception as e:
        colored_print(f"Error reading the original CSV file: {e}", SECONDARY_COLOR)
        return

    current_rows = len(original_df)
    colored_print(f"\nOriginal dataset has {current_rows} rows.", ACCENT_COLOR)

    rows_to_add = max(0, target_rows - current_rows)
    if rows_to_add == 0:
        colored_print("The dataset already has the desired number of rows or more. No expansion needed.", PRIMARY_COLOR)
        return

    colored_print(f"Will add {rows_to_add} new rows to the dataset.", ACCENT_COLOR)

    colored_print("\nAnalyzing the dataset...", ACCENT_COLOR)
    analysis = analyze_dataset(co, sample_df, analyzer_prompt)
    if analysis is None:
        return
    colored_print("Analysis complete.", ACCENT_COLOR)

    output_file = f"expanded_{os.path.basename(input_file)}"
    original_df.to_csv(output_file, index=False)

    rows_added = 0
    colored_print("Expanding dataset, this can take a while. Go take a break ;)", PRIMARY_COLOR)
    while rows_added < rows_to_add:
        new_rows = min(50, rows_to_add - rows_added)
        new_data = expand_dataset(co, sample_df, analysis, expander_prompt, new_rows)
        if new_data is None:
            colored_print("Failed to expand dataset. Exiting.", SECONDARY_COLOR)
            return
        append_to_csv(output_file, new_data)
        rows_added += new_rows
        colored_print(f"Progress: {rows_added}/{rows_to_add} rows added", ACCENT_COLOR)

    colored_print(f"\nDataset expansion complete. {rows_added} new rows added.", PRIMARY_COLOR)
    colored_print(f"Expanded dataset saved as '{output_file}'", SECONDARY_COLOR)

if __name__ == "__main__":
    main()