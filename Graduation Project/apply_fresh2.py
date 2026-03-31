import codecs

# 1. Update login.html
filename = './demo/templates/registration/login.html'
with codecs.open(filename, 'r', 'utf-8') as f:
    text = f.read()

target1 = '<div class="mb-3">\n                            <label for="id_username" class="form-label">'

new_field1 = '''
                        <div class="mb-3">
                            <label for="id_email" class="form-label">校园邮箱</label>
                            <input type="email" name="email" class="form-control" id="id_email" placeholder="格式：学号@ncjti.edu.cn">
                        </div>
                        
                        <div class="mb-3">
                            <label for="id_username" class="form-label">'''

# Windows might use \r\n
target1_rn = '<div class="mb-3">\r\n                            <label for="id_username" class="form-label">'

if target1 in text:
    text = text.replace(target1, new_field1)
elif target1_rn in text:
    text = text.replace(target1_rn, new_field1)
else:
    print("WARNING: login.html target not found")

js_block1 = '''
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
{% endblock %}'''

text = text.replace('{% endblock %}', js_block1)

with codecs.open(filename, 'w', 'utf-8') as f:
    f.write(text)


# 2. Update register.html
filename2 = './demo/templates/marketplace/register.html'
with codecs.open(filename2, 'r', 'utf-8') as f:
    text2 = f.read()

target2 = '<div class="mb-3">\n                        <label for="{{ form.username.id_for_label }}" class="form-label">'
target2_rn = '<div class="mb-3">\r\n                        <label for="{{ form.username.id_for_label }}" class="form-label">'

new_field2 = '''
                    <div class="mb-3">
                        <label for="id_email" class="form-label">校园邮箱 <span class="text-danger">*</span></label>
                        <input type="email" name="email" class="form-control" id="id_email" placeholder="格式：学号@ncjti.edu.cn" required>
                        <div class="form-text text-danger fw-bold">必须使用校园邮箱注册</div>
                    </div>

                    <div class="mb-3">
                        <label for="{{ form.username.id_for_label }}" class="form-label">'''

if target2 in text2:
    text2 = text2.replace(target2, new_field2)
elif target2_rn in text2:
    text2 = text2.replace(target2_rn, new_field2)
else:
    print("WARNING: register.html target not found")

text2 = text2.replace('{% endblock %}', js_block1)

with codecs.open(filename2, 'w', 'utf-8') as f:
    f.write(text2)


# 3. Update views.py
filename3 = './demo/marketplace/views.py'
with codecs.open(filename3, 'r', 'utf-8') as f:
    text3 = f.read()

text3 = text3.replace(
    '''            email = form.cleaned_data.get('email', '')''',
    '''            email = request.POST.get('email', '')'''
)
text3 = text3.replace(
    '''            user = form.save()\n\n            # 璁板綍娉ㄥ唽浜嬩欢''',
    '''            user = form.save()\n            user.email = email\n            user.save()\n\n            # 璁板綍娉ㄥ唽浜嬩欢'''
)
text3 = text3.replace(
    '''            user = form.save()\r\n\r\n            # 璁板綍娉ㄥ唽浜嬩欢''',
    '''            user = form.save()\r\n            user.email = email\r\n            user.save()\r\n\r\n            # 璁板綍娉ㄥ唽浜嬩欢'''
)

with codecs.open(filename3, 'w', 'utf-8') as f:
    f.write(text3)

print("Done resetting everything!")
