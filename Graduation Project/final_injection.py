import codecs

# LOGIN
file_login = 'demo/templates/registration/login.html'
with codecs.open(file_login, 'r', 'utf-8') as f:
    text = f.read()

target_str = '<div class="mb-3">\n                            <label for="id_password"'
if target_str not in text:
    target_str = '<div class="mb-3">\r\n                            <label for="id_password"'

insert_str = '''<div class="mb-3">
                            <label for="id_email" class="form-label">校园邮箱 (非管理员必填)</label>
                            <input type="email" name="email" class="form-control" id="id_email" placeholder="格式：学号@ncjti.edu.cn">
                        </div>

                        '''
text = text.replace(target_str, insert_str + target_str)

js_script = '''
<!-- 校园邮箱验证 -->
<script>
document.addEventListener('DOMContentLoaded', function() {
    var form = document.querySelector('form');
    var emailInput = document.getElementById('id_email');
    var usernameInput = document.getElementById('id_username');
    
    if (form && emailInput) {
        form.addEventListener('submit', function(e) {
            var email = emailInput.value.trim();
            var username = usernameInput ? usernameInput.value.trim() : '';
            var emailRegex = /^[0-9a-zA-Z_.-]+@ncjti\\.edu\\.cn$/;
            
            // 允许管理员账号跳过邮箱验证
            if (username === 'admin' || username === 'testuser') {
                return; // 放行
            }
            
            if (!emailRegex.test(email)) {
                e.preventDefault();
                alert('【格式错误】\\n除管理员外，登录/注册请务必提供您的校园邮箱！\\n格式要求：学号@ncjti.edu.cn\\n例如：20220210270411@ncjti.edu.cn');
                emailInput.focus();
                emailInput.style.border = '2px solid #d9534f';
                emailInput.style.boxShadow = '0 0 5px rgba(217, 83, 79, 0.5)';
            }
        });

        emailInput.addEventListener('input', function() {
            this.style.border = '';
            this.style.boxShadow = '';
        });
    }
});
</script>
{% endblock %}
'''

text = text.replace('{% endblock %}', js_script)

with codecs.open(file_login, 'w', 'utf-8') as f:
    f.write(text)

# REGISTER
file_reg = 'demo/templates/marketplace/register.html'
with codecs.open(file_reg, 'r', 'utf-8') as f:
    text2 = f.read()

target_str2 = '<div class="mb-3">\n                        <label for="{{ form.password1.id_for_label }}"'
if target_str2 not in text2:
    target_str2 = '<div class="mb-3">\r\n                        <label for="{{ form.password1.id_for_label }}"'

insert_str2 = '''<div class="mb-3">
                        <label for="id_email" class="form-label">校园邮箱 <span class="text-danger">*</span></label>
                        <input type="email" name="email" class="form-control" id="id_email" placeholder="格式：学号@ncjti.edu.cn" required>
                        <div class="form-text text-danger fw-bold" style="color: #d9534f;">必须使用校园邮箱注册</div>
                    </div>

                    '''
text2 = text2.replace(target_str2, insert_str2 + target_str2)

text2 = text2.replace('{% endblock %}', js_script)

with codecs.open(file_reg, 'w', 'utf-8') as f:
    f.write(text2)

# VIEWS.PY
file_view = 'demo/marketplace/views.py'
with codecs.open(file_view, 'r', 'utf-8') as f:
    text3 = f.read()

text3 = text3.replace("email = form.cleaned_data.get('email', '')", "email = request.POST.get('email', '')")

# To accurately replace the user = form.save() in register
if "user = form.save()" in text3:
    user_save_idx = text3.find("user = form.save()")
    if user_save_idx != -1:
        text3 = text3[:user_save_idx] + "user = form.save()\n              user.email = email\n              user.save()" + text3[user_save_idx+18:]

with codecs.open(file_view, 'w', 'utf-8') as f:
    f.write(text3)

print('Injection script executed successfully!')
