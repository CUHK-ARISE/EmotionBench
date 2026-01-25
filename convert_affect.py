import json

def convert_affect_values():
    # Read the JSON file
    with open('public/crowd.json', 'r') as f:
        data = json.load(f)

    # Get control values
    control_positive = data['Crowd']['Control']['Positive Affect']
    control_negative = data['Crowd']['Control']['Negative Affect']

    print(f"Control values - Positive: {control_positive}, Negative: {control_negative}")

    # Function to recursively process affect values
    def process_entry(entry, path=""):
        if 'Positive Affect' in entry and 'Negative Affect' in entry:
            # This is a leaf node with affect values
            old_positive = entry['Positive Affect']
            old_negative = entry['Negative Affect']

            entry['Positive Affect'] = control_positive + old_positive
            entry['Negative Affect'] = control_negative + old_negative

            print(f"  {path}: Positive {old_positive} → {entry['Positive Affect']}, Negative {old_negative} → {entry['Negative Affect']}")
        else:
            # This is a parent node, recurse into children
            for key, value in entry.items():
                if isinstance(value, dict):
                    process_entry(value, f"{path}/{key}" if path else key)

    # Process all entries except Control
    for emotion_key in data['Crowd']:
        if emotion_key != 'Control':
            print(f"\nProcessing {emotion_key}:")
            process_entry(data['Crowd'][emotion_key], emotion_key)

    # Write back to file
    with open('public/crowd.json', 'w') as f:
        json.dump(data, f, indent=4)

    print('\nConversion complete! File updated.')

if __name__ == '__main__':
    convert_affect_values()
