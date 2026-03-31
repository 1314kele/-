import re

path = 'demo/templates/marketplace/message_list.html'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

new_text = re.sub(
    r'<a href="{% url \'send_message\' message\.product\.id %}"(.*?)>回复</a>',
    r'<a href="{% url \'send_message\' message.product.id %}?receiver_id={{ message.sender.id }}"\1>回复</a>',
    text
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(new_text)

print('Updated reply link in message_list.html')
