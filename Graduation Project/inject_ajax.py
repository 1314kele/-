import os

path = 'demo/templates/marketplace/message_list.html'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

ajax_script = """
    // --- 实时消息无感刷新轮询脚本 ---
    setInterval(function() {
        fetch('{% url "check_new_messages" %}')
        .then(response => response.json())
        .then(data => {
            if (data.has_new) {
                // 发现新消息，静默重新拉取当前页面以更新消息列表DOM
                fetch(window.location.href)
                .then(res => res.text())
                .then(html => {
                    var parser = new DOMParser();
                    var doc = parser.parseFromString(html, 'text/html');
                    
                    // 无刷新替换消息主体容器
                    var newContent = doc.getElementById('messageTabsContent').innerHTML;
                    document.getElementById('messageTabsContent').innerHTML = newContent;
                    
                    // 无刷新替换顶部未读数量角标
                    var newReceivedTab = doc.getElementById('received-tab').innerHTML;
                    if(newReceivedTab) {
                        document.getElementById('received-tab').innerHTML = newReceivedTab;
                    }
                    
                    console.log('检测到新消息，列表已自动刷新');
                });
            }
        }).catch(err => console.log('消息轮询异常:', err));
    }, 3000); // 每 3 秒拉取一次
"""

# inject ajax_script just before {% endblock %}
if '实时消息无感刷新轮询脚本' not in text:
    target = "{% endblock %}"
    if target in text:
        new_text = text.replace(target, ajax_script + "\n" + target)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_text)
        print('Injected AJAX script in message_list.html')
    else:
        print('Could not find {% endblock %}')
else:
    print('AJAX already injected.')
