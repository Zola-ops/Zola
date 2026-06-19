"""
从解密的 QQ 数据库导出聊天记录
解析 QQ MSG 二进制格式
"""
import sqlite3
import os
import datetime
import struct

def extract_text_from_msg(data):
    """
    从 QQ MSG 二进制格式提取文本
    
    QQ MSG 格式:
    - 头部: "MSG\x00\x00\x00\x00\x00" (8字节)
    - 后面是 protobuf 结构，文本以 UTF-8 存储
    """
    if not data or not isinstance(data, bytes):
        return None
    
    if len(data) < 8:
        return None
    
    # 扫描可打印 UTF-8 序列
    text_parts = []
    current = bytearray()
    
    for b in data:
        if b >= 0x20 and b < 0x7f:
            current.append(b)
        elif b >= 0x80:  # UTF-8 continuation
            current.append(b)
        else:
            if len(current) >= 4:
                try:
                    text = current.decode('utf-8')
                    # 过滤：必须有中文或足够长的英文
                    if any(ord(c) > 0x4e00 for c in text) or (len(text) >= 10 and text.isprintable()):
                        text_parts.append(text)
                except:
                    pass
            current = bytearray()
    
    # 处理最后一段
    if len(current) >= 4:
        try:
            text = current.decode('utf-8')
            if any(ord(c) > 0x4e00 for c in text) or (len(text) >= 10 and text.isprintable()):
                text_parts.append(text)
        except:
            pass
    
    # 过滤元数据
    filtered = []
    for t in text_parts:
        # 跳过短字符串
        if len(t) <= 3 and not any(ord(c) > 0x4e00 for c in t):
            continue
        # 跳过路径/URL
        if t.startswith('OSRoot:') or t.startswith('C:\\') or t.startswith('http'):
            continue
        # 跳过常见元数据
        if t in ['QQ', 'Msg', 'Time', 'Sender']:
            continue
        filtered.append(t)
    
    return ' '.join(filtered) if filtered else None

def ts_to_str(ts):
    """QQ 时间戳转字符串"""
    if not ts:
        return ""
    try:
        # QQ 时间戳通常是秒级
        if isinstance(ts, (int, float)):
            return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        return str(ts)
    except:
        return str(ts)

def export_qq(decrypted_db, output_file, my_qq=None):
    """
    导出 QQ 聊天记录
    
    Args:
        decrypted_db: 解密的 Msg3.0.db 路径
        output_file: 输出文件路径
        my_qq: 自己的 QQ 号，用于判断 is_self
    """
    
    conn = sqlite3.connect(decrypted_db)
    cursor = conn.cursor()
    
    # 获取所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    all_tables = [r[0] for r in cursor.fetchall()]
    
    # 好友消息表: buddy_xxx
    buddy_tables = [t for t in all_tables if t.startswith('buddy_') and not t.endswith('_Del')]
    # 群消息表: group_xxx
    group_tables = [t for t in all_tables if t.startswith('group_') and not t.endswith('_Del')]
    
    print(f"Found {len(buddy_tables)} buddy tables, {len(group_tables)} group tables")
    
    messages = []
    
    # 导出好友消息
    for table in buddy_tables:
        try:
            # 获取表结构
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [r[1] for r in cursor.fetchall()]
            
            # 查找列名
            time_col = 'Time' if 'Time' in columns else columns[0]
            sender_col = 'SenderUin' if 'SenderUin' in columns else None
            content_col = 'MsgContent' if 'MsgContent' in columns else None
            
            if not content_col:
                continue
            
            # 查询消息
            query = f"SELECT {time_col}, {sender_col or '1'}, {content_col} FROM {table} ORDER BY {time_col}"
            cursor.execute(query)
            
            for row in cursor.fetchall():
                ts, sender, content = row
                text = extract_text_from_msg(content)
                
                if text:
                    is_self = (str(sender) == str(my_qq)) if my_qq else False
                    messages.append({
                        'time': ts_to_str(ts),
                        'talker': table.replace('buddy_', ''),
                        'sender': sender,
                        'is_self': is_self,
                        'type': 'text',
                        'content': text
                    })
        except Exception as e:
            print(f"Error reading {table}: {e}")
    
    # 导出群消息
    for table in group_tables:
        try:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [r[1] for r in cursor.fetchall()]
            
            time_col = 'Time' if 'Time' in columns else columns[0]
            sender_col = 'SenderUin' if 'SenderUin' in columns else None
            content_col = 'MsgContent' if 'MsgContent' in columns else None
            
            if not content_col:
                continue
            
            query = f"SELECT {time_col}, {sender_col or '1'}, {content_col} FROM {table} ORDER BY {time_col}"
            cursor.execute(query)
            
            for row in cursor.fetchall():
                ts, sender, content = row
                text = extract_text_from_msg(content)
                
                if text:
                    is_self = (str(sender) == str(my_qq)) if my_qq else False
                    messages.append({
                        'time': ts_to_str(ts),
                        'talker': f"群:{table.replace('group_', '')}",
                        'sender': sender,
                        'is_self': is_self,
                        'type': 'text',
                        'content': text
                    })
        except Exception as e:
            print(f"Error reading {table}: {e}")
    
    conn.close()
    
    # 按时间排序
    messages.sort(key=lambda x: x['time'])
    
    # 输出
    with open(output_file, 'w', encoding='utf-8') as f:
        for msg in messages:
            self_mark = "[我]" if msg['is_self'] else ""
            f.write(f"[{msg['time']}] {msg['talker']}{self_mark}: {msg['content']}\n")
    
    print(f"\n✓ Exported {len(messages)} messages to {output_file}")
    return len(messages)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="导出 QQ 聊天记录")
    parser.add_argument("db", help="解密的 Msg3.0.db 路径")
    parser.add_argument("-o", "--output", required=True, help="输出文件路径")
    parser.add_argument("--my-qq", help="自己的 QQ 号")
    
    args = parser.parse_args()
    
    export_qq(args.db, args.output, args.my_qq)

if __name__ == "__main__":
    main()
