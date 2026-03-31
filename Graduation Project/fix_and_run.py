import os

with open('draw_actual_system_architecture_with_chinese.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("actual_system_architecture_with_chinese.png", "image/system_architecture.png")
content = content.replace("plt.show()", "# plt.show()")

with open('draw_actual_system_architecture_with_chinese_temp.py', 'w', encoding='utf-8') as f:
    f.write(content)

os.system('C:/Users/86150/AppData/Local/Programs/Python/Python38/python.exe draw_actual_system_architecture_with_chinese_temp.py')
