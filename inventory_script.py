import xml.etree.ElementTree as ET
from decimal import Decimal
import argparse
import csv


def parse_inventory(xml_file):
    """解析XML库存文件"""
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
    except Exception as e:
        print(f"无法解析XML文件：{e}")
        return []

    items = []
    for item in root.findall("item"):
        try:
            item_id = item.find("id").text.strip()
            name = item.find("name").text.strip()
            category = item.find("category").text.strip()
            quantity = int(item.find("quantity").text.strip())
            price = Decimal(item.find("unit_price").text.strip())
            items.append({
                "id": item_id,
                "name": name,
                "category": category,
                "quantity": quantity,
                "unit_price": price,
                "value": quantity * price
            })
        except Exception as e:
            print(f"跳过无效记录：{e}")
            continue
    return items


def analyze_inventory(items, threshold):
    """分析库存数据，返回低库存项和总价值"""
    low_stock_items = [item for item in items if item["quantity"] < threshold]
    total_value = sum(item["value"] for item in items)
    category_summary = {}

    for item in items:
        cat = item["category"]
        category_summary[cat] = category_summary.get(cat, Decimal("0")) + item["value"]

    return low_stock_items, total_value, category_summary


def export_csv(filename, items):
    """导出低库存物品到CSV"""
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=items[0].keys())
        writer.writeheader()
        writer.writerows(items)
    print(f"已导出CSV文件：{filename}")


def main():
    parser = argparse.ArgumentParser(description="库存数据分析脚本")
    parser.add_argument("--file", type=str, default="inventory.xml", help="XML文件路径")
    parser.add_argument("--threshold", type=int, default=10, help="低库存阈值")
    parser.add_argument("--output", type=str, default="low_stock.csv", help="导出CSV文件名")

    args = parser.parse_args()

    items = parse_inventory(args.file)
    if not items:
        print("无有效库存数据，程序终止。")
        return

    low_stock_items, total_value, category_summary = analyze_inventory(items, args.threshold)

    print("\n=== 库存分析报告 ===")
    print(f"总库存记录数：{len(items)}")
    print(f"低于阈值({args.threshold})的物品数量：{len(low_stock_items)}")
    print(f"库存总价值：{total_value:.2f}\n")

    print("—— 分类汇总 ——")
    for cat, val in category_summary.items():
        print(f"{cat:<15} : {val:.2f}")

    if low_stock_items:
        print("\n—— 低库存清单 ——")
        for item in low_stock_items:
            print(f"{item['id']:>4} | {item['name']:<20} | 库存: {item['quantity']:>3} | 单价: {item['unit_price']:.2f}")
        export_csv(args.output, low_stock_items)
    else:
        print("\n没有低库存物品。")

if __name__ == "__main__":
    main()