"""
使用截获的密钥解密 QQ Msg3.0.db
"""
import sqlite3
import os
import sys
import shutil

def decrypt_qq_db(encrypted_db, key_hex, output_db):
    """
    解密 QQ 数据库
    
    Args:
        encrypted_db: 加密的 Msg3.0.db 路径
        key_hex: 密钥（空格分隔的十六进制，如 "ff 7c fa 12..."）
        output_db: 输出明文数据库路径
    """
    
    # 复制一份用于解密（避免损坏原文件）
    temp_db = output_db + ".tmp"
    shutil.copy(encrypted_db, temp_db)
    
    # 去掉空格，格式化为 SQLCipher 需要的格式
    key_clean = key_hex.replace(" ", "").replace("0x", "")
    
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    
    try:
        # 设置密钥
        cursor.execute(f"PRAGMA key = \"x'{key_clean}'\"")
        cursor.execute("PRAGMA cipher_page_size = 4096")
        cursor.execute("PRAGMA kdf_iter = 4000")
        
        # 验证密钥
        cursor.execute("SELECT count(*) FROM sqlite_master")
        count = cursor.fetchone()[0]
        print(f"✓ 密钥验证成功，数据库包含 {count} 个表")
        
        # 导出明文
        cursor.execute(f"ATTACH DATABASE '{output_db}' AS plaintext KEY ''")
        cursor.execute("SELECT sqlcipher_export('plaintext')")
        cursor.execute("DETACH DATABASE plaintext")
        
        print(f"✓ 解密完成: {output_db}")
        
    except Exception as e:
        print(f"✗ 解密失败: {e}")
        raise
    finally:
        conn.close()
        if os.path.exists(temp_db):
            os.remove(temp_db)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="解密 QQ Msg3.0.db")
    parser.add_argument("db", help="加密的 Msg3.0.db 路径")
    parser.add_argument("--key", "-k", help="密钥（十六进制，空格分隔）")
    parser.add_argument("--key-file", "-f", help="密钥文件路径")
    parser.add_argument("-o", "--output", required=True, help="输出明文数据库路径")
    
    args = parser.parse_args()
    
    # 获取密钥
    if args.key:
        key = args.key
    elif args.key_file:
        with open(args.key_file, 'r') as f:
            key = f.read().strip()
    else:
        print("错误: 请提供 --key 或 --key-file")
        sys.exit(1)
    
    print(f"解密: {args.db}")
    print(f"密钥: {key[:20]}...")
    print(f"输出: {args.output}")
    print("-" * 50)
    
    decrypt_qq_db(args.db, key, args.output)

if __name__ == "__main__":
    main()
