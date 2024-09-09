import json

def main():
    filepath = 'data/data.json'
    
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
            print(json.dumps(data, indent=2))  # Print formatted JSON
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {filepath}")

if __name__ == "__main__":
    main()
