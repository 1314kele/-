import codecs

filename = './demo/marketplace/views.py'
with codecs.open(filename, 'r', 'utf-8') as f:
    text = f.read()

text = text.replace(
    '''        if form.is_valid():
            email = form.cleaned_data.get('email', '')''',
    '''        if form.is_valid():
            email = request.POST.get('email', '')'''
)

text = text.replace(
    '''            user = form.save()

            # 记录注册事件''',
    '''            user = form.save()
            user.email = email
            user.save()

            # 记录注册事件'''
)

with codecs.open(filename, 'w', 'utf-8') as f:
    f.write(text)

print('Updated views.py')
