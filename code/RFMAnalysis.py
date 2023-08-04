import datetime
import math
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import seaborn as sns
import matplotlib as mpt
import matplotlib.pyplot as plt

mpt.use('TkAgg')
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号


# 使用K均值算法聚类分析用户价值
class RFMAnalysis:
    def __init__(self, data):
        self.taobao_data = data

    def count_days(self, max_date_group_list, max_date):
        time_list = []
        max_date_time = max_date  # 这里假设 max_date_group_list 已经是 datetime 类型
        for group_time in max_date_group_list:
            time_r_day = (max_date_time - group_time).days
            time_list.append(time_r_day)
        return time_list

    def build_R(self, max_r, min_r, trisection_distance_r, date_list):
        # 计算R-score
        score_r_list = []
        for i in date_list:
            if math.ceil((date_list[i] - min_r) / trisection_distance_r) == 0:
                score_r_list.append(1)
            else:
                score_r_list.append(math.ceil((date_list[i] - min_r) / trisection_distance_r))
        return score_r_list

    def build_F(self, max_f, min_f, trisection_distance_f, buy_num_count_list):
        score_f_list = []
        for i in date_list:
            if math.ceil((buy_num_count_list[i] - min_f) / trisection_distance_f) == 0:
                score_f_list.append(1)
            else:
                score_f_list.append(math.ceil((buy_num_count_list[i] - min_f) / trisection_distance_f))
        return score_f_list


if __name__ == '__main__':
    taobao_data = pd.read_csv('../data/user_action_new.csv')
    taobao_data['登陆时间'] = pd.to_datetime(taobao_data['登陆时间'])
    # 出于电脑性能原因，只选取前10W条数据进行分析
    data = taobao_data.iloc[:100000, :]

    data_analysis = RFMAnalysis(data)

    max_date = data['登陆时间'].max()
    behavior_type_user_num = data.groupby('用户行为')['用户ID']
    behavior_type_user_list = list(behavior_type_user_num)
    behavior_type_user_num_tuple = behavior_type_user_list[3][1]
    behavior_type_user_str = behavior_type_user_list[3][0]
    user_behaviour_list = []
    for i in behavior_type_user_num_tuple:
        user_behaviour_1 = dict(list(data.groupby(['用户ID', '用户行为'])))[(i, behavior_type_user_str)]
        user_behaviour_frame_1 = pd.DataFrame(user_behaviour_1)
        user_behaviour_list.append(user_behaviour_frame_1)
    user_behaviour_frame_con = pd.concat(user_behaviour_list)

    # 各个用户最近购买日期
    max_date_group = user_behaviour_frame_con.groupby('用户ID')['登陆时间'].max()
    # 求取各个用户最近购买日期距离数据采集时的天数——即R值
    max_date_group_list = list(max_date_group)
    date_list = data_analysis.count_days(max_date_group_list, max_date)
    # 购买次数计数——即F值
    buy_num_count = user_behaviour_frame_con.groupby('用户ID')['用户行为'].count()
    # 转换为列表
    buy_num_count_list = list(buy_num_count)
    print('data_list', date_list)
    # 求取R、F的最大、最小、三等分距
    # 求R的最大值
    max_r = max(date_list)
    # 求R的最小值
    min_r = min(date_list)
    # 求 R的极值三等分距
    trisection_distance_r = (max_r - min_r) / 3
    print('trisection_distance_r', trisection_distance_r)
    # 求F的最大值
    max_f = max(buy_num_count_list)
    # 求F的最小值
    min_f = min(buy_num_count_list)
    # 求F的三等分距
    trisection_distance_f = (max_f - min_f) / 3
    print('trisection_distance_f', trisection_distance_f)

    rfm = pd.DataFrame()
    rfm['R-score'] = data_analysis.build_R(max_r, min_r, trisection_distance_r, date_list)
    rfm['F-score'] = data_analysis.build_F(max_f, min_f, trisection_distance_f, buy_num_count_list)
    print(rfm)
    # 数据标准化
    scaler = StandardScaler()
    rfm_scaled = scaler.fit_transform(rfm[['R-score', 'F-score']])
    print(rfm_scaled)
    # 定义候选K值
    scope = range(1, 11, 1)
    #     定义SSE列表，用来存放不同K值下的SSE
    sse = []
    for k in scope:
        kmeans = KMeans(n_clusters=k)
        kmeans.fit(rfm_scaled)
        sse.append(kmeans.inertia_)
    plt.xticks(scope)

    sns.lineplot(x=scope, y=sse, marker='o')
    # plt.show()
    # 根据kmeans肘部法则，确定K值为3
    kmeans = KMeans(n_clusters=3)
    kmeans.fit(rfm_scaled)
    #     获取聚类质心
    print('质心:', kmeans.cluster_centers_)
    # 获取样本簇标签
    print('标签:', kmeans.labels_)
    # 获取SSE
    print('SSE:', kmeans.inertia_)
    # 获取迭代次数
    print('迭代次数:', kmeans.n_iter_)
    # 将聚类标签添加到原始数据
    rfm['Cluster'] = kmeans.labels_

    # 绘制箱线图，
    fig, ax = plt.subplots(3, 3)
    fig.set_size_inches(18, 5)
    for i in range(3):
        d = rfm[rfm['Cluster'] == i]
        sns.boxplot(y="R-score", data=d, ax=ax[i][0])
        sns.boxplot(y="F-score", data=d, ax=ax[i][1])
        # sns.boxplot(y="M-score", data=d, ax=ax[i][2])
    plt.tight_layout()
    plt.savefig('../tmp/不同群体箱形图对比.svg')
    plt.show()
