# script to remove non-code text like license headers and email addresses

import json
import sys 

def load_data(filepath):
    """Load JSON data from a file."""
    with open(filepath, 'r') as file:
        data = json.load(file)
    return data

def save_data(data, filepath):
    """Save JSON data to a file."""
    with open(filepath, 'w') as file:
        json.dump(data, file, indent=4)

def clean_data(data):
    """Remove entries containing specific copyright or license notifications."""
    keywords = ["GNU General Public License", "MIT", "Copyright", "express or implied", "applicable law", "warranty", "@gmail.com", "CLIENT_SECRET =", "client_secret ="]
    return [entry for entry in data if not any(keyword in entry['text'] for keyword in keywords)]

def main():
    if len(sys.argv) != 2:
        print("Usage: python clean_dataset.py <filepath>")
        sys.exit(1)

    filepath = sys.argv[1]
    data = load_data(filepath)
    cleaned_data = clean_data(data)
    new_filepath = f"{filepath.rsplit('.', 1)[0]}_clean.json"
    save_data(cleaned_data, new_filepath)
    print(f"Cleaned data saved to {new_filepath}")

if __name__ == "__main__":
    main()
