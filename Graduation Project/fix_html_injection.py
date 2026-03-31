import codecs
import re

# 1. Update login.html
login_file = './demo/templates/registration/login.html'
with codecs.open(login_file, 'r', 'utf-8') as f:
    text = f.read()

# Check if email input is already there
if 'name="email"' not in text:
    old_pattern = r'(<input type="text" name="username" class="form-control" id="id_username" required autofocus>\s*</div>)'
    new_html = r'\1\n\n                        <div class="mb-3">\n                            <label for="id_email" class="form-label">校园邮箱 (选填)</label>\n                            <input type="email" name="email" class="form-control" id="id_email" placeholder="格式：学号@ncjti.edu.cn">\n                        </div>'
    text = re.sub(old_pattern, new_html, text)
    
    with codecs.open(login_file, 'w', 'utf-8') as f:
        f.write(text)
    print("Injected email into login.html")

# 2. Update register.html
reg_file = './demo/templates/marketplace/register.html'
with codecs.open(reg_file, 'r', 'utf-8') as f:
    text2 = f.read()

if '<input type="email" name="email"' not in text2:
    # Look for the username div block: <div class="form-text">...</div>\s*</div>
    old_pattern2 = r'(<div class="form-text">.*?</div>\s*</div>)'
    new_html2 = r'\1\n\n                    <div class="mb-3">\n                        <label for="id_email" class="form-label">校园邮箱 <span class="text-danger">*</span></label>\n                        <input type="email" name="email" class="form-control" id="id_email" placeholder="格式：学号@ncjti.edu.cn" required>\n                        <div class="form-text text-danger fw-bold">必须使用校园邮箱注册</div>\n                    </div>'
    text2 = re.sub(old_pattern2, new_html2, text2, count=1)
    
    with codecs.open(reg_file, 'w', 'utf-8') as f:
        f.write(text2)
    print("Injected email into register.html")
