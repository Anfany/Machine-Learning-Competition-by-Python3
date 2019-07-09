# -*- coding：utf-8 -*-
# &Author  AnFany


# 数据概览中需要的辅助函数：绘制图的函数，以及产生数据的函数
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt  # 绘图
from pylab import mpl  # 中文显示
from collections import Counter
import seaborn as sns
import matplotlib.gridspec as gridspec
import data_report_config as drc
mpl.rcParams['axes.unicode_minus'] = False  # 显示负号
plt.rcParams['font.family'] = ['Arial Unicode MS']


# 处理标签数据的函数,防止相邻的标签字符数过长，产生交叉，影响展示
def handle_str(x_data, length=8):
    """
    每间隔length个字符就换行
    :param x_data: 标签数据，列表
    :param length: 间隔数
    :return: 处理后的标签的列表
    """
    new_data = []
    for i in x_data:
        i = str(i)
        new_data.append(re.sub(r"(.{%d})" % length, "\\1-\n", i))
    return new_data


# 产生绘制柱状图需要的数据
def generate_bar(data):
    """
    产生绘制柱状图需要的数据
    :param data: 类别型特征数据
    :return: 标签数据，标签数据对应的数值数据（按照数值的降序排列）
    """
    data_dict = Counter(data)
    sort_dict = sorted(data_dict.items(), key=lambda x: x[1], reverse=True)
    x_data, y_data = [], []
    for j in sort_dict:
        x_data.append(j[0])
        y_data.append(j[1])
    return x_data, y_data


# 绘制柱状图的函数:matplotlib
def plot_bar(x_data, y_data, title, fig_name):
    """
    绘制柱状图
    :param x_data: 标签数据,列表
    :param y_data: 标签数据对应的数量，列表
    :param title:  图片标题，字符串
    :param fig_name:  图片名，字符串
    :return:
    """
    # 绘图
    plt.style.use('ggplot')
    fig, ax = plt.subplots(figsize=(9, 6))
    # 处理较长的标签
    x_data = handle_str(x_data)
    # 绘制竖直柱状图
    ax.bar(x_data, y_data, width=.3)

    # 去除四周的边框 (spine.set_visible(False))
    [spine.set_visible(False) for spine in ax.spines.values()]
    # 去除 x 和 y 轴之间无用的刻度 tick
    ax.tick_params(top=False, left=False, right=False)
    plt.yticks([])  # 去除y坐标轴标签
    # # 实际的值展示
    vmax = max(y_data)
    for i, value in zip(x_data, y_data):
         ax.text(i, value + vmax * 0.02, '%d' % value, va='center', fontsize=12)
    plt.title(title)
    plt.savefig(r'%s\%s.png' % (drc.SAVE_PATH, fig_name))
    plt.close()


# 绘制直方图的函数:seaborn
def plot_hist(x_data, title, fig_name):
    """
    绘制直方图
    :param x_data: 数据列表
    :param title:  图片标题，字符串
    :param fig_name:  图片名，字符串
    :return: 直方图
    """
    plt.style.use('ggplot')
    plt.figure(figsize=(9, 6), dpi=100)  # 通过dpi参数指定图像的分辨率
    sns.distplot(x_data, hist=True, kde=True)
    plt.title(u'%s' % title)
    plt.savefig(r'%s\%s.png' % (drc.SAVE_PATH, fig_name))
    plt.close()


# 绘制分类柱状图需要的数据
def generate_bar_type(x_data, y_data):
    """
    绘制分类柱状图需要的数据
    :param x_data: 类别数据，列表
    :param y_data: 标签数据，列表
    :return: 类别集合。标签集合(按照数量的多少排序)。{类别：{标签：数量}}的字典
    """
    # 首先确定标签集合的顺序
    la_dict = Counter(y_data)
    sort_dict = sorted(la_dict.items(), key=lambda x: x[1], reverse=True)
    new_y = [j[0] for j in sort_dict]
    # 获取类别的集合
    type_list = sorted(list(set(x_data)), reverse=True)
    # 获取字典
    data_dict = {h: Counter([j for i, j in zip(x_data, y_data) if i == h]) for h in type_list}
    return type_list, new_y, data_dict


# 绘制带有数据的分类柱状图的函数
def plot_hist_with_type(x_data, y_data, data_dict, title, fig_name):
    """
    绘制柱状图
    :param x_data: 类别集合，字符串列表
    :param y_data: 标签集合，列表
    :param data_dict: 格式为{类别：{标签：数量}}的字典
    :param title:  图片标题，字符串
    :param fig_name:  图片名，字符串
    :return:
    """
    fig = plt.figure()
    gs = gridspec.GridSpec(3, 1)
    ax0 = fig.add_subplot(gs[:2, :])
    ax1 = fig.add_subplot(gs[2, 0])
    fig.subplots_adjust(hspace=0.8)
    sign = 1
    # 需要将y_data中的元素变为字符串
    str_y_data = handle_str(y_data)
    cc = []  # 定义柱状的起始数据
    table_data = []
    for index, t in enumerate(x_data):
        plot_data = [data_dict[t][h] if h in data_dict[t] else 0 for h in y_data]
        table_data.append([str(j) for j in plot_data])
        if sign:
            ax0.bar(str_y_data, plot_data, label='类：%s' % t, width=0.3)
            cc = np.array(plot_data)
            sign = 0
        else:
            ax0.bar(str_y_data, plot_data, label='类：%s' % t, bottom=cc, width=0.3)
            cc += np.array(plot_data)
    ax0.legend()
    ax0.set_title(u'%s' % title)
    x_data.reverse()
    table_data.reverse()
    # 添加数据表格
    # 计算类别比例
    title_type = [[h, sum(data_dict[h].values())] for h in x_data]
    # 类别
    str_type = '类%s' % title_type[0][0]
    # 比值
    str_pre = '1'
    num = title_type[0][1]
    for jj in title_type[1:]:
        str_type += ':类%s' % jj[0]
        str_pre += ':%.3f' % (jj[1] / num)
    [spine.set_visible(False) for spine in ax1.spines.values()]
    ax1.set_xticks([])
    ax1.set_yticks([])
    ax1 = plt.gca()
    ax1.patch.set_facecolor("white")
    # 数据最后一行加上类别的比值
    x_data += ['比例']
    str_p = []
    for i in range(len(table_data[0])):
        num = float(table_data[0][i])
        str_per = '1:'
        for j in range(1, len(table_data)):
            if num != 0:
                str_per += '%.3f' % (float(table_data[j][i]) / num)
            else:
                str_per += '0'
        str_p.append(str_per)
    table_data.append(str_p)
    ax1.set_xlabel(u'样本：' + str_type + '，比例' + str_pre)
    ax1.table(cellText=table_data, rowLabels=x_data, loc='center', cellLoc='center')
    plt.savefig(r'%s\%s.png' % (drc.SAVE_PATH, fig_name))
    plt.close()


# 生成分类概率密度的函数
def generate_data_for_plot_distribution(x_data, y_data):
    """
    输出每个类别对应的数据的列表的字典
    :param x_data: 类别数据列表
    :param y_data: 数值型数据列表
    :return: {类别：[数据列表]}的字典
    """
    digit_data_dict = {}
    for key, value in zip(x_data, y_data):
        if key in digit_data_dict:
            digit_data_dict[key].append(value)
        else:
            digit_data_dict[key] = [value]
    return digit_data_dict


# 绘制分类标识的概率密度图
def plot_density_with_type(data_dict, title, fig_name, xlabel):
    """
    绘制分类标识的概率密度图
    :param data_dict: 每一类对应的数据列表的字典
    :param title: 图片的标题
    :param fig_name: 保存图片的名称
    :param xlabel: X轴标题
    :return: 
    """
    plt.figure()
    for j, t in enumerate(sorted(list(data_dict.keys()))):
        sns.distplot(list(data_dict[t]), hist=True, label='类: %s' % str(t))
    plt.title(u'%s' % title)
    plt.legend()
    plt.xlabel(u'%s' % xlabel)
    plt.savefig(r'%s\%s.png' % (drc.SAVE_PATH, fig_name))
    plt.close()


# 计算序列间的皮尔逊系数
def get_pearson(data1, data2):
    """
    计算数据间的皮尔逊系数
    :param data1: 数据1,列表
    :param data2: 数据2，列表
    """
    x1, x2 = np.array(data1), np.array(data2)
    # 求和
    xy = np.sum(x1 * x2)
    # 求平方和
    sx1 = np.sum(x1 ** 2)
    sx2 = np.sum(x2 ** 2)
    return xy/((sx1 ** 0.5) * (sx2 ** 0.5))


# 绘制散点图
def plot_scatter(data1, data2, title, fig_name, labelx, labely):
    """
    绘制数据间的散点图
    :param data1: 数据1,列表
    :param data2: 数据2，列表
    :param title: 图片的标题
    :param fig_name: 保存的图片名称
    :param labelx: X轴标题
    :param labely: Y轴标题
    :return: 散点图
    """
    plt.style.use('ggplot')
    plt.figure()
    plt.plot(data1, data2, 'o')
    plt.title(u'%s，皮尔逊系数：%.4f' % (title, get_pearson(data1, data2)))
    plt.xlabel(u'%s' % labelx)
    plt.ylabel(u'%s' % labely)
    plt.savefig(r'%s\%s.png' % (drc.SAVE_PATH, fig_name))
    plt.close()


def plot_two_type_type_pie(data1, data2, data3, title, fig_name):
    """
    data1,data2均是类别型特征的值的列表。 data3是类别型特征。绘制组合特征值组合的分类饼图
    :param data1: 数据列表1
    :param data2: 数据列表2
    :param data3: 数据列表3
    :param title: 图片的标题
    :param fig_name: 保存的图片名称
    :return: 饼图
    """
    # 2个类别特征的值
    type_data1 = sorted(list(set(data1)))
    type_data2 = sorted(list(set(data2)))
    # 目标特征的值
    t_type = sorted(list(set(data3)))
    # 特征值数少的作为行
    if len(type_data1) > len(type_data2):
        type_data1, type_data2 = type_data2, type_data1
        data1, data2 = data2, data1
    # 设置图
    fig, axes = plt.subplots(nrows=len(type_data1), ncols=len(type_data2))
    #  根据饼图中人数的多少。定义饼图的大小。
    min_num, max_num = 0.9, 1.9
    size_dict = {}
    count_dict = {}
    for a in type_data1:
        for b in type_data2:
            pie_data = []
            for c, d, e in zip(data1, data2, data3):
                if a == c and b == d:
                    pie_data.append(e)
            size_dict['%s_%s' % (str(a), str(b))] = len(pie_data) / len(data3)
            count_dict['%s_%s' % (str(a), str(b))] = pie_data
    trans_size_dict = {h: (size_dict[h] - min(size_dict.values()) / (max(size_dict.values()) - min(size_dict.values()))
                                                                         * (max_num - min_num) + min_num) for h in size_dict}
    # 定义图的位置
    sign = 0
    for a in type_data1:
        for b in type_data2:
            # 计算
            new_dict = {}
            for k in count_dict['%s_%s' % (str(a), str(b))]:
                if k in new_dict:
                    new_dict[k] += 1
                else:
                    new_dict[k] = 1
            # 数值列表
            data_pie = [new_dict[o] if o in new_dict else 0 for o in t_type]
            label = ['类%s:\n' % tt + str(dd) if dd != 0 else '' for dd, tt in zip(data_pie, t_type)]
            axes[sign // len(type_data2), sign % len(type_data2)].pie(data_pie,
                                                                      labels=label,
                                                                      radius=trans_size_dict['%s_%s' % (str(a), str(b))],
                                                                      labeldistance=.2)

            if sign // len(type_data2) == len(type_data1) - 1:
                axes[sign // len(type_data2), sign % len(type_data2)].set_xlabel(b)

            if sign % len(type_data2) == 0:
                axes[sign // len(type_data2), sign % len(type_data2)].set_ylabel(a)

            sign += 1

    fig.suptitle(u'%s' % title)
    plt.savefig(r'%s\%s.png' % (drc.SAVE_PATH, fig_name))
    plt.close()


def plot_one_type_type_box(data1, data2, data3, title, fig_name, labelx, labely, name):
    """
    data1是连续特征的值的列表,data2是类别型特征的值的列表。 data3是类别型特征。绘制组合特征值组合的分类箱图
    :param data1: 数据列表1
    :param data2: 数据列表2
    :param data3: 数据列表3
    :param title: 图片的标题
    :param fig_name: 保存的图片名称
    :param labelx: X轴标题
    :param labely: Y轴标题
    :param name: 图例的名称
    :return: 饼图
    """
    df = pd.DataFrame()
    df['number'] = data1
    df['type'] = data2
    df['target'] = data3
    plt.figure(figsize=(13, 10), dpi=80)
    sns.boxplot(x='type', y='number', data=df, hue='target')

    for i in range(len(df['type'].unique())-1):
        plt.vlines(i+.5, 10, 45, linestyles='solid', colors='gray', alpha=0.2)

    plt.title(u'%s' % title, fontsize=22)
    plt.xlabel(u'%s' % labely)
    plt.ylabel(u'%s' % labelx)
    plt.legend(title=name)
    plt.savefig(r'%s\%s.png' % (drc.SAVE_PATH, fig_name))
    plt.close()


def plot_scatter_type(data1, data2, data3, title, fig_name, label1, label2):
    """
    绘制data1和data2的散点图，其中data3中的值为图例。如果类别大于10个类别，需要在程序中添加颜色。否则会导致不同类颜色相同
    :param data1: 数据列表1
    :param data2: 数据列表2
    :param data3: 代表图例的数据列表
    :param title: 图片的标题
    :param fig_name: 保存的图片名称
    :param label1: X轴标题
    :param label2: Y轴标题
    :return: 散点图
    """
    fig, ax = plt.subplots()
    legend_list = list(set(data3))
    # 10种颜色的列表
    c_list = ['k', 'g', 'c', 'b', 'y', 'r', 'm', 'tab:brown', 'tab:blue', 'tab:gray', 'tab:pink']

    for j in range(len(legend_list)):
        data_1 = [a for a, b in zip(data1, data3) if b == legend_list[j]]
        data_2 = [c for c, d in zip(data2, data3) if d == legend_list[j]]
        ax.scatter(data_1, data_2, c=c_list[j % 10], label=legend_list[j % 10], alpha=0.9, edgecolors='none', s=50)
    ax.legend()
    plt.title(u'%s' % title)
    plt.xlabel(u'%s' % label1)
    plt.ylabel(u'%s' % label2)
    plt.savefig(r'%s\%s.png' % (drc.SAVE_PATH, fig_name))
    plt.close()


def plot_scatter_3d(data1, data2, data3, title, fig_name, label1, label2, label3):
    """
    绘制3d的散点图
    :param data1: 数据列表1
    :param data2: 数据列表2
    :param data3: 数据列表3
    :param title: 图片的标题
    :param fig_name: 保存的图片名称
    :param label1: X轴标题
    :param label2: Y轴标题
    :param label3: Z轴标题
    :return: 散点图
    """
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(data1, data2, data3)
    ax.set_xlabel(u'%s' % label1)
    ax.set_ylabel(u'%s' % label2)
    ax.set_zlabel(u'%s' % label3)
    plt.title(u'%s' % title)
    plt.savefig(r'%s\%s.png' % (drc.SAVE_PATH, fig_name))
    plt.close()


def plot_two_type_num_box(data1, data2, data3, title, fig_name):
    """
    data1,data2均是类别型特征的值的列表。 data3是连续型特征，特征值的组合采用箱图
    :param data1: 数据列表1
    :param data2: 数据列表2
    :param data3: 数据列表3
    :param title: 图片的标题
    :param fig_name: 保存的图片名称
    :return: 饼图
    """
    plt.style.use('ggplot')
    # 2个类别特征的值
    type_data1 = sorted(list(set(data1)))
    type_data2 = sorted(list(set(data2)))

    # 特征值数少的作为行
    if len(type_data1) > len(type_data2):
        type_data1, type_data2 = type_data2, type_data1
        data1, data2 = data2, data1
    # 设置图
    fig, axes = plt.subplots(nrows=len(type_data1), ncols=len(type_data2))
    if len(data1) == 0 or len(data2) == 0 or len(data3) == 0:
        return print('绘图数据出现空列表')
    min_num, max_num = min(data3), max(data3)
    sign = 0
    for a in type_data1:
        for b in type_data2:
            pie_data = []
            for c, d, e in zip(data1, data2, data3):
                if a == c and b == d:
                    pie_data.append(e)
            if len(type_data1) == 1:
                if len(type_data2) != 1:
                    axes[sign % len(type_data2)].boxplot(pie_data, showmeans=True, labels=[''])
                    # 设置同样的y轴区间
                    axes[sign % len(type_data2)].set_ylim(min_num, max_num)

                    # 最后一行
                    axes[sign % len(type_data2)].set_xlabel(b)
                    # 第一列
                    if sign % len(type_data2) == 0:
                        axes[sign % len(type_data2)].set_ylabel(a)
                    else:
                        axes[sign % len(type_data2)].set_yticks(())
                else:
                    axes.boxplot(pie_data, showmeans=True, labels=[''])
                    # 设置同样的y轴区间
                    axes.set_ylim(min_num, max_num)
                    # 最后一行
                    axes.set_xlabel(b)
                    axes.set_ylabel(a)
            else:
                axes[sign // len(type_data2), sign % len(type_data2)].boxplot(pie_data, showmeans=True, labels=[''])
                # 设置同样的y轴区间
                axes[sign // len(type_data2), sign % len(type_data2)].set_ylim(min_num, max_num)

                # 最后一行
                if sign // len(type_data2) == len(type_data1) - 1:
                    axes[sign // len(type_data2), sign % len(type_data2)].set_xlabel(b)
                # 第一列
                if sign % len(type_data2) == 0:
                    axes[sign // len(type_data2), sign % len(type_data2)].set_ylabel(a)
                    # 只要是第一列的，不是最后一行，只保留y轴
                    if sign // len(type_data2) != len(type_data1) - 1:
                        axes[sign // len(type_data2), sign % len(type_data2)].set_xticks(())
                else:
                    # 只要不是第一列的，最后一行，只保留x轴
                    if sign // len(type_data2) == len(type_data1) - 1:
                        axes[sign // len(type_data2), sign % len(type_data2)].set_yticks(())
                    else:
                        axes[sign // len(type_data2), sign % len(type_data2)].set_yticks(())
                        axes[sign // len(type_data2), sign % len(type_data2)].set_xticks(())
            sign += 1

    fig.suptitle(u'%s' % title)
    plt.savefig(r'%s\%s.png' % (drc.SAVE_PATH, fig_name))
    plt.close()




