import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import os

# 设置数据和结果路径
data_dir = "/mnt/ymj/vivo/群控/data"
result_dir = "/mnt/ymj/vivo/群控/result"
os.makedirs(data_dir, exist_ok=True)
os.makedirs(result_dir, exist_ok=True)

# 检查数据文件是否存在，如果不存在则生成
data_path = os.path.join(data_dir, 'device_data.csv')
if not os.path.exists(data_path):
    print("数据文件不存在，正在生成模拟数据...")
    import generate_data
    # 重新生成数据后，强制刷新分析结果
    if os.path.exists(os.path.join(result_dir, 'suspicious_devices.csv')):
        os.remove(os.path.join(result_dir, 'suspicious_devices.csv'))
    if os.path.exists(os.path.join(result_dir, 'group_leaders.csv')):
        os.remove(os.path.join(result_dir, 'group_leaders.csv'))
    if os.path.exists(os.path.join(result_dir, 'group_analysis.csv')):
        os.remove(os.path.join(result_dir, 'group_analysis.csv'))

# 读取数据
print("正在读取设备数据...")
df = pd.read_csv(data_path)
print(f"共读取{len(df)}条设备数据")

# 第一步：识别同一子网下IMEI数量大于20的设备
print("\n步骤1: 识别同一子网下IMEI数量大于20的设备")
subnet_counts = df.groupby('subnet')['imei'].count().reset_index()
subnet_counts.columns = ['subnet', 'imei_count']
suspicious_subnets = subnet_counts[subnet_counts['imei_count'] > 20]['subnet'].tolist()

print(f"发现{len(suspicious_subnets)}个可疑子网，每个子网包含超过20个设备")

# 筛选出这些子网下的设备
suspicious_devices = df[df['subnet'].isin(suspicious_subnets)]

# 同时筛选出公网IP一致的设备
ip_groups = df.groupby('ip')['imei'].count().reset_index()
ip_groups.columns = ['ip', 'imei_count']
suspicious_ips = ip_groups[ip_groups['imei_count'] > 1]['ip'].tolist()

ip_suspicious_devices = df[df['ip'].isin(suspicious_ips)]

# 合并两种可疑设备
suspicious_devices = pd.concat([suspicious_devices, ip_suspicious_devices]).drop_duplicates()
print(f"共识别出{len(suspicious_devices)}个可疑设备")

# 保存可疑设备数据
suspicious_devices_path = os.path.join(result_dir, 'suspicious_devices.csv')
suspicious_devices.to_csv(suspicious_devices_path, index=False)
print(f"可疑设备数据已保存至{suspicious_devices_path}")

# 第二步：对可疑设备进行K-means聚类分析
print("\n步骤2: 对可疑设备进行K-means聚类分析")

# 选择用于聚类的特征
features = ['screen_time', 'trade_freq', 'trade_amount', 'app_switches']
X = suspicious_devices[features].values

# 标准化特征
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 执行K-means聚类 (n=3)
n_clusters = 3
kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
cluster_labels = kmeans.fit_predict(X_scaled)

# 将聚类结果添加到数据框
suspicious_devices['cluster'] = cluster_labels

# 分析聚类结果
cluster_stats = suspicious_devices.groupby('cluster')[features].mean()
print("\n各聚类中心特征平均值:")
print(cluster_stats)

# 根据交易频率和交易金额特征识别各类群体
def identify_cluster_type(row):
    if row['trade_freq'] < cluster_stats['trade_freq'].mean() and row['trade_amount'] > cluster_stats['trade_amount'].mean():
        return "重大leader"
    elif abs(row['trade_freq'] - cluster_stats['trade_freq'].median()) < 2 and row['trade_amount'] < cluster_stats['trade_amount'].mean():
        return "肉机"
    else:
        return "误差项"

suspicious_devices['group_type'] = suspicious_devices.apply(identify_cluster_type, axis=1)

# 统计各类型设备数量
group_type_counts = suspicious_devices['group_type'].value_counts()
print("\n各类型设备数量:")
print(group_type_counts)

# 识别每个团伙的leader
print("\n步骤3: 识别每个团伙的leader")

# 计算每个设备的IP数量
device_ip_counts = suspicious_devices.groupby('imei')['ip'].nunique().reset_index()
device_ip_counts.columns = ['imei', 'ip_count']

# 合并IP数量信息
suspicious_devices = pd.merge(suspicious_devices, device_ip_counts, on='imei', how='left')

# 识别leader (交易金额大且IP变化多)
leaders = suspicious_devices[
    (suspicious_devices['group_type'] == "重大leader") & 
    (suspicious_devices['ip_count'] > 1)
]

print(f"共识别出{len(leaders)}个团伙leader")

# 保存leader信息
leaders_path = os.path.join(result_dir, 'group_leaders.csv')
leaders.to_csv(leaders_path, index=False)
print(f"团伙leader信息已保存至{leaders_path}")

# 可视化聚类结果
plt.figure(figsize=(12, 8))

# 交易频率 vs 交易金额
plt.subplot(2, 2, 1)
plt.scatter(suspicious_devices['trade_freq'], suspicious_devices['trade_amount'], c=suspicious_devices['cluster'], cmap='viridis', alpha=0.6)
plt.colorbar(label='聚类')
plt.xlabel('交易频率')
plt.ylabel('交易金额')
plt.title('交易频率 vs 交易金额')

# 屏幕使用时间 vs 应用跳转次数
plt.subplot(2, 2, 2)
plt.scatter(suspicious_devices['screen_time'], suspicious_devices['app_switches'], c=suspicious_devices['cluster'], cmap='viridis', alpha=0.6)
plt.colorbar(label='聚类')
plt.xlabel('屏幕使用时间')
plt.ylabel('应用跳转次数')
plt.title('屏幕使用时间 vs 应用跳转次数')

# 各聚类的设备数量
plt.subplot(2, 2, 3)
cluster_counts = suspicious_devices['cluster'].value_counts().sort_index()
cluster_counts.plot(kind='bar')
plt.xlabel('聚类')
plt.ylabel('设备数量')
plt.title('各聚类的设备数量')

# 各类型的设备数量
plt.subplot(2, 2, 4)
group_type_counts.plot(kind='bar')
plt.xlabel('设备类型')
plt.ylabel('设备数量')
plt.title('各类型的设备数量')

plt.tight_layout()
cluster_analysis_path = os.path.join(result_dir, 'cluster_analysis.png')
plt.savefig(cluster_analysis_path)
print(f"聚类分析可视化结果已保存至{cluster_analysis_path}")

# 计算团伙规模和交易特征
print("\n步骤4: 分析团伙规模和交易特征")

# 根据IP分组计算团伙规模
group_sizes = suspicious_devices.groupby('ip')['imei'].count().reset_index()
group_sizes.columns = ['ip', 'group_size']

# 计算每个团伙的交易特征平均值
group_stats = suspicious_devices.groupby('ip')[['trade_freq', 'trade_amount']].mean().reset_index()
group_stats = pd.merge(group_stats, group_sizes, on='ip', how='left')

# 按团伙规模排序
group_stats = group_stats.sort_values('group_size', ascending=False)

print("\n团伙规模和交易特征 (前10个):")
print(group_stats.head(10))

# 保存团伙分析结果
group_analysis_path = os.path.join(result_dir, 'group_analysis.csv')
group_stats.to_csv(group_analysis_path, index=False)
print(f"团伙分析结果已保存至{group_analysis_path}")

print("\n分析完成!")