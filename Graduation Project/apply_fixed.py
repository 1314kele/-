import codecs

# LOGIN
file_login = 'demo/templates/registration/login.html'
with codecs.open(file_login, 'r', 'utf-8') as f:
    text = f.read()

# Add email field above password field
target_str = '<div class=\"mb-3\">\n                            <label for=\"id_password\"'
if target_str not in text:
    target_str = '<div class=\"mb-3\">\r\n                            <label for=\"id_password\"'

insert_str = '''<div class=\"mb-3\">
                            <label for=\"id_email\" class=\"form-label\">校园邮箱</label>
                            <input type=\"email\" name=\"email\" class=\"form-control\" id=\"id_email\" placeholder=\"格式：学号@ncjti.edu.cn\">
                        </div>

                        '''
text = text.replace(target_str, insert_str + target_str)

js_script = '''
<script>
document.addEventListener('DOMContentLoaded', function() {
    var form = document.querySelector('form');
    var emailInput = document.getElementById('id_email');
    
    if (form && emailInput) {
        form.addEventListener('submit', function(e) {
            var email = emailInput.value.trim();
            var emailRegex = /^[0-9a-zA-Z_.-]+@ncjti\\.edu\\.cn$/;
            
            if (email.length > 0 && !emailRegex.test(email)) {
                e.preventDefault();
                alert('❌ 校园邮箱格式不正确！\\n\\n【必须符合以下规定】\\n1. 必须使用本校分配的校园邮箱。\\n2. 格式示例：20220210270411@ncjti.edu.cn');
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

target_str2 = '<div class=\"mb-3\">\n                        <label for=\"{{ form.password1.id_for_label }}\"'
if target_str2 not in text2:
    target_str2 = '<div class=\"mb-3\">\r\n                        <label for=\"{{ form.password1.id_for_label }}\"'

insert_str2 = '''<div class=\"mb-3\">
                        <label for=\"id_email\" class=\"form-label\">校园邮箱 <span class=\"text-danger\">*</span></label>
                        <input type=\"email\" name=\"email\" class=\"form-control\" id=\"id_email\" placeholder=\"格式：学号@ncjti.edu.cn\" required>
                        <div class=\"form-text text-danger fw-bold\" style=\"color: #d9534f;\">必须使用校园邮箱注册</div>
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

# Make sure we don't mess up replacing multiple lines due to \r\n
# Just line by line replacing
lines = text3.split('\\n')
new_lines = []
for i, line in enumerate(lines):
    if \"email = form.cleaned_data.get('email', '')\" in line:
        # replace just this part
        line = line.replace(\"form.cleaned_data.get('email', '')\", \"request.POST.get('email', '')\")
    
    if \"user = form.save()\" in line:
        new_lines.append(line)
        # Check if it's inside the register function
        # Looking at previous context there's only one user = form.save() in register
        # We will dynamically attach user.email = email \n user.save()
        if 'register(request):' in text3[:text3.find(line)]: 
            spaces = line.split('user')[0]
            new_lines.append(spaces + 'user.email = email\\n' + spaces + 'user.save()')
        continue
        
    new_lines.append(line)

with codecs.open(file_view, 'w', 'utf-8') as f:
    f.write('\\n'.join(new_lines))

print("Injection complete!")
