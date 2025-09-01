import re

def extract_member_name_from_content(content):
    if not content:
        return None
    
    # Handle cases like "Susy MoncadaConfirmarAug 29" - extract just the name part
    name_match = re.match(r'^([A-Z][a-z]+ [A-Z][a-z]+)', content)
    if name_match:
        name = name_match.group(1)
        # Skip if it's a system word
        if not re.match(r'^(System|ClubOS|Confirm|Cancel|Reminder|Notification|Ok|Thanks|Yes|No)', name, re.IGNORECASE):
            return name
    
    return None

# Test with actual message content
test_messages = [
    "Susy MoncadaConfirmarAug 29",
    "Alejandra EspinozaOk thanksAug 29", 
    "Alejandra Espinoza😞Aug 29"
]

print("Testing name extraction:")
for msg in test_messages:
    name = extract_member_name_from_content(msg)
    print(f"'{msg}' -> '{name}'")

print("\nTesting regex directly:")
for msg in test_messages:
    match = re.match(r'^([A-Z][a-z]+ [A-Z][a-z]+)', msg)
    if match:
        print(f"'{msg}' -> '{match.group(1)}'")
    else:
        print(f"'{msg}' -> NO MATCH")
