import numpy as np
import pandas as pd
import datetime as dt
import matplotlib as mpt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from matplotlib import pyplot as plt
from datetime import datetime

mpt.use('TkAgg')
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号


class Data_Analysis:
    def __init__(self, taobao_data):
        self.taobao_data = taobao_data
        self.pv = 0  # 点击量
        self.fav = 0  # 收藏量
        self.cart = 0  # 加购物车数量
        self.buy = 0  # 购买量

    def flow_analysis(self):  # 流量指标分析，PV（APP总访问量）、UV（APP独立访问数）。
        # 查看PV
        # 行为类型数量，规定1代表pv，2代表fav，3代表cart，4代表buy。
        behavior_type_num = self.taobao_data.groupby('用户行为')['用户ID'].count()
        print("行为类型数量\n", behavior_type_num)  # 总访问PV为11550581
        self.pv = behavior_type_num[1]
        self.fav = behavior_type_num[2]
        self.cart = behavior_type_num[3]
        self.buy = behavior_type_num[4]
        # 查看UV
        for col in self.taobao_data.columns:
            print('{}的唯一值：'.format(col), len(self.taobao_data[col].unique()))  # UV是用户ID的唯一值： 10000
        self.pv = behavior_type_num[1]

    def aarrr_analysis(self):  # AARRR模型，分析各个流程的转化漏斗。
        # 由于收藏和加购没有先后顺序，所以二者合并后计算转化率——收藏加购转化率
        # 收藏加购转化率
        fav_cart_sum = self.fav + self.cart
        fav_cart_ratio = fav_cart_sum / self.pv * 100
        # 购买转化率
        buy_ratio = self.buy / fav_cart_sum * 100
        print('收藏加购转化率\n', fav_cart_ratio)
        print('购买转化率\n', buy_ratio)
        # 绘制漏斗图
        labels = ['PV', 'FAV+CART', 'BUY']
        values = [self.pv, fav_cart_sum, self.buy]
        click_num = self.pv
        data1 = [click_num / 2 - i / 2 for i in values]
        data2 = [i + j for i, j in zip(values, data1)]
        color_list = ['#5c1d1d', '#892c2c', '#994a4a', '#c56161']  # 柱子颜色
        fig, ax = plt.subplots(figsize=(16, 9), facecolor='#f4f4f4')
        ax.barh(labels[::-1], data2[::-1], color=color_list, height=0.7)  # 柱宽设置为0.7
        ax.barh(labels[::-1], data1[::-1], color='#f4f4f4', height=0.7)  # 设置成背景同色
        ax.axis('off')

        polygons = []
        for i in range(len(values)):
            # 阶段
            ax.text(
                0,  # 坐标
                i,  # 高度
                labels[::-1][i],  # 文本
                color='black', alpha=0.8, size=16, ha="right")

            # 数量
            ax.text(
                data2[0] / 2,
                i,
                str(values[::-1][i]) + '(' + str(round(values[::-1][i] / values[0] * 100, 1)) + '%)',
                color='black', alpha=0.8, size=18, ha="center")

            if i < 2:
                # 比例
                ax.text(
                    data2[0] / 2,
                    1.5 - i,
                    str(round(values[i + 1] / values[i], 2) * 100) + '%',
                    color='black', alpha=0.8, size=16, ha="center")

                # 绘制多边形
                polygons.append(Polygon(xy=np.array([(data1[i + 1], 1 + 0.35 - i),
                                                     # 因为柱状图的宽度设置成了0.7，所以一半便是0.35
                                                     (data2[i + 1], 1 + 0.35 - i),
                                                     (data2[i], 2 - 0.35 - i),
                                                     (data1[i], 2 - 0.35 - i)])))
        # 使用add_collection与PatchCollection来向Axes上添加多边形
        ax.add_collection(PatchCollection(polygons,
                                          facecolor='#e2b0b0',
                                          alpha=0.8))
        plt.title("流量转化漏斗", fontsize=18)
        plt.savefig('../tmp/流量转化漏斗.svg')
        plt.show()

    def time_analysis(self):  # 不同时间用户行为模式分析
        # 1.不同日期访问量
        unique_user_day = self.taobao_data.groupby('登陆时间')['用户ID'].value_counts()
        unique_user_day1 = unique_user_day.groupby('登陆时间').count().reset_index()
        column_names = unique_user_day1.columns.tolist()
        print(column_names)
        dates = unique_user_day1.iloc[:, 0].tolist()
        visitors = unique_user_day1.iloc[:, 1].tolist()
        plt.figure(figsize=(20, 10), dpi=100)  # 设置图片 大小
        x_values = range(len(dates))
        plt.xticks(x_values, rotation=90)
        plt.yticks(range(0, max(visitors), 500))
        # plt.grid(True, linestyle="--", alpha=0.5)  # 添加网格显示
        #  添加描述信息
        plt.xlabel("日期")
        plt.ylabel("访问量")
        plt.title("不同日期访问量", fontsize=20)
        plt.plot(dates, visitors, color='orange')
        plt.bar(dates, visitors)
        plt.savefig('../tmp/不同日期访问量.svg')
        plt.show()

        # 2.分析一周内每日的用户行为
        # 取平常一周和双十二一周数据对比
        normal_index = unique_user_day1.loc[unique_user_day1['登陆时间'] == '2014-11-18'].index[0]

        weeks_normal = unique_user_day1.iloc[normal_index:normal_index + 15, 0].tolist()
        visitors_normal = unique_user_day1.iloc[normal_index:normal_index + 15, 1].tolist()

        weeks_twelve_index = unique_user_day1.loc[unique_user_day1['登陆时间'] == '2014-12-12'].index[0]
        weeks_twelve = unique_user_day1.iloc[weeks_twelve_index - 4:weeks_twelve_index + 3, 0].tolist()
        visitors_twelve = unique_user_day1.iloc[weeks_twelve_index - 4:weeks_twelve_index + 3, 1].tolist()

        print(visitors_normal)
        print(visitors_twelve)
        weeks_normal_dates = [datetime.strptime(date, '%Y-%m-%d').strftime('%m-%d (%a)') for date in weeks_normal]
        weeks_twelve_dates = [datetime.strptime(date, '%Y-%m-%d').strftime('%m-%d (%a)') for date in weeks_twelve]

        plt.figure(figsize=(12, 5))
        plt.subplot(221)
        x_values1 = range(len(weeks_normal))
        plt.xticks(x_values1, weeks_normal_dates, rotation=45)
        plt.yticks(range(0, max(visitors_normal), 500))
        plt.title("平常一周的访问量", fontsize=20)
        plt.plot(weeks_normal, visitors_normal, color='orange')
        plt.bar(weeks_normal, visitors_normal)

        plt.subplot(222)
        x_values1 = range(len(weeks_twelve))
        plt.xticks(x_values1, weeks_twelve_dates, rotation=45)
        plt.yticks(range(0, max(visitors_twelve), 500))
        plt.title("双十二一周的访问量", fontsize=20)
        plt.plot(weeks_twelve, visitors_twelve, color='orange')
        plt.bar(weeks_twelve, visitors_twelve)
        plt.savefig('../tmp/平常一周和双十二一周数据对比.svg')
        plt.show()

        # 3.不同时刻访问量
        unique_user_hour = self.taobao_data.groupby('登陆时刻')['用户ID'].value_counts()
        unique_user_hour_count = unique_user_hour.groupby('登陆时刻').count().reset_index()
        hours = unique_user_hour_count.iloc[:, 0].tolist()
        visitors_hours = unique_user_hour_count.iloc[:, 1].tolist()
        plt.figure(figsize=(12, 5), dpi=100)  # 设置图片 大小
        x_values = range(len(hours))
        plt.xticks(x_values)
        plt.yticks(range(0, max(visitors_hours), 500))
        # plt.grid(True, linestyle="--", alpha=0.5)  # 添加网格显示
        #  添加描述信息
        plt.xlabel("时刻")
        plt.ylabel("访问量")
        plt.title("不同时刻访问量", fontsize=20)
        plt.plot(hours, visitors_hours, color='orange')
        plt.bar(hours, visitors_hours)
        plt.savefig('../tmp/不同时刻访问量.svg')
        plt.show()
        # 4. 双十二当天不同时刻用户行为分析
        # 双十二当天用户访问量
        taobao_twelve = self.taobao_data.loc[self.taobao_data['登陆时间'] == '2014-12-12']
        column_names = taobao_twelve.columns.tolist()
        # print(column_names)

        twelve_user_hour = taobao_twelve.groupby('登陆时刻')['用户ID'].value_counts()
        twelve_user_hour1 = twelve_user_hour.groupby('登陆时刻').count().reset_index()

        hours_twelve = twelve_user_hour1.iloc[:, 0].tolist()
        visitors_twelve = twelve_user_hour1.iloc[:, 1].tolist()
        # 双十二当天用户购买量
        taobao_sales = taobao_twelve.loc[taobao_twelve['用户行为'] == 4]  # 购买行为是4
        sales_twelve = taobao_sales.groupby('登陆时刻')['用户ID'].value_counts()
        sales_twelve1 = sales_twelve.groupby('登陆时刻').count().reset_index()
        print(sales_twelve.groupby('登陆时刻').count().reset_index(name='计数'), '\n', sales_twelve1.iloc[:, 1].sum(), '\n',
              sales_twelve1.iloc[:, 1])
        sales = sales_twelve1.iloc[:, 1].tolist()

        # 双十二当天用户加入购物车量
        taobao_sales = taobao_twelve.loc[taobao_twelve['用户行为'] == 3]  # 加入购物车行为是3
        carts_twelve = taobao_sales.groupby('登陆时刻')['用户ID'].value_counts()
        carts_twelve1 = carts_twelve.groupby('登陆时刻').count().reset_index()
        carts = carts_twelve1.iloc[:, 1].tolist()

        # 双十二当天用户收藏量
        taobao_sales = taobao_twelve.loc[taobao_twelve['用户行为'] == 2]  # 收藏行为是2
        favs_twelve = taobao_sales.groupby('登陆时刻')['用户ID'].value_counts()
        favs_twelve1 = favs_twelve.groupby('登陆时刻').count().reset_index()
        favs = favs_twelve1.iloc[:, 1].tolist()

        def drawing_picture(self, x, y1, y2, y3, y, x_label, y_label, y_step, title, save_path):
            plt.figure(figsize=(12, 5), dpi=100)  # 设置图片 大小
            x_values = range(len(x))
            plt.xticks(x_values)
            plt.yticks(range(0, max(y + y1 + y2 + y3), y_step))
            # plt.grid(True, linestyle="--", alpha=0.5)  # 添加网格显示
            #  添加描述信息
            plt.xlabel(x_label)
            plt.ylabel(y_label)
            plt.title(title, fontsize=20)
            # plt.plot(x, y, lable='访问量', color='orange')
            plt.bar(x, y, label='访问量')
            plt.plot(x, y1, label='购买量', color='red')
            plt.plot(x, y2, label='加入购物车量', color='blue')
            plt.plot(x, y3, label='收藏量', color='green')
            plt.legend()  # 添加图例

            plt.savefig(save_path)
            plt.show()

        drawing_picture(hours_twelve, sales, carts, favs, visitors_twelve, '时刻', '访问量', 500, '双12当天用户行为',
                        '../tmp/双12当天用户行为.svg')

    def rfm_analysis(self):
        print('开始分析', '*' * 20)
        # 选取10万数据
        taobao_data_sub1 = self.taobao_data.iloc[:100000, :]
        # 不日期访问量
        max_date = taobao_data_sub1['登陆时间'].max()
        behavior_type_user_num = taobao_data_sub1.groupby('用户行为')['用户ID']
        # 将 groupby 对象转换为 list
        behavior_type_user_list = list(behavior_type_user_num)
        # 提取 'buy' 行为类型对应的用户ID
        behavior_type_user_num_tuple = behavior_type_user_list[3][1]
        # 提取 'buy' 这个字符串
        behavior_type_user_str = behavior_type_user_list[3][0]
        # 提取出行为类型为 'buy' 的数据框
        user_behaviour_list = []
        for i in behavior_type_user_num_tuple:
            user_behaviour_1 = dict(list(taobao_data_sub1.groupby(['用户ID', '用户行为'])))[(i, behavior_type_user_str)]
            user_behaviour_frame_1 = pd.DataFrame(user_behaviour_1)
            user_behaviour_list.append(user_behaviour_frame_1)
        user_behaviour_frame_con = pd.concat(user_behaviour_list)

        # 求取各个顾客最近购买行为的距离天数的函数
        def count_days(max_date_group_list):
            time_list = []
            max_date_time = dt.datetime.strptime(max_date, "%Y-%m-%d")
            for group in max_date_group_list:
                group_time = dt.datetime.strptime(group, "%Y-%m-%d")
                time_r_day = (max_date_time - group_time).days
                time_list.append(time_r_day)
            return time_list

        # 各个用户最近购买日期
        max_date_group = user_behaviour_frame_con.groupby('用户ID')['登陆时间'].max()
        # 求取各个用户最近购买日期距离数据采集时的天数——即R值
        max_date_group_list = list(max_date_group)
        date_list = count_days(max_date_group_list)
        # 购买次数计数——即F值
        buy_num_count = user_behaviour_frame_con.groupby('用户ID')['用户行为'].count()
        # 转换为列表
        buy_num_count_list = list(buy_num_count)

        # 求取R、F的最大、最小、三等分距
        # 求R的最大值
        max_r = max(date_list)
        # 求R的最小值
        min_r = min(date_list)
        # 求 R的极值三等分距
        trisection_distance_r = (max_r - min_r) / 3
        # 求F的最大值
        max_f = max(buy_num_count_list)
        # 求F的最小值
        min_f = min(buy_num_count_list)
        # 求F的三等分距
        trisection_distance_f = (max_f - min_f) / 3

        # 计算R-score、F-score
        import math
        # 计算R-score
        score_r_list = []
        for i in date_list:
            if math.ceil((date_list[i] - min_r) / trisection_distance_r) == 0:
                score_r_list.append(1)
            else:
                score_r_list.append(math.ceil((date_list[i] - min_r) / trisection_distance_r))
        # 计算F-score
        score_f_list = []
        for i in date_list:
            if math.ceil((buy_num_count_list[i] - min_f) / trisection_distance_f) == 0:
                score_f_list.append(1)
            else:
                score_f_list.append(math.ceil((buy_num_count_list[i] - min_f) / trisection_distance_f))

        # 计算 RF-score=100*R-score+10*F-score+1*M-score
        # 由于本数据集不涉及到消费金额，所以暂时不考虑M-score
        rf_score_list = []
        for index in range(len(score_r_list)):
            rf_score_list.append(100 * score_r_list[index] + 10 * score_f_list[index])

        # 统计不同的RF-score出现的次数
        rf_score_list_110 = rf_score_list.count(110)
        rf_score_list_120 = rf_score_list.count(120)
        rf_score_list_210 = rf_score_list.count(210)
        rf_score_list_310 = rf_score_list.count(310)
        print('RF_scoreList110', rf_score_list_110, '\nRF_scoreList120', rf_score_list_120,
              '\nRF_scoreList210', rf_score_list_210, '\nRF_scoreList310', rf_score_list_310)


if __name__ == '__main__':
    data_analysis = Data_Analysis(pd.read_csv('../data/user_action_new.csv'))
    # data_analysis.flow_analysis()
    # data_analysis.aarrr_analysis()
    # data_analysis.time_analysis()
    data_analysis.rfm_analysis()
