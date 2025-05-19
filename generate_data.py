import pandas as pd
import numpy as np
import random
import ipaddress
from datetime import datetime

# 设置随机种子以确保结果可重现
np.random.seed(42)
random.seed(42)

# 生成模拟数据
def generate_data(num_devices=1000, num_groups=3):
    # 创建空的数据框
    data = []
    
    # 生成3个明确的团伙IP和子网
    group_subnets = [
        "192.168.1",  # 第一个团伙的子网
        "172.16.10",  # 第二个团伙的子网
        "10.0.0"      # 第三个团伙的子网
    ]
    
    # 为每个团伙生成几个公网IP (模拟DHCP变化)
    group_ips = [
        [f"{group_subnets[0]}.{random.randint(1, 254)}" for _ in range(8)],  # 第一个团伙有8个IP
        [f"{group_subnets[1]}.{random.randint(1, 254)}" for _ in range(6)],  # 第二个团伙有6个IP
        [f"{group_subnets[2]}.{random.randint(1, 254)}" for _ in range(4)]   # 第三个团伙有4个IP
    ]
    
    # 定义每个团伙的特征
    group_features = [
        {  # 第一个团伙特征
            "leader": {
                "screen_time_range": (0.3, 1.5),     # 屏幕使用时间范围
                "trade_freq_range": (1, 3),         # 交易频率范围
                "trade_amount_range": (8000, 15000), # 交易金额范围
                "app_switches_range": (5, 20)        # 应用跳转次数范围
            },
            "meat_machine": {
                "screen_time_range": (4, 7),        # 屏幕使用时间范围
                "trade_freq_range": (10, 15),       # 交易频率范围
                "trade_amount_range": (100, 800),   # 交易金额范围
                "app_switches_range": (60, 90)      # 应用跳转次数范围
            }
        },
        {  # 第二个团伙特征
            "leader": {
                "screen_time_range": (0.5, 2),      # 屏幕使用时间范围
                "trade_freq_range": (2, 4),         # 交易频率范围
                "trade_amount_range": (10000, 20000), # 交易金额范围
                "app_switches_range": (8, 25)        # 应用跳转次数范围
            },
            "meat_machine": {
                "screen_time_range": (3, 6),        # 屏幕使用时间范围
                "trade_freq_range": (8, 12),        # 交易频率范围
                "trade_amount_range": (200, 1000),  # 交易金额范围
                "app_switches_range": (50, 80)      # 应用跳转次数范围
            }
        },
        {  # 第三个团伙特征
            "leader": {
                "screen_time_range": (0.2, 1),      # 屏幕使用时间范围
                "trade_freq_range": (1, 2),         # 交易频率范围
                "trade_amount_range": (12000, 25000), # 交易金额范围
                "app_switches_range": (10, 30)       # 应用跳转次数范围
            },
            "meat_machine": {
                "screen_time_range": (5, 8),        # 屏幕使用时间范围
                "trade_freq_range": (12, 18),       # 交易频率范围
                "trade_amount_range": (150, 600),   # 交易金额范围
                "app_switches_range": (70, 100)     # 应用跳转次数范围
            }
        }
    ]
    
    # 分配设备数量
    # 第一个团伙: 40% 的团伙设备
    # 第二个团伙: 35% 的团伙设备
    # 第三个团伙: 25% 的团伙设备
    # 总共70%的设备属于团伙，30%是正常用户
    group_device_counts = [
        int(num_devices * 0.4 * 0.7),  # 第一个团伙设备数量
        int(num_devices * 0.35 * 0.7), # 第二个团伙设备数量
        int(num_devices * 0.25 * 0.7)  # 第三个团伙设备数量
    ]
    
    # 确保总数正确
    total_group_devices = sum(group_device_counts)
    normal_devices = num_devices - total_group_devices
    
    # 生成设备数据
    data = []
    device_count = 0
    
    # 为每个团伙生成设备
    for group_id in range(num_groups):
        group_features_dict = group_features[group_id]
        device_count_in_group = group_device_counts[group_id]
        
        # 每个团伙中leader的数量 (约5%)
        leader_count = max(1, int(device_count_in_group * 0.05))
        
        # 生成leader设备
        for i in range(leader_count):
            subnet = group_subnets[group_id]
            ip = random.choice(group_ips[group_id])
            
            # 使用团伙特定的leader特征
            leader_features = group_features_dict["leader"]
            screen_time = random.uniform(*leader_features["screen_time_range"])
            trade_freq = random.uniform(*leader_features["trade_freq_range"])
            trade_amount = random.uniform(*leader_features["trade_amount_range"])
            app_switches = random.uniform(*leader_features["app_switches_range"])
            
            # 生成IMEI (15位数字)
            imei = ''.join([str(random.randint(0, 9)) for _ in range(15)])
            
            # 添加到数据集
            data.append({
                'imei': imei,
                'ip': ip,
                'subnet': subnet,
                'screen_time': screen_time,
                'trade_freq': trade_freq,
                'trade_amount': trade_amount,
                'app_switches': app_switches,
                'role': f"leader_group_{group_id+1}"  # 标记leader属于哪个团伙
            })
            device_count += 1
        
        # 生成肉机设备
        meat_machine_count = device_count_in_group - leader_count
        for i in range(meat_machine_count):
            subnet = group_subnets[group_id]
            ip = random.choice(group_ips[group_id])
            
            # 使用团伙特定的肉机特征
            meat_features = group_features_dict["meat_machine"]
            screen_time = random.uniform(*meat_features["screen_time_range"])
            trade_freq = random.uniform(*meat_features["trade_freq_range"])
            trade_amount = random.uniform(*meat_features["trade_amount_range"])
            app_switches = random.uniform(*meat_features["app_switches_range"])
            
            # 生成IMEI (15位数字)
            imei = ''.join([str(random.randint(0, 9)) for _ in range(15)])
            
            # 添加到数据集
            data.append({
                'imei': imei,
                'ip': ip,
                'subnet': subnet,
                'screen_time': screen_time,
                'trade_freq': trade_freq,
                'trade_amount': trade_amount,
                'app_switches': app_switches,
                'role': f"meat_machine_group_{group_id+1}"  # 标记肉机属于哪个团伙
            })
            device_count += 1
    
    # 生成正常用户设备
    for i in range(normal_devices):
        role = "normal"
        subnet = f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}"
        ip = f"{subnet}.{random.randint(1, 254)}"
        screen_time = random.uniform(1, 10)  # 正常用户屏幕使用时间分布广
        trade_freq = random.uniform(0.5, 10)  # 正常用户交易频率分布广
        trade_amount = random.uniform(50, 10000)  # 正常用户交易金额分布广
        app_switches = random.uniform(20, 150)  # 正常用户应用跳转次数分布广
        
        # 生成IMEI (15位数字)
        imei = ''.join([str(random.randint(0, 9)) for _ in range(15)])
        
        # 添加到数据集
        data.append({
            'imei': imei,
            'ip': ip,
            'subnet': subnet,
            'screen_time': screen_time,
            'trade_freq': trade_freq,
            'trade_amount': trade_amount,
            'app_switches': app_switches,
            'role': role
        })
        device_count += 1
        
        # 生成IMEI (15位数字)
        imei = ''.join([str(random.randint(0, 9)) for _ in range(15)])
        
        # 添加到数据集
        data.append({
            'imei': imei,
            'ip': ip,
            'subnet': subnet,
            'screen_time': screen_time,
            'trade_freq': trade_freq,
            'trade_amount': trade_amount,
            'app_switches': app_switches,
            'role': role  # 真实角色标签，仅用于验证
        })
    
    return pd.DataFrame(data)

# 生成数据并保存
df = generate_data(1000, 3)

# 添加一些统计信息
group_counts = df['role'].value_counts()
print("\n数据集统计信息:")
print(f"总设备数: {len(df)}")
for role, count in group_counts.items():
    print(f"{role}: {count}条记录")

# 保存数据
import os
data_dir = "/mnt/ymj/vivo/群控/data"
os.makedirs(data_dir, exist_ok=True)
data_path = os.path.join(data_dir, 'device_data.csv')
df.to_csv(data_path, index=False)
print(f"\n已生成{len(df)}条设备数据，保存至{data_path}")
print("包含3个明确的薅羊毛团体，每个团体都有特定的leader和肉机特征")