"""
Frida Hook QQ 登录过程，截获 Msg3.0.db 密钥
使用方法：先运行此脚本，再启动 QQ 登录
"""
import frida
import sys
import os
import time
import shutil
import psutil

QQ_EXE = r"D:\QQ\Bin\QQ.exe"  # 修改为你的 QQ 路径
WORK_DIR = os.path.dirname(os.path.abspath(__file__))

def log(msg):
    print(msg)
    sys.stdout.flush()

# Frida Hook 脚本
HOOK_JS = r"""
const kernel_util = Module.load('KernelUtil.dll');
send("[+] KernelUtil.dll loaded at " + kernel_util.base);

function findFunc(pattern) {
    pattern = pattern.replaceAll("##", "").replaceAll(" ", "").toLowerCase().replace(/\s/g,'').replace(/(.{2})/g,"$1 ");
    var list = Memory.scanSync(kernel_util.base, kernel_util.size, pattern);
    if (list.length == 0) { send("ERROR: pattern NOT FOUND: " + pattern); return null; }
    return list[0]['address'];
}

var open_func = findFunc("##558BEC6A006A06FF750CFF7508E8E0130200");
var key_func  = findFunc("55 8b ec 56 6b 75 10 11 83 7d 10 10 74 0d 68 17 02 00 00 e8");
var rekey_func = findFunc("##558BEC837D1010740D682F020000E8");
var close_func = findFunc("##55 8B EC 56 8B  75 08 85 F6 74 6D 56 E87C 3E 01 00");
var name_func  = findFunc("55 8B EC FF 75 0C FF 75 08 E8 B8 D1 02 00 59 59 85");

if (!open_func || !key_func || !rekey_func || !close_func) {
    send("!!FAILED: Missing functions");
} else {
    send("[+] All functions found");
    
    var open_caller  = new NativeFunction(open_func,  'int', ['pointer', 'pointer']);
    var key_caller   = new NativeFunction(key_func,   'int', ['pointer', 'pointer', 'int']);
    var rekey_caller = new NativeFunction(rekey_func, 'int', ['pointer', 'pointer', 'int']);
    var close_caller = new NativeFunction(close_func, 'int', ['pointer', 'int']);
    var name_caller  = new NativeFunction(name_func,  'pointer', ['pointer', 'pointer']);
    
    var empty_password = Memory.alloc(16);
    empty_password.writeByteArray(Array(16).fill(0));
    var new_database_handle = Memory.alloc(128);
    var calling_key = false;
    var captured_key = null;
    
    function buf2hex(buffer) {
        var byteArray = new Uint8Array(buffer);
        var parts = [];
        for (var i = 0; i < byteArray.length; i++) {
            parts.push(('00' + byteArray[i].toString(16)).slice(-2));
        }
        return parts.join(' ');
    }
    
    Interceptor.attach(key_func, {
        onEnter: function(args) {
            if (calling_key) return;
            
            var dbName = null;
            try { dbName = name_caller(args[0], NULL).readUtf8String(); } catch(e) { return; }
            if (!dbName) return;
            
            var filename = dbName.replaceAll('/', '\\').split('\\').pop().toLowerCase();
            var keyLen = args[2].toInt32();
            
            if (filename.includes('msg3.0')) {
                send("[KEY] Database: " + filename);
                send("[KEY] Key length: " + keyLen);
                
                var keyData = Memory.readByteArray(args[1], keyLen);
                var keyHex = buf2hex(keyData);
                send("CAPTURED_KEY:" + keyHex);
                captured_key = keyHex;
                
                // Decrypt the .bak file
                try {
                    calling_key = true;
                    var result = open_caller(Memory.allocUtf8String(bakFile), new_database_handle);
                    send("[+] Open .bak result: " + result);
                    
                    if (result === 0) {
                        var dbPtr = Memory.readPointer(new_database_handle);
                        var key_result = key_caller(dbPtr, args[1], keyLen);
                        send("[+] Key set result: " + key_result);
                        
                        var rekey_result = rekey_caller(dbPtr, empty_password, 0);
                        send("[+] Rekey result: " + rekey_result);
                        
                        var close_result = close_caller(dbPtr, 0);
                        send("[+] Close result: " + close_result);
                        send("[+] Decryption complete!");
                    }
                    calling_key = false;
                } catch(e) {
                    send("ERROR: " + e.message);
                    calling_key = false;
                }
            }
        }
    });
}
"""

captured_key = None

def on_message(message, data):
    global captured_key
    if message['type'] == 'send':
        msg = message['payload']
        log(msg)
        if msg.startswith("CAPTURED_KEY:"):
            captured_key = msg.replace("CAPTURED_KEY:", "").strip()
            log(f"\n✅ 密钥已捕获: {captured_key}")
            # 保存到文件
            key_file = os.path.join(WORK_DIR, "qq_key.txt")
            with open(key_file, 'w') as f:
                f.write(captured_key)
            log(f"密钥已保存到: {key_file}")

def find_qq_process():
    """查找 QQ 进程"""
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] and 'qq' in proc.info['name'].lower():
            return proc.info['pid']
    return None

def main():
    log("=" * 60)
    log("QQ 密钥提取工具")
    log("=" * 60)
    log("\n使用步骤:")
    log("1. 确保 QQ 完全退出")
    log("2. 运行此脚本")
    log("3. 在脚本提示后，启动 QQ 并登录")
    log("4. 等待密钥自动捕获")
    log("=" * 60)
    
    # 检查是否有 QQ 在运行
    existing_pid = find_qq_process()
    if existing_pid:
        log(f"\n⚠️ 检测到 QQ 进程 (PID: {existing_pid})")
        log("请先完全退出 QQ，然后按 Enter 继续...")
        input()
    
    log("\n[1/3] 准备启动 QQ...")
    log(f"QQ 路径: {QQ_EXE}")
    
    try:
        # 启动 QQ
        pid = frida.spawn([QQ_EXE])
        log(f"[2/3] QQ 已启动 (PID: {pid})")
        
        # 附加进程
        session = frida.attach(pid)
        log("[3/3] 已附加到 QQ 进程")
        
        # 创建脚本
        script = session.create_script(HOOK_JS)
        script.on('message', on_message)
        script.load()
        
        # 恢复执行
        frida.resume(pid)
        log("\n🔄 等待 QQ 登录并捕获密钥...")
        log("(登录过程中会自动截获密钥)\n")
        
        # 等待
        try:
            while True:
                time.sleep(1)
                if captured_key:
                    log("\n✅ 任务完成，可以关闭此窗口")
                    break
        except KeyboardInterrupt:
            log("\n\n用户中断")
            
    except Exception as e:
        log(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
