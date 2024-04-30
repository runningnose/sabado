import json
import re

def fix_json(file_path):
    try:
        # Read the contents of the original file
        with open(file_path, 'r') as file:
            content = file.read()

        # Replace single quotes with double quotes
        content = content.replace("'", '"')

        # Escape unescaped double quotes within strings
        # This regex finds double quotes that are not preceded by a backslash and replaces them
        content = re.sub(r'(?<!\\)"', r'\"', content)
        
        # Attempt to parse the JSON
        data = json.loads(content)
        
        # Write the fixed JSON back to a new file
        with open('fixed_json_output.json', 'w') as file:
            json.dump(data, file, indent=4)
        
        print("JSON fixed and written to 'fixed_json_output.json'")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
fix_json('links.json')

