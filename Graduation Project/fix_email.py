import codecs

filename = '论文终稿7.0_扩充测试版.txt'
with codecs.open(filename, 'r', 'gbk') as f:
    text = f.read()

new_text = text.replace('test@example.com', 'test@student.edu.cn')

with codecs.open(filename, 'w', 'gbk') as f:
    f.write(new_text)

print('Updated email to test@student.edu.cn')
