import codecs
import re

filename = '论文终稿7.0_扩充测试版.txt'
with codecs.open(filename, 'r', 'gbk') as f:
    text = f.read()

# Make sure to look at the bottom of the document
parts = text.split('参考文献')
if len(parts) > 1:
    print(parts[-1][:2000])
else:
    print('Not found')
