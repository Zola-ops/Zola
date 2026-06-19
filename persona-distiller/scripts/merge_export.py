"""
合并微信和 QQ 导出文件为统一 CSV 格式
"""
import csv
import re
from datetime import datetime

def parse_wechat_line(line):
    """解析微信导出的一行"""
    # 格式: [2024-01-15 14:32:10] 张三: 消息内容
    # 或: [2024-01-15 14:32:10] 张三[我]: 消息内容
    
    match = re.match(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] (.+?): (.+)', line)
    if not match:
        return None
    
    time_str, sender, content = match.groups()
    is_self = '[我]' in sender
    sender = sender.replace('[我]', '').strip()
    
    return {
        'time': time_str,
        'platform': 'wechat',
        'sender': sender,
        'is_self': is_self,
        'type': 'text',
        'content': content.strip()
    }

def parse_qq_line(line):
    """解析 QQ 导出的一行"""
    # 格式与微信相同
    return parse_wechat_line(line)

def merge_exports(wechat_file, qq_file, output_csv, my_qq=None):
    """
    合并微信和 QQ 导出文件
    
    Args:
        wechat_file: 微信导出文件路径（可为 None）
        qq_file: QQ 导出文件路径（可为 None）
        output_csv: 输出 CSV 路径
        my_qq: 自己的 QQ 号
    """
    
    messages = []
    
    # 加载微信消息
    if wechat_file and os.path.exists(wechat_file):
        print(f"Loading WeChat: {wechat_file}")
        with open(wechat_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                msg = parse_wechat_line(line)
                if msg:
                    messages.append(msg)
        print(f"  Loaded {len(messages)} WeChat messages")
    
    # 加载 QQ 消息
    qq_start = len(messages)
    if qq_file and os.path.exists(qq_file):
        print(f"Loading QQ: {qq_file}")
        with open(qq_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                msg = parse_qq_line(line)
                if msg:
                    msg['platform'] = 'qq'
                    # 重新判断 is_self
                    if my_qq and my_qq in line:
                        msg['is_self'] = True
                    messages.append(msg)
        print(f"  Loaded {len(messages) - qq_start} QQ messages")
    
    # 按时间排序
    def parse_time(t):
        try:
            return datetime.strptime(t, '%Y-%m-%d %H:%M:%S')
        except:
            return datetime.min
    
    messages.sort(key=lambda x: parse_time(x['time']))
    
    # 输出 CSV
    with open(output_csv, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['time', 'platform', 'sender', 'is_self', 'type', 'content'])
        writer.writeheader()
        writer.writerows(messages)
    
    # 统计
    self_count = sum(1 for m in messages if m['is_self'])
    print(f"\n✓ Merged {len(messages)} messages to {output_csv}")
    print(f"  我的发言: {self_count} 条 ({self_count/len(messages)*100:.1f}%)")
    print(f"  微信: {len([m for m in messages if m['platform']=='wechat'])} 条")
    print(f"  QQ: {len([m for m in messages if m['platform']=='qq'])} 条")

def main():
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description="合并微信和 QQ 导出文件")
    parser.add_argument("--wechat", "-w", help="微信导出文件路径")
    parser.add_argument("--qq", "-q", help="QQ 导出文件路径")
    parser.add_argument("-o", "--output", required=True, help="输出 CSV 路径")
    parser.add_argument("--my-qq", help="自己的 QQ 号")
    
    args = parser.parse_args()
    
    if not args.wechat and not args.qq:
        print("错误: 请至少提供 --wechat 或 --qq")
        return
    
    merge_exports(args.wechat, args.qq, args.output, args.my_qq)

if __name__ == "__main__":
    main()
