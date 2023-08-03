import pandas as pd


class Data_Cleanout:
    def __init__(self, taobao_data):
        print('总行数:', taobao_data.shape[0])
        print('数据类型\n', taobao_data.dtypes)
        # 将列名修改为中文
        col_name_dict = {'user_id': '用户ID', 'item_id': '商品ID', 'behavior_type': '用户行为',
                         'user_geohash': '用户地址', 'item_category': '商品类别', 'time': '登陆时间'}
        taobao_data.rename(columns=col_name_dict, inplace=True)
        self.taobao_data = taobao_data
        # 查看数据集
        print(self.taobao_data.head())

    def cleanout(self):
        # 查看缺失值
        print('查看缺失值\n', self.taobao_data.isnull().sum())
        # 查看数据类型
        print('查看数据类型\n', self.taobao_data.info())
        # 修改为object类型
        self.taobao_data['用户ID'] = self.taobao_data['用户ID'].astype(object)
        self.taobao_data['商品ID'] = self.taobao_data['商品ID'].astype(object)
        self.taobao_data['用户行为'] = self.taobao_data['用户行为'].astype(object)
        self.taobao_data['商品类别'] = self.taobao_data['商品类别'].astype(object)
        # 去重
        self.taobao_data.drop_duplicates(subset=['用户ID', '商品ID', '用户行为', '商品类别', '登陆时间'], keep='first')
        print('去重后行数\n', self.taobao_data.shape[0])
        # 时间分列，时间格式为2014-12-06 02处理为[登陆时间]：2014-12-06，[登陆时刻]：02的格式
        # 获取日期值
        time_colser = self.taobao_data.loc[:, '登陆时间']
        time_list = []
        for v in time_colser:
            date_ser = v.split()[0]
            time_list.append(date_ser)
        time_ser = pd.Series(time_list)
        date = time_ser

        # 获取时刻值
        time_list1 = []
        for v in time_colser:
            date_ser1 = v.split(' ')[1]
            time_list1.append(date_ser1)
        time_ser1 = pd.Series(time_list1)
        date_clock = time_ser1
        # 将日期和时刻赋值给数据表
        self.taobao_data.loc[:, '登陆时间'] = date
        self.taobao_data.loc[:, '登陆时刻'] = date_clock

        print(self.taobao_data.head())
        # 保存清洗后的数据
        self.taobao_data.to_csv('../data/user_action_new.csv', index=False)


if __name__ == '__main__':
    data_clean = Data_Cleanout(pd.read_csv('../data/user_action.csv'))
    data_clean.cleanout()
