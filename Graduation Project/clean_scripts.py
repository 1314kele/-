import codecs
import re

for filename in ['./demo/templates/registration/login.html', './demo/templates/marketplace/register.html']:
    with codecs.open(filename, 'r', 'utf-8') as f:
        text = f.read()
    
    # Remove the whole <script>...</script> tag I added
    text = re.sub(r'<!-- 校园邮箱轻量化验证脚本 -->\s*<script>.*?</script>\s*', '', text, flags=re.DOTALL)
    
    with codecs.open(filename, 'w', 'utf-8') as f:
        f.write(text)

print('Cleaned previous scripts')
