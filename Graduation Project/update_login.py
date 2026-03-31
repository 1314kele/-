import codecs

filename = './demo/templates/registration/login.html'
with codecs.open(filename, 'r', 'utf-8') as f:
    text = f.read()

# Add JS script before {% endblock %}
js_code = '''
<!-- 校园邮箱轻量化验证脚本 -->
<script>
document.addEventListener('DOMContentLoaded', function() {
    var form = document.querySelector('form');
    var usernameInput = document.getElementById('id_username');
    
    // 更新Label提示
    var label = document.querySelector('label[for="id_username"]');
    if (label) {
        label.innerText = '校园邮箱（用户名）';
    }
    if (usernameInput) {
        usernameInput.placeholder = '学号@ncjti.edu.cn (如: 20220210270411@ncjti.edu.cn)';
    }

    form.addEventListener('submit', function(e) {
        var username = usernameInput.value.trim();
        // 允许管理员和已有测试账号绕过（兼容已有的结构），对于邮箱格式严格校验
        var emailRegex = /^[a-zA-Z0-9_.-]+@ncjti\.edu\.cn$/;
        
        // 如果包含@符号，则必须是指定的校园邮箱格式
        if (username.indexOf('@') !== -1) {
            if (!emailRegex.test(username)) {
                e.preventDefault();
                alert('【格式错误】\\n请输入正确的校园邮箱！\\n格式要求：学号@ncjti.edu.cn\\n例如：20220210270411@ncjti.edu.cn');
                usernameInput.focus();
            }
        } else if (username !== 'admin' && username !== 'testuser' && username.length > 0) {
           // 强制要求新用户使用邮箱登录（可选，为了不破坏之前可能存在的没带邮箱的老用户，这里可以选择弹窗确认或者直接放行，这里为了符合业务需求，直接阻挡除了特定特权账号外的普通非邮箱输入）
           var confirmAdmin = confirm('您未输入校园邮箱后缀！\\n除系统管理员外，学生请使用带 @ncjti.edu.cn 的校园邮箱登录。\\n是否继续尝试登录？');
           if(!confirmAdmin) {
               e.preventDefault();
               usernameInput.focus();
           }
        }
    });
});
</script>
{% endblock %}'''

new_text = text.replace('{% endblock %}', js_code)

with codecs.open(filename, 'w', 'utf-8') as f:
    f.write(new_text)

print('Updated login.html')
