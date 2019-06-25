# -*- coding：utf-8 -*-
# &Author  AnFany

#  更改此程序中的设置，运行generate_report.py生成.word格式的数据报告


# 数据文件的路径
FILE_PATH = r'E:\tensorflow_Learn\machine_learning_competitions\kaggle\titanic'

# 数据文件的主名
FILE_NAME = 'train'

# 数据文件的扩展名(支持csv，excel)
FORMAT = 'csv'

# 目标字段名
TARGET_NAME = 'Survived'

# 不用读取的特征字段列表
REDUNDANT_NAME_LIST = ['PassengerId']

# 字段的值为数值型，实际为类别型特征的字段列表
TYPE_LIST = ['Survived', 'Pclass', 'SibSp', 'Parch']


# 保存数据报告的图片以及数据报告的文件
SAVE_PATH = r'E:\tensorflow_Learn\machine_learning_competitions\kaggle\titanic\report'


# 数据集名称
DATA_NAME = '泰坦尼克号乘客生还数据集'

# 类别型字段中，值的个数超过定值，就不再进行展示
THRESHOLD_VALUE = 20







