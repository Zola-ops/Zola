# Persona Distiller 快速开始

端到端流程：从原始聊天记录到 AI 人设 Skill。

## 安装依赖

```bash
pip install pywxdump frida psutil
```

## 完整流程

### 步骤 1: 提取聊天记录

```bash
# 1.1 扫描本地数据
python scripts/scan_chat_data.py

# 1.2 Hook QQ 密钥（需要 QQ 登录）
python scripts/hook_qq_key.py

# 1.3 解密 QQ 数据库
python scripts/decrypt_qq_with_key.py --key <密钥> --input Msg3.0.db.1.bak --output decrypted.db

# 1.4 导出微信消息
python scripts/export_wechat.py --input wechat-decrypt/decrypted/ --output wechat.csv

# 1.5 导出 QQ 消息
python scripts/export_qq.py --input decrypted.db --output qq.csv

# 1.6 合并为统一 CSV
python scripts/merge_export.py --wechat wechat.csv --qq qq.csv --output all_messages.csv
```

### 步骤 2: 语言特征分析

```bash
python scripts/analyze_speech.py --input all_messages.csv --output speech_report.txt
```

查看 `speech_report.txt`，了解语言特征。

### 步骤 3: 蒸馏成人设 MD

```bash
python scripts/distill_persona.py --report speech_report.txt --name "张三" --output persona_skill.md
```

### 步骤 4: 手动补充

生成的人设 MD 需要手动补充：
1. **人设知识图谱**：基本信息、职业路径、教育背景、城市记忆、兴趣偏好
2. **模拟指南**：聊天风格、正式写作风格、禁忌
3. **典型句式**：根据随机长句样本调整

### 步骤 5: 测试和优化

1. 将人设 MD 放入 `~/.workbuddy/skills/<人名>/SKILL.md`
2. 让 AI 加载 Skill，生成回复
3. 对比真实语料，调整不准确的特征描述
4. 重复直到效果满意

## 快速开始（已有 CSV）

如果已经有导出的 CSV 文件，可以直接从步骤 2 开始：

```bash
# 直接分析
python scripts/analyze_speech.py --input all_messages.csv --output speech_report.txt

# 蒸馏成人设 MD
python scripts/distill_persona.py --report speech_report.txt --name "张三" --output persona_skill.md
```

## 输出文件

| 文件 | 说明 |
|------|------|
| `all_messages.csv` | 合并后的聊天记录（统一格式） |
| `speech_report.txt` | 语言特征分析报告 |
| `persona_skill.md` | 人设 Skill MD（需要手动补充） |

## 故障排除

**问题**: 提取到 0 条文本
- 检查 CSV 列索引是否正确
- 确认"是否我的发言"列的值（是/True/1）
- 检查文件编码（工具自动处理 UTF-8）

**问题**: 人设 MD 效果不好
- 检查分析报告是否准确（样本量是否足够，建议 > 1 万条）
- 补充更多项目文档/简历信息
- 调整模拟指南的规则描述
- 增加"禁忌"部分（明确不应该做什么）

**问题**: QQ Hook 抓不到密钥
- QQ 登录时会重启进程，Hook 脚本需能自动重新 attach
- 使用 `.bak` 备份文件触发解密流程
- 检查 `KernelUtil.dll` 版本是否匹配
