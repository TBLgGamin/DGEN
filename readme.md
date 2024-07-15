# Dataset Expander

This tool helps you expand your CSV datasets using AI. It's designed to be easy to use, even if you have no programming experience.

## Getting Started

### Step 1: Install Python

If you don't have Python installed on your computer:

1. Go to [python.org](https://www.python.org/downloads/)
2. Download the latest version for your operating system (Windows, macOS, or Linux)
3. Run the installer and follow the installation instructions

### Step 2: Download the Project Files

Make sure you have these files in the same folder:

- `main.py`
- `install.py`
- `requirements.txt`

### Step 3: Install Required Packages

1. Open your computer's terminal or command prompt
2. Navigate to the folder containing the project files
3. Run the following command:

   ```
   python install.py
   ```

   This will install all the necessary packages for the tool to work.

### Step 4: Get a Cohere API Key

1. Go to [cohere.ai](https://cohere.ai/)
2. Sign up for an account
3. Once logged in, find your API key in your account settings

### Step 5: Rename the .env file

1. Rename .env.copy to .env after filling the API Key field.

### Step 6: Run the Dataset Expander

1. In the terminal or command prompt, run:

   ```
   python main.py
   ```

2. Follow the prompts:
   - Provide the path to your CSV file
   - Specify how many rows you want in your expanded dataset

3. The tool will analyze your data and create a new, expanded CSV file in the same folder

## Tips

- Make sure your original CSV file is in the same folder as `main.py`
- The new, expanded file will be named `expanded_` followed by your original filename
- If something goes wrong, the tool will guide you through the process

## Troubleshooting

- If you see any error messages, read them carefully. They often provide hints about what went wrong.
- Make sure you have a stable internet connection, as the tool needs to communicate with Cohere's AI service.
- If you're having trouble, try running the `install.py` script again to ensure all packages are correctly installed.

## Need Help?

If you encounter any issues or have questions, please reach out to the project maintainer for assistance.

Happy data expanding!