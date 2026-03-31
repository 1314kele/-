import os

path = 'demo/templates/marketplace/send_message.html'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('联系卖家 - {{ product.title }}', '{% if receiver and receiver != product.seller %}回复 {{ receiver.username }} - {{ product.title }}{% else %}联系卖家 - {{ product.title }}{% endif %}')
text = text.replace('<h4 class="mb-0">联系卖家</h4>', '<h4 class="mb-0">{% if receiver and receiver != product.seller %}发消息给 {{ receiver.username }}{% else %}联系卖家{% endif %}</h4>')
text = text.replace('卖家：{% if receiver %}{{ receiver.username }}{% else %}{{ product.seller.username }}{% endif %}', '发送至：{% if receiver %}{{ receiver.username }}{% else %}{{ product.seller.username }}{% endif %}')
text = text.replace('请输入您想对卖家说的话...', '请输入消息内容...')

# Let's also enforce action attribute to definitely retain receiver_id if present
text = text.replace('<form method="post">', '<form method="post" action="{% if receiver %}?receiver_id={{ receiver.id }}{% endif %}">')

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated text.')
