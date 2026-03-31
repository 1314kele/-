import codecs

filename = './demo/templates/marketplace/register.html'
with codecs.open(filename, 'r', 'utf-8') as f:
    text = f.read()

# Add JS script before {% endblock %}
js_code = '''
<!-- 校园邮箱轻量化验证脚本 -->
<script>
document.addEventListener('DOMContentLoaded', function() {
    var form = document.querySelector('form');
    var usernameInput = document.getElementById('id_username');
    
    // 动态修改提示文字，无需修改后端复杂逻辑
    var label = document.querySelector('label[for="id_username"]');
    if (label) {
        label.innerText = '校园邮箱（用户名）';
    }
    
    // 给用户名下方的帮忙文本添加提示
    var helpText = usernameInput.nextElementSibling;
    if (helpText && helpText.classList.contains('form-text')) {
        helpText.innerHTML = '必须使用校园邮箱注册（格式：学号@ncjti.edu.cn）';
        helpText.style.color = '#d9534f';
        helpText.style.fontWeight = 'bold';
    }

    form.addEventListener('submit', function(e) {
        var username = usernameInput.value.trim();
        var emailRegex = /^[0-9a-zA-Z_.-]+@ncjti\.edu\.cn$/;
        
        if (!emailRegex.test(username)) {
            e.preventDefault();
            // 轻量化气泡/弹窗拦截
            alert('❌ 校园邮箱格式不正确！\\n\\n【必须符合以下规定】\\n1. 必须使用本校分配的校园邮箱。\\n2. 格式示例：20220210270411@ncjti.edu.cn');
            usernameInput.focus();
            // 在输入框添加红框样式提示
            usernameInput.style.border = '2px solid #d9534f';
            usernameInput.style.boxShadow = '0 0 5px rgba(217, 83, 79, 0.5)';
        } else {
            // 通过验证，恢复样式
            usernameInput.style.border = '';
            usernameInput.style.boxShadow = '';
        }
    });
    
    usernameInput.addEventListener('input', function() {
        this.style.border = '';
        this.style.boxShadow = '';
    });
});
</script>
{% endblock %}'''

new_text = text.replace('{% endblock %}', js_code)

with codecs.open(filename, 'w', 'utf-8') as f:
    f.write(new_text)

print('Updated register.html')
