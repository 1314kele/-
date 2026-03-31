import codecs
import re

filename = '论文终稿7.0_扩充测试版.txt'
with codecs.open(filename, 'r', 'gbk') as f:
    text = f.read()

new_refs = '''[1] Linden G, Smith B, York J. Amazon.com recommendations: Item-to-item collaborative filtering[J]. IEEE Internet computing, 2003, 7(1): 76-80.
[2] Django Software Foundation. Django Documentation[EB/OL]. https://docs.djangoproject.com/en/3.2/, 2022-04-01.
[3] 刘江. Django企业开发实战[M]. 北京: 机械工业出版社, 2020.
[4] 王珊, 萨师煊. 数据库系统概论[M]. 6版. 北京: 高等教育出版社, 2014.
[5] 项亮. 推荐系统实践[M]. 北京: 人民邮电出版社, 2012.
[6] 周志华. 机器学习[M]. 北京: 清华大学出版社, 2016.
[7] 冯登国. 信息安全技术[M]. 北京: 清华大学出版社, 2019.
[8] 孙强, 赵莉. 高校校园二手交易平台的设计与实现[J]. 电脑知识与技术, 2022, 18(12): 54-56.
[9] 陈艳, 李明. 基于协同过滤的商品推荐算法研究与应用[J]. 软件工程, 2021, 24(8): 21-25.
[10] 张晨光. 基于Django的电子商务网站设计与实现[D]. 北京: 北京交通大学, 2020.
[11] 李明. 二手商品交易平台的设计与实现[D]. 上海: 上海交通大学, 2019.
[12] 王强. 基于Python的Web应用开发技术研究[J]. 计算机科学与应用, 2021, 11(5): 1234-1242.'''

new_text = re.sub(r'\[1\]Django Software Foundation.*?1234-1242\.', new_refs, text, flags=re.DOTALL)

with codecs.open('论文终稿8.0_精简文献版.txt', 'w', 'gbk') as f:
    f.write(new_text)

print('Updated references!')
