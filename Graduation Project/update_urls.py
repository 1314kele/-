import os

path = 'demo/marketplace/urls.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

target = "path('messages/', views.message_list, name='message_list'),"
replacement = "path('messages/', views.message_list, name='message_list'),\n    path('api/messages/check/', views.check_new_messages, name='check_new_messages'),"

new_text = text.replace(target, replacement)
with open(path, 'w', encoding='utf-8') as f:
    f.write(new_text)

print('Url modified:', target in text, replacement in new_text)
