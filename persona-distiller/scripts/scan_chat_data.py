"""
扫描本地 QQ/微信聊天记录数据库文件
"""
import os
import glob
from pathlib import Path

def scan_wechat():
    """扫描微信数据目录"""
    base_paths = [
        Path.home() / "Documents" / "WeChat Files",
        Path.home() / "xwechat_files",
    ]
    
    accounts = []
    for base in base_paths:
        if not base.exists():
            continue
        for account_dir in base.iterdir():
            if not account_dir.is_dir():
                continue
            
            wxid = account_dir.name.replace("_a47a", "")
            
            # 旧版路径
            old_msg = account_dir / "Msg"
            # 新版路径
            new_msg = account_dir / "db_storage" / "message"
            
            old_dbs = list(old_msg.glob("MSG*.db")) if old_msg.exists() else []
            new_dbs = list(new_msg.glob("message_*.db")) if new_msg.exists() else []
            
            if old_dbs or new_dbs:
                accounts.append({
                    "wxid": wxid,
                    "path": str(account_dir),
                    "old_dbs": [str(d) for d in old_dbs],
                    "new_dbs": [str(d) for d in new_dbs],
                    "total_size_mb": sum(d.stat().st_size for d in old_dbs + new_dbs) / 1024 / 1024
                })
    
    return accounts

def scan_qq():
    """扫描 QQ 数据目录"""
    base_path = Path.home() / "Documents" / "Tencent Files"
    
    accounts = []
    if not base_path.exists():
        return accounts
    
    for account_dir in base_path.iterdir():
        if not account_dir.is_dir():
            continue
        
        qq_number = account_dir.name
        msg_db = account_dir / "Msg3.0.db"
        bak_file = account_dir / "Msg3.0.db.1.bak"
        
        if msg_db.exists() or bak_file.exists():
            accounts.append({
                "qq": qq_number,
                "path": str(account_dir),
                "main_db": str(msg_db) if msg_db.exists() else None,
                "bak_file": str(bak_file) if bak_file.exists() else None,
                "size_mb": (msg_db.stat().st_size if msg_db.exists() else 0) / 1024 / 1024
            })
    
    return accounts

def main():
    print("=" * 60)
    print("聊天记录数据库扫描结果")
    print("=" * 60)
    
    # 扫描微信
    print("\n📱 微信账号:")
    wechat_accounts = scan_wechat()
    if wechat_accounts:
        for acc in wechat_accounts:
            print(f"  • {acc['wxid']}")
            print(f"    路径: {acc['path']}")
            print(f"    数据库: 旧版 {len(acc['old_dbs'])} 个, 新版 {len(acc['new_dbs'])} 个")
            print(f"    总大小: {acc['total_size_mb']:.1f} MB")
    else:
        print("  未发现微信数据")
    
    # 扫描 QQ
    print("\n💬 QQ 账号:")
    qq_accounts = scan_qq()
    if qq_accounts:
        # 按大小排序
        qq_accounts.sort(key=lambda x: x['size_mb'], reverse=True)
        for acc in qq_accounts:
            print(f"  • {acc['qq']}")
            print(f"    路径: {acc['path']}")
            print(f"    主库: {'✓' if acc['main_db'] else '✗'}, 备份: {'✓' if acc['bak_file'] else '✗'}")
            print(f"    大小: {acc['size_mb']:.1f} MB")
    else:
        print("  未发现 QQ 数据")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
