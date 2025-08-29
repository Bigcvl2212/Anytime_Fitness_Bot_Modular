# Read the file
with open('src/routes/training.py', 'r') as f:
    content = f.read()

# Replace the problematic line
old_line = "        logger.info(f\"� Payment status: {payment_details.get('status')}, Amount owed: ${payment_details.get('amount_owed', 0)}\")"
new_line = "        logger.info(f\"� Payment status: Processing {len(agreements)} agreements, Amount owed: TBD\")"

content = content.replace(old_line, new_line)

# Write back
with open('src/routes/training.py', 'w') as f:
    f.write(content)

print('Fixed the payment_details reference')
