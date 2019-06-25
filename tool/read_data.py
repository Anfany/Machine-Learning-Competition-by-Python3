# -*- coding：utf-8 -*-
# &Author  AnFany

# 读取数据的程序

import data_report_config as drc
import pandas as pd


class READ():

    def __init__(self):
        # 文件路径
        self.filepath = drc.FILE_PATH

        # 文件主名
        self.filename = drc.FILE_NAME

        # 文件格式
        self.format = drc.FORMAT

        # 不用读取的特征字段的列表
        self.reduntan_name = drc.REDUNDANT_NAME_LIST

    def read_data_from_file(self):
        """
        利用pd读取数据文件，得到的数据为DataFrame格式
        :return: DataFrame格式
        """
        if self.format == 'csv':
            data = pd.read_csv(r'%s\%s.%s' % (self.filepath, self.filename, self.format))
        elif self.format == 'excel':
            data = pd.read_excel(r'%s\%s.%s' % (self.filepath, self.filename, self.format))
        else:
            return print('数据文件格式不对')
        # 删除不必要的数据
        for name in self.reduntan_name:
            if name in data:
                del data[name]
        return data


read_data = READ()
#  读取数据
DataSet = read_data.read_data_from_file()


# 主函数
if __name__ == "__main__":
    print(DataSet.head())




