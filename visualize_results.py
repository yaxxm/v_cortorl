import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from matplotlib.font_manager import FontProperties

# 自动检测Linux下的常用中文字体
font = None
try:
    font_candidates = [
        '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
        '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/truetype/arphic/ukai.ttc',
        '/usr/share/fonts/truetype/arphic/uming.ttc',
        '/usr/share/fonts/truetype/simhei.ttf',
        '/usr/share/fonts/truetype/simsun.ttf',
        '/usr/share/fonts/truetype/DroidSansFallbackFull.ttf'
    ]
    for fpath in font_candidates:
        if os.path.exists(fpath):
            font = FontProperties(fname=fpath)
            plt.rcParams['font.sans-serif'] = [os.path.splitext(os.path.basename(fpath))[0]]
            break
    if font is None:
        plt.rcParams['font.sans-serif'] = ['SimHei']
        font = FontProperties(fname=None)
    plt.rcParams['axes.unicode_minus'] = False
except Exception as e:
    print("警告: 无法加载中文字体，图表中的中文可能无法正确显示", e)

# 设置数据和结果路径
DATA_DIR = '/mnt/ymj/vivo/群控/data'
RESULT_DIR = '/mnt/ymj/vivo/群控/result'
VIS_DIR = os.path.join(RESULT_DIR, 'visualization')

# 检查分析结果文件是否存在
required_files = [
    os.path.join(RESULT_DIR, 'suspicious_devices.csv'),
    os.path.join(RESULT_DIR, 'group_leaders.csv'),
    os.path.join(RESULT_DIR, 'group_analysis.csv')
]
missing_files = [f for f in required_files if not os.path.exists(f)]

if missing_files:
    print(f"缺少以下分析结果文件: {', '.join(missing_files)}")
    print("请先运行 analyze_groups.py 生成分析结果")
    if not os.path.exists(os.path.join(DATA_DIR, 'device_data.csv')):
        print("数据文件不存在，正在生成模拟数据...")
        import generate_data
    print("正在运行分析脚本...")
    import analyze_groups

# 读取分析结果
print("正在读取分析结果...")
suspicious_devices = pd.read_csv(os.path.join(RESULT_DIR, 'suspicious_devices.csv'))
leaders = pd.read_csv(os.path.join(RESULT_DIR, 'group_leaders.csv'))
group_analysis = pd.read_csv(os.path.join(RESULT_DIR, 'group_analysis.csv'))

# 创建可视化结果目录
if not os.path.exists(VIS_DIR):
    os.makedirs(VIS_DIR)

# 1. 可疑设备分布热力图
plt.figure(figsize=(12, 10))
sns.heatmap(suspicious_devices[['screen_time', 'trade_freq', 'trade_amount', 'app_switches']].corr(), 
            annot=True, cmap='coolwarm', vmin=-1, vmax=1)
plt.title('可疑设备特征相关性热力图', fontproperties=font, fontsize=16)
plt.savefig(os.path.join(VIS_DIR, 'feature_correlation.png'), dpi=300, bbox_inches='tight')
plt.close()

# 2. 团伙规模分布
plt.figure(figsize=(14, 8))
sns.histplot(group_analysis['group_size'], bins=30, kde=True)
plt.title('团伙规模分布', fontproperties=font, fontsize=16)
plt.xlabel('团伙规模（设备数量）', fontproperties=font, fontsize=14)
plt.ylabel('频率', fontproperties=font, fontsize=14)
plt.savefig(os.path.join(VIS_DIR, 'group_size_distribution.png'), dpi=300, bbox_inches='tight')
plt.close()

# 3. 交易频率与交易金额散点图（按设备类型着色）
plt.figure(figsize=(14, 10))
sns.scatterplot(data=suspicious_devices, x='trade_freq', y='trade_amount', 
                hue='group_type', size='app_switches', sizes=(20, 200), alpha=0.7)
plt.title('交易频率与交易金额散点图（按设备类型）', fontproperties=font, fontsize=16)
plt.xlabel('交易频率', fontproperties=font, fontsize=14)
plt.ylabel('交易金额', fontproperties=font, fontsize=14)
plt.legend(prop=font)

# 标记leader位置
leaders_plot = suspicious_devices[suspicious_devices['group_type'] == '重大leader']
plt.scatter(leaders_plot['trade_freq'], leaders_plot['trade_amount'], 
            color='red', marker='*', s=300, label='Leader', edgecolor='black')
plt.savefig(os.path.join(VIS_DIR, 'trade_patterns.png'), dpi=300, bbox_inches='tight')
plt.close()

# 4. 团伙交易特征箱线图
plt.figure(figsize=(16, 8))

# 按团伙规模分组
group_analysis['size_category'] = pd.cut(group_analysis['group_size'], 
                                       bins=[0, 5, 10, 20, 50, 100, np.inf], 
                                       labels=['1-5', '6-10', '11-20', '21-50', '51-100', '>100'])

# 交易频率箱线图
plt.subplot(1, 2, 1)
sns.boxplot(x='size_category', y='trade_freq', data=group_analysis)
plt.title('不同规模团伙的交易频率分布', fontproperties=font, fontsize=16)
plt.xlabel('团伙规模', fontproperties=font, fontsize=14)
plt.ylabel('平均交易频率', fontproperties=font, fontsize=14)

# 交易金额箱线图
plt.subplot(1, 2, 2)
sns.boxplot(x='size_category', y='trade_amount', data=group_analysis)
plt.title('不同规模团伙的交易金额分布', fontproperties=font, fontsize=16)
plt.xlabel('团伙规模', fontproperties=font, fontsize=14)
plt.ylabel('平均交易金额', fontproperties=font, fontsize=14)

plt.tight_layout()
plt.savefig(os.path.join(VIS_DIR, 'group_trade_patterns.png'), dpi=300, bbox_inches='tight')
plt.close()

# 5. Leader特征雷达图
if not leaders.empty:
    # 选择前5个leader进行展示
    top_leaders = leaders.head(min(5, len(leaders)))
    # 准备雷达图数据
    categories = ['屏幕使用时间', '交易频率', '交易金额', '应用跳转次数', 'IP变化数']
    # 标准化特征
    from sklearn.preprocessing import MinMaxScaler
    scaler = MinMaxScaler()
    scaled_features = scaler.fit_transform(top_leaders[['screen_time', 'trade_freq', 'trade_amount', 'app_switches', 'ip_count']])
    # 创建雷达图
    plt.figure(figsize=(10, 8))
    # 设置雷达图的角度
    angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False).tolist()
    angles += angles[:1]  # 闭合雷达图
    # 绘制每个leader的雷达图
    ax = plt.subplot(111, polar=True)
    for i, leader in enumerate(top_leaders.iterrows()):
        values = scaled_features[i].tolist()
        values += values[:1]  # 闭合雷达图
        ax.plot(angles, values, linewidth=2, label=f"Leader {i+1}")
        ax.fill(angles, values, alpha=0.1)
    # 设置雷达图属性
    ax.set_thetagrids(np.degrees(angles[:-1]), categories, fontproperties=font)
    ax.set_ylim(0, 1)
    plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
    plt.title('团伙Leader特征雷达图', fontproperties=font, fontsize=16)
    plt.savefig(os.path.join(VIS_DIR, 'leader_radar.png'), dpi=300, bbox_inches='tight')
    plt.close()

# 6. 生成HTML报告
html_report = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>薅羊毛团体分析报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1, h2 {{ color: #333; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
        .stat-box {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; text-align: center; width: 200px; }}
        .stat-value {{ font-size: 24px; font-weight: bold; color: #0066cc; }}
        .stat-label {{ font-size: 14px; color: #666; }}
        .visualization {{ margin: 30px 0; }}
        .visualization img {{ max-width: 100%; border: 1px solid #ddd; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>薅羊毛团体分析报告</h1>
        <div class="stats">
            <div class="stat-box">
                <div class="stat-value">{len(suspicious_devices)}</div>
                <div class="stat-label">可疑设备总数</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{len(leaders)}</div>
                <div class="stat-label">识别出的团伙Leader</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{len(group_analysis)}</div>
                <div class="stat-label">识别出的团伙数量</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{group_analysis['group_size'].max()}</div>
                <div class="stat-label">最大团伙规模</div>
            </div>
        </div>
        <h2>分析结果可视化</h2>
        <div class="visualization">
            <h3>1. 可疑设备特征相关性</h3>
            <img src="feature_correlation.png" alt="特征相关性热力图">
            <p>此热力图展示了设备特征之间的相关性，帮助理解不同行为特征之间的关系。</p>
        </div>
        <div class="visualization">
            <h3>2. 团伙规模分布</h3>
            <img src="group_size_distribution.png" alt="团伙规模分布">
            <p>展示了不同团伙规模的分布情况。</p>
        </div>
        <div class="visualization">
            <h3>3. 交易模式散点图</h3>
            <img src="trade_patterns.png" alt="交易模式散点图">
            <p>不同设备类型在交易频率和金额上的分布。</p>
        </div>
        <div class="visualization">
            <h3>4. 团伙交易特征箱线图</h3>
            <img src="group_trade_patterns.png" alt="团伙交易特征箱线图">
            <p>不同规模团伙的交易频率和金额分布。</p>
        </div>
        <div class="visualization">
            <h3>5. Leader特征雷达图</h3>
            <img src="leader_radar.png" alt="Leader特征雷达图">
            <p>展示了团伙Leader的多维特征。</p>
        </div>
    </div>
</body>
</html>
'''

with open(os.path.join(VIS_DIR, 'report.html'), 'w', encoding='utf-8') as f:
    f.write(html_report)

print(f"可视化结果已保存至{VIS_DIR}")
print(f"可以打开{os.path.join(VIS_DIR, 'report.html')}查看完整分析报告")