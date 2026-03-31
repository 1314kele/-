import os

path = 'demo/demo/settings.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

if "'simpleui'" not in text and '"simpleui"' not in text:
    new_text = text.replace("INSTALLED_APPS = [", "INSTALLED_APPS = [\n    'simpleui',")
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_text)
    print('SimpleUI added to INSTALLED_APPS')
else:
    print('SimpleUI already there')
