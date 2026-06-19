"""
从解密的微信数据库导出聊天记录
"""
import sqlite3
import os
import datetime
import json
import glob
from pathlib import Path

def ts_to_str(ts):
    """时间戳转字符串"""
    if not ts:
        return ""
    try:
        if isinstance(ts, (int, float)):
            if ts > 1e15: ts = ts / 1000000
            elif ts > 1e12: ts = ts / 1000
            return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        return str(ts)
    except:
        return str(ts)

def get_msg_type_name(t):
    """消息类型映射"""
    return {
        1: "text", 3: "image", 34: "voice", 43: "video", 47: "emoji",
        49: "link/app", 10000: "system", 10002: "system",
    }.get(t, f"type_{t}")

def load_contacts(contact_db):
    """加载联系人映射"""
    contacts = {}
    try:
        conn = sqlite3.connect(contact_db)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='tables'")
        tables = [r[0] for r in cur.fetchall()]
        
        for t in tables:
            try:
                cur.execute(f"PRAGMA table_info({t})")
                cols = [r[1] for r in cur.fetchall()]
                
                uid_col = None
                for c in ['username', 'usrName', 'wxid']:
                    if c in cols: 
                        uid_col = c
                        break
                
                name_cols = []
                for c in ['nickname', 'nickName', 'remark', 'dbContactRemark', 'NickName']:
                    if c in cols: 
                        name_cols.append(c)
                
                if uid_col:
                    select = f"SELECT {uid_col}" + "".join(f", {c}" for c in name_cols)
                    cur.execute(select)
                    for row in cur.fetchall():
                        uid = str(row[0]) if row[0] else ""
                        if uid:
                            for name in row[1:]:
                                if name and isinstance(name, str) and len(name) > 0:
                                    contacts[uid] = name
                                    break
                            if uid not in contacts:
                                contacts[uid] = uid
            except:
                pass
        conn.close()
    except Exception as e:
        print(f"Contact error: {e}")
    return contacts

def parse_wcdb_content(content_bytes):
    """
    解析 WCDB protobuf 格式的消息内容
    简化版：尝试提取文本
    """
    if not content_bytes:
        return ""
    
    if isinstance(content_bytes, str):
        return content_bytes
    
    # 尝试直接解码
    try:
        return content_bytes.decode('utf-8')
    except:
        pass
    
    # 尝试提取可打印字符
    text_parts = []
    current = bytearray()
    for b in content_bytes:
        if b >= 0x20 and b < 0x7f:
            current.append(b)
        elif b >= 0x80:
            current.append(b)
        else:
            if len(current) >= 2:
                try:
                    text = current.decode('utf-8')
                    text_parts.append(text)
                except:
                    pass
            current = bytearray()
    
    if len(current) >= 2:
        try:
            text = current.decode('utf-8')
            text_parts.append(text)
        except:
            pass
    
    return "".join(text_parts) if text_parts else "[二进制内容]"

def export_wechat(decrypted_dir, output_file, my_wxid=None):
    """
    导出微信聊天记录
    
    Args:
        decrypted_dir: 解密后的微信数据目录
        output_file: 输出文件路径
        my_wxid: 自己的微信ID，用于判断 is_self
    """
    
    contact_db = os.path.join(decrypted_dir, 'contact', 'contact.db')
    session_db = os.path.join(decrypted_dir, 'session', 'session.db')
    msg_dir = os.path.join(decrypted_dir, 'message')
    
    # 加载联系人
    print("Loading contacts...")
    contacts = load_contacts(contact_db) if os.path.exists(contact_db) else {}
    print(f"Loaded {len(contacts)} contacts")
    
    # 加载会话映射
    sessions = {}
    if os.path.exists(session_db):
        conn = sqlite3.connect(session_db)
        for row in conn.execute("SELECT session_id, user_id FROM session"):
            sessions[row[0]] = row[1]
        conn.close()
    
    # 导出消息
    messages = []
    db_files = sorted(glob.glob(os.path.join(msg_dir, 'message_*.db')))
    
    print(f"Found {len(db_files)} message databases")
    
    for db_file in db_files:
        print(f"Processing {os.path.basename(db_file)}...")
        conn = sqlite3.connect(db_file)
        
        # 获取表结构
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'message%'")
        tables = [r[0] for r in cursor.fetchall()]
        
        for table in tables:
            try:
                cursor = conn.execute(f"SELECT createTime, talkerId, content, type, isSender FROM {table}")
                for row in cursor:
                    ts, talker_id, content, msg_type, is_sender = row
                    
                    talker_name = contacts.get(talker_id, sessions.get(talker_id, str(talker_id)))
                    msg_text = parse_wcdb_content(content)
                    
                    messages.append({
                        'time': ts_to_str(ts),
                        'talker': talker_name,
                        'is_self': bool(is_sender),
                        'type': get_msg_type_name(msg_type),
                        'content': msg_text
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
    
    parser = argparse.ArgumentParser(description="导出微信聊天记录")
    parser.add_argument("--db-dir", "-d", required=True, help="解密后的微信数据目录")
    parser.add_argument("-o", "--output", required=True, help="输出文件路径")
    parser.add_argument("--my-wxid", help="自己的微信ID")
    
    args = parser.parse_args()
    
    export_wechat(args.db_dir, args.output, args.my_wxid)

if __name__ == "__main__":
    main()
