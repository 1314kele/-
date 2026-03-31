import os

path = 'demo/templates/marketplace/message_list.html'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# Replace the incorrectly escaped quotes with proper single quotes
new_text = text.replace("{% url \\'send_message\\'", "{% url 'send_message'")

with open(path, 'w', encoding='utf-8') as f:
    f.write(new_text)

print('Error fixed in template.')
