import codecs
import re

filename = '论文终稿7.0_扩充测试版.txt'
with codecs.open(filename, 'r', 'gbk') as f:
    text = f.read()

match = re.search(r'参考文献(.*)', text, re.DOTALL)
if match:
    print(match.group(1).strip()[:1000]) # Print first 1000 chars of references
else:
    print("参考文献 section not found")
