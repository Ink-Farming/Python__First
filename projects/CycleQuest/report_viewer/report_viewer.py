"""主入口：串联读取 → 统计 → 生成报告。"""
from data_loader import load_data, parse_records
from stats import compute_stats
from html_generator import generate_html


def main():
    print("📂 正在读取历史数据...")
    raw = load_data()
    print("📊 正在分析数据...")
    records = parse_records(raw)
    stats = compute_stats(records)
    print("🎨 正在生成报告...")
    generate_html(records, stats)
    print("✨ 完成！")
    input("按回车退出...")


if __name__ == '__main__':
    main()