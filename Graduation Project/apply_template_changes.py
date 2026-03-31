import codecs

# 1. Update login.html
login_file = './demo/templates/registration/login.html'
with codecs.open(login_file, 'r', 'utf-8') as f:
    login_text = f.read()

email_html = '''
                        <div class="mb-3">
                            <label for="id_email" class="form-label">校园邮箱</label>
                            <input type="email" name="email" class="form-control" id="id_email" placeholder="格式：学号@ncjti.edu.cn">
                        </div>'''

login_text = login_text.replace(
    '''<input type="text" name="username" class="form-control" id="id_username" required autofocus>\n                        </div>''',
    '''<input type="text" name="username" class="form-control" id="id_username" required autofocus>\n                        </div>''' + email_html
)

login_js = '''
<!-- 校园邮箱轻量化验证脚本 -->
<script>
document.addEventListener('DOMContentLoaded', function() {
    var form = document.querySelector('form');
    var emailInput = document.getElementById('id_email');
    
    // 如果是登录页面，校园邮箱可以作为辅助验证，或者只是记录/附加。用户需求：增加文本框并验证。
    form.addEventListener('submit', function(e) {
        var email = emailInput ? emailInput.value.trim() : '';
        var emailRegex = /^[0-9a-zA-Z_.-]+@ncjti\.edu\.cn$/;
        
        if (email.length > 0 && !emailRegex.test(email)) {
            e.preventDefault();
            alert('❌ 校园邮箱格式不正确！\\n\\n【必须符合以下规定】\\n1. 必须使用本校分配的校园邮箱。\\n2. 格式示例：20220210270411@ncjti.edu.cn');
            emailInput.focus();
            emailInput.style.border = '2px solid #d9534f';
            emailInput.style.boxShadow = '0 0 5px rgba(217, 83, 79, 0.5)';
        }
    });

    if (emailInput) {
        emailInput.addEventListener('input', function() {
            this.style.border = '';
            this.style.boxShadow = '';
        });
    }
});
</script>
{% endblock %}
'''

login_text = login_text.replace('{% endblock %}', login_js)

with codecs.open(login_file, 'w', 'utf-8') as f:
    f.write(login_text)

# 2. Update register.html
register_file = './demo/templates/marketplace/register.html'
with codecs.open(register_file, 'r', 'utf-8') as f:
    register_text = f.read()

email_html_reg = '''
                    <div class="mb-3">
                        <label for="id_email" class="form-label">校园邮箱 <span class="text-danger">*</span></label>
                        <input type="email" name="email" class="form-control" id="id_email" placeholder="格式：学号@ncjti.edu.cn" required>
                        <div class="form-text" style="color: #d9534f; font-weight: bold;">必须使用校园邮箱注册</div>
                    </div>'''

register_text = register_text.replace(
    '''<div class="form-text">请输入您的用户名</div>\n                    </div>''',
    '''<div class="form-text">请输入您的用户名</div>\n                    </div>''' + email_html_reg
)

register_js = '''
<!-- 校园邮箱轻量化验证脚本 -->
<script>
document.addEventListener('DOMContentLoaded', function() {
    var form = document.querySelector('form');
    var emailInput = document.getElementById('id_email');

    form.addEventListener('submit', function(e) {
        var email = emailInput.value.trim();
        var emailRegex = /^[0-9a-zA-Z_.-]+@ncjti\.edu\.cn$/;
        
        if (!emailRegex.test(email)) {
            e.preventDefault();
            alert('❌ 校园邮箱格式不正确！\\n\\n【必须符合以下规定】\\n1. 必须使用本校分配的校园邮箱。\\n2. 后缀必须为 @ncjti.edu.cn');
            emailInput.focus();
            emailInput.style.border = '2px solid #d9534f';
            emailInput.style.boxShadow = '0 0 5px rgba(217, 83, 79, 0.5)';
        }
    });

    if (emailInput) {
        emailInput.addEventListener('input', function() {
            this.style.border = '';
            this.style.boxShadow = '';
        });
    }
});
</script>
{% endblock %}
'''

register_text = register_text.replace('{% endblock %}', register_js)

with codecs.open(register_file, 'w', 'utf-8') as f:
    f.write(register_text)

print('Updated both templates with separate email fields!')
