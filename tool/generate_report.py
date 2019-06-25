# -*- coding：utf-8 -*-
# &Author  AnFany

#  生成数据集报告的主程序

from docx import Document  # 写入.word
from docx.shared import Inches  #
import io
import pandas as pd
import numpy as np
import auxiliary_fuction as a_f  # 辅助函数
import data_report_config as drc  # 数据报告的配置
import read_data as data  # 数据文件


# WORD版数据报告
DOC = Document()
DOC.add_heading('%s:数据分析报告' % drc.DATA_NAME, 0)  # word文档的标题


class VIEW():

    def __init__(self):
        """
        生成.word版的数据报告
        """
        # 需要进行分析的数据，DataFrame格式
        self.data = data.DataSet
        # 数据集中的目标字段
        self.name = drc.TARGET_NAME
        # 值的类型为数值型，但是看作离散性特征的字段名称的列表
        self.f_list = drc.TYPE_LIST
        # 存储图片的路径
        self.path = drc.SAVE_PATH
        # 数据报告的名称
        self.report_name = drc.DATA_NAME
        # 类别型特征中值的个数超过阈值就不再进行展示,需要进行特殊处理
        self.type_count = drc.THRESHOLD_VALUE
        # 缺失值的展示标识
        self.miss_name = '缺失值'
        # 缺失值字段的字典
        self.miss = self.overview()
        # 只有一个值的特征字段
        self.one = self.distribution_feature()
        # 需要进行特殊处理的特征
        self.special = self.relation_feature_with_target()

    def overview(self):
        """
        数据概览，以及缺失值的信息
        :return:
        """
        miss_dict = {}
        for column_name in self.data.columns:
            length = self.data[column_name].count()
            if length != len(self.data):
                miss_dict[column_name] = '缺失率：%.3f' % (1 - length / len(self.data))

        DOC.add_heading('一、数据概览', level=1)
        buffer = io.StringIO()
        self.data.info(buf=buffer)
        s = buffer.getvalue()
        DOC.add_paragraph('%s' % s)
        print('一、数据概览：完毕')

        DOC.add_heading('二、缺失值分析', level=1)
        if miss_dict:
            DOC.add_paragraph('含有缺失值的特征：\n%s' % sorted(miss_dict.items(), key=lambda x: x[1], reverse=True))
        else:
            DOC.add_paragraph('所有特征均没有缺失值')
        print('二、缺失值分析：完毕')
        return miss_dict

    def distribution_feature(self):
        """
        单一特征的数据分布，数值型采用直方图，类别型用柱状图，
        对于数值型特征，删除缺失值。对于类别型特征，缺失值看作一类
        只有一个值的字段，无论是数值型还是类别型，均不绘制图
        :return: 以字段名命名的图
        """
        DOC.add_heading('三、每个字段的值的分布', level=1)
        # 只有一个值的字段，无论字段的属性是什么，均不绘制图
        one_number_list = []
        for key in self.data:
            # 类别型特征
            if self.data[key].dtype == object or key in self.f_list:
                plot_data = self.data[key]
                if len(set(list(plot_data.values))) != 1:
                    # 缺失值变为自定义的类别
                    plot_data = plot_data.replace(np.nan, self.miss_name).values
                    # 产生数据
                    label_data, num_data = a_f.generate_bar(plot_data)
                    if key in self.miss:
                        # 获取图片的标题
                        if key == self.name:
                            title = '目标字段' + key + ', %s' % self.miss[key]
                        else:
                            title = '特征字段' + key + ', %s' % self.miss[key]
                    else:
                        # 绘制柱状图
                        if key == self.name:
                            title = '目标字段' + key
                        else:
                            title = '特征字段' + key
                    # 绘制柱状图
                    a_f.plot_bar(label_data, num_data, title, key)
                    # 输出到数据报告
                    DOC.add_paragraph('特征字段：' + key, style='List Number')
                    DOC.add_picture(r'%s/%s.png' % (self.path, key), width=Inches(5.8))
                else:
                    one_number_list.append(key)
                    DOC.add_paragraph('字段%s只有一个值' % key, style='List Number')

            else:
                # 绘制直方图
                plot_data = self.data[key].dropna().values  # 删除缺失值
                if len(set(list(plot_data))) != 1:
                    if key in self.miss:
                        if key == self.name:
                            title = '目标字段' + key + ', %s' % self.miss[key]
                        else:
                            title = '特征字段' + key + ', %s' % self.miss[key]
                    else:
                        if key == self.name:
                            title = '目标字段' + key
                        else:
                            title = '特征字段' + key
                    # 绘制直方图
                    a_f.plot_hist(plot_data, title, key)
                    # 输出到数据报告
                    DOC.add_paragraph('字段：' + key, style='List Number')
                    DOC.add_picture(r'%s/%s.png' % (self.path, key), width=Inches(5.8))
                else:
                    one_number_list.append(key)
                    DOC.add_paragraph('字段%s只有一个值' % key, style='List Number')
        print('三、单个字段的值的分布：完毕')
        return one_number_list

    def relation_feature_with_target(self):
        """
        获取每个特征字段与目标字段之间的关系：
        对于数值型特征，删除缺失值。对于类别型特征，缺失值看作一类
        如果目标字段是类别型特征，特征是类别型的，用分类柱状图；特征是数值的，用概率密度图
        如果目标字段是数值型特征，特征是类别型的，用概率密度图；特征是数值的，用散点图
        只有一个值的字段不绘制图
        :return: 绘制的图
        """
        DOC.add_heading('四、每个特征字段与目标字段之间的关系', level=1)
        # 存储值较多的类别型特征的字段名
        special_list = []  # 这些字段需要特殊处理
        for key in self.data:
            if key != self.name:
                if key not in self.one:
                    # 目标字段的值为类别型
                    if self.data[self.name].dtype == object or self.name in self.f_list:
                        # 特征字段值为类别型
                        if self.data[key].dtype == object or key in self.f_list:
                            # 类别的值
                            xdata = list(self.data[self.name].values)
                            if key in self.miss:
                                ydata = self.data[key].fillna('缺失值')
                            else:
                                ydata = self.data[key]

                            # 判断该类型中不同值的个数
                            if len(set(ydata.values)) > self.type_count:
                                print(len(set(ydata.values)), self.type_count)
                                special_list.append(key)
                                continue
                            # 生成数据
                            x_data, y_data, data_dict = a_f.generate_bar_type(xdata, ydata)

                            if key not in self.miss:
                                title = "字段%s：不同类别的占比" % key
                            else:
                                title = "字段%s：不同类别的占比" % key + ' %s' % self.miss[key]
                            # 绘制分类柱状图
                            a_f.plot_hist_with_type(x_data, y_data, data_dict, title, key + '_' + self.name)

                        # 特征字段值为数值型
                        else:
                            new_df = pd.DataFrame()
                            new_df['type'] = self.data[self.name]
                            new_df['num'] = self.data[key]
                            new_df = new_df.dropna(axis=0, how='any')
                            x_data = new_df['type'].values
                            y_data = new_df['num'].values
                            data_dict = a_f.generate_data_for_plot_distribution(x_data, y_data)
                            # 获取标题
                            if key not in self.miss:
                                title = "字段%s：不同类别的分布" % key
                            else:
                                title = "字段%s：不同类别的分布" % key + ' %s' % self.miss[key]
                            # 绘制概率密度图
                            a_f.plot_density_with_type(data_dict, title, key + '_' + self.name, key)
                        # 输出数据报告
                        DOC.add_paragraph('关系: ' + key + ' VS ' + self.name, style='List Bullet')
                        DOC.add_picture(r'%s/%s_%s.png' % (self.path, key, self.name), width=Inches(5.8))
                    # 目标字段的值为数值型
                    else:
                        # 特征字段值为类别型
                        if self.data[key].dtype == object or key in self.f_list:
                            # 获取数据
                            new_df = pd.DataFrame()
                            new_df['num'] = self.data[self.name]
                            new_df['type'] = self.data[key]
                            new_df = new_df.dropna(axis=0, how='any')
                            x_data = new_df['type'].values
                            y_data = new_df['num'].values
                            # 判断该类型中不同值的个数
                            if len(set(y_data)) > self.type_count:
                                print(len(set(y_data)),  self.type_count)
                                special_list.append(key)
                                continue
                            data_dict = a_f.generate_data_for_plot_distribution(x_data, y_data)
                            # 获取标题
                            if key not in self.miss:
                                title = "特征%s：分布" % key
                            else:
                                title = "特征%s：分布" % key + ' %s' % self.miss[key]
                            # 绘制概率密度图
                            a_f.plot_density_with_type(data_dict, title, key + '_' + self.name, self.name)

                        # 特征字段值为数值型
                        else:
                            # 获取数据
                            new_df = pd.DataFrame()
                            new_df['num1'] = self.data[self.name]
                            new_df['num2'] = self.data[key]
                            new_df = new_df.dropna(axis=0, how='any')
                            data1 = new_df['num1'].values
                            data2 = new_df['num2'].values
                            # 获取标题
                            if key not in self.miss:
                                title = "特征%s：散点" % key
                            else:
                                title = "特征%s：散点" % key + ' %s' % self.miss[key]
                            # 绘制散点图
                            a_f.plot_scatter(data1, data2, title, key + '_' + self.name, self.name, key)

                        # 输出数据报告
                        DOC.add_paragraph('关系: ' + key + ' VS ' + self.name, style='List Bullet')
                        DOC.add_picture(r'%s/%s_%s.png' % (self.path, key, self.name), width=Inches(5.8))
        print('四、每个特征字段与目标字段之间的关系：完毕')
        return special_list

    def report_other(self):
        DOC.add_heading('五、其他', level=1)
        DOC.add_paragraph('类别型特征中，不同值较多的字段：')
        for j in self.special:
            DOC.add_paragraph('字段%s，不同值的个数：%d' % (j, len(set(self.data[j].values))), style='List Bullet')
        return print('五、其他：完毕')


# 主函数
if __name__ == "__main__":

    data_report = VIEW()
    data_report.report_other()
    DOC.save(r'%s/%s数据报告.docx' % (data_report.path, data_report.report_name))
    print('数据报告生成完毕')

