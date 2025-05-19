import os
import time
import sys

def print_header(message):
    """打印带有格式的标题"""
    print("\n" + "=" * 80)
    print(f" {message} ".center(80, "="))
    print("=" * 80 + "\n")

def run_step(step_name, module_name):
    """运行指定步骤"""
    print_header(f"正在执行: {step_name}")
    try:
        if module_name == "generate_data":
            import generate_data
        elif module_name == "analyze_groups":
            import analyze_groups
        elif module_name == "visualize_results":
            import visualize_results
        print(f"\n{step_name}执行完成!")
        return True
    except Exception as e:
        print(f"\n执行{step_name}时出错: {str(e)}")
        return False

def check_dependencies():
    """检查依赖包是否已安装"""
    try:
        import pandas
        import numpy
        import matplotlib
        import seaborn
        import sklearn
        return True
    except ImportError as e:
        print(f"缺少必要的依赖包: {str(e)}")
        print("请先运行: pip install -r requirements.txt")
        return False

def main():
    """主函数，运行整个分析流程"""
    print_header("薅羊毛团体识别系统")
    
    # 检查依赖包
    if not check_dependencies():
        return
    
    # 检查是否需要重新生成数据
    regenerate = False
    if len(sys.argv) > 1 and sys.argv[1] == "--regenerate":
        regenerate = True
    
    # 步骤1: 生成数据
    data_path = "/mnt/ymj/vivo/群控/data/device_data.csv"
    if not os.path.exists(data_path) or regenerate:
        if not run_step("步骤1: 生成模拟数据", "generate_data"):
            return
    else:
        print(f"数据文件已存在于 {data_path}，跳过数据生成步骤。如需重新生成数据，请使用参数 --regenerate")
    
    # 步骤2: 分析数据
    if not run_step("步骤2: 分析薅羊毛团体", "analyze_groups"):
        return
    
    # 步骤3: 可视化结果
    if not run_step("步骤3: 可视化分析结果", "visualize_results"):
        return
    
    print_header("分析完成")
    result_dir = "/mnt/ymj/vivo/群控/result"
    print("分析结果文件:")
    print(f"  - {result_dir}/suspicious_devices.csv: 可疑设备数据")
    print(f"  - {result_dir}/group_leaders.csv: 团伙领导者信息")
    print(f"  - {result_dir}/group_analysis.csv: 团伙规模和交易特征")
    print("\n可视化结果:")
    print(f"  - {result_dir}/cluster_analysis.png: 聚类分析图")
    print(f"  - {result_dir}/visualization/: 详细可视化结果目录")
    print(f"  - {result_dir}/visualization/report.html: 完整分析报告")
    
    # 提示用户如何查看报告
    print(f"\n请使用浏览器打开 {result_dir}/visualization/report.html 查看完整分析报告")

if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    print(f"\n总运行时间: {end_time - start_time:.2f} 秒")