# Persona Distiller - 人设蒸馏 Skill

端到端流程：从原始聊天记录到 AI 人设 Skill 的完整流水线。

## 整体流程

```
原始数据 → 提取聊天记录 → 导出为 CSV → 语言特征分析 → 蒸馏成人设 MD
   ↓            ↓              ↓              ↓                ↓
QQ/微信    解密数据库      统一格式        统计分析         SKILL.md
```

## 阶段一：数据提取

### 1.1 扫描定位

目标：找到本地聊天记录数据库文件。

**微信数据位置**：
```
旧版: C:\Users\<用户名>\Documents\WeChat Files\<wxid>\Msg\
新版: C:\Users\<用户名>\xwechat_files\<wxid>_a47a\db_storage\
```

**QQ 数据位置**：
```
C:\Users\<用户名>\Documents\Tencent Files\<QQ号>\Msg3.0.db
C:\Users\<用户名>\Documents\Tencent Files\<QQ号>\Msg3.0.db.1.bak
```

**关键文件**：
- 微信：`MSG0.db`~`MSG5.db` (旧版), `message_0.db`~`message_3.db` (新版)
- QQ：`Msg3.0.db` (主库), `Msg3.0index.db` (索引)

### 1.2 解密数据库

**微信解密**：
```bash
pip install pywxdump
pywxdump bias_addr      # 从内存提取密钥
pywxdump db_decrypt     # 解密数据库
```

**QQ 解密（Frida Hook）**：
- QQ 使用 `KernelUtil.dll` 进行 SQLCipher 加密
- 密钥在首次打开数据库时通过 `key_func` 传入
- 需要用 Frida Hook 截获密钥，再用 SQLCipher 解密
- 详细步骤见 `scripts/hook_qq_key.py`

### 1.3 导出为 CSV

将解密后的数据库导出为统一格式：

```
时间, 平台, 发送者, 是否我的发言, 消息类型, 内容
```

**微信导出**：解析 WCDB protobuf 格式，提取文本内容
**QQ 导出**：解析 MSG 自定义格式（以 `MSG\x00` 开头）

导出脚本：`scripts/export_wechat.py`、`scripts/export_qq.py`

### 1.4 合并

将微信和 QQ 的 CSV 合并为一个文件，按时间排序：

```bash
python scripts/merge_export.py --wechat wechat.csv --qq qq.csv --output all_messages.csv
```

## 阶段二：语言特征分析

### 2.1 提取"我的发言"

从合并后的 CSV 中过滤出 `是否我的发言=是` 且 `消息类型=text` 的记录。

### 2.2 运行分析脚本

```bash
python scripts/analyze_speech.py --input all_messages.csv --output speech_report.txt
```

### 2.3 分析维度

| 维度 | 说明 | 用途 |
|------|------|------|
| 语气词频率 | 口头禅、情绪词统计 | 构建"口头禅"列表 |
| 句尾字偏好 | 个人独特的句尾习惯 | 调整生成风格 |
| 高频短句 | 1-12 字的重复表达 | 学习自动化回复模式 |
| 典型中长句 | 13-50 字的完整句式 | 学习句式结构 |
| 标点符号 | 句号/省略号/无标点偏好 | 调整标点风格 |
| 中英混用 | 英文单词和 Emoji 比例 | 调整语言混合度 |
| 文本长度分布 | 1-5字/6-15字/16-30字占比 | 判断极简/详细风格 |
| 场景分布 | 技术/日常/学习/情感/游戏 | 调整话题权重 |

### 2.4 输出报告

分析报告包含：
- 语气词 TOP 60
- 句尾字 TOP 30
- 高频短句 TOP 80
- 典型中长句 TOP 50
- 标点符号 TOP 20
- 基础统计（总条数、平均长度、英文比例、Emoji 比例）
- 场景关键词覆盖率
- 随机长句样本 × 30

## 阶段三：蒸馏成人设 MD

### 3.1 人设 MD 结构

```
## 语言风格特征
  ### 高频口头禅
  ### 句尾偏好
  ### 典型句式
  ### 标点习惯

## 人设知识图谱
  ### 基本信息
  ### 职业路径
  ### 教育背景
  ### 城市记忆
  ### 兴趣偏好

## 模拟指南
  ### 聊天风格
  ### 正式写作风格
  ### 禁忌
```

### 3.2 从分析报告提取特征

**高频口头禅**：从"语气词频率 TOP 60"中选取出现频率 > 1% 的词
**句尾偏好**：从"句尾字 TOP 30"中总结规律
**典型句式**：从"随机长句样本"中提取句式模式
**标点习惯**：从"标点符号 TOP 20"中总结偏好

### 3.3 补充人设知识

除了聊天记录，还需要：
- **简历/工作文档**：职业路径、技能栈、项目经验
- **社交平台**：朋友圈、微博、小红书等公开内容
- **自我介绍**：让用户提供关键信息（民族、星座、MBTI 等）
- **项目文档**：毕业论文、课程作业、工作总结

### 3.4 编写模拟指南

模拟指南是 AI 执行的核心规则，需要明确：
- **应该做什么**：短句优先、情绪化、标点随意
- **不应该做什么**：不用破折号、不反问、不用 AI 味表达
- **边界案例**：如何处理特定场景（工作汇报、正式邮件、日常聊天）

### 3.5 迭代优化

人设 MD 不是一次写成的，需要：
1. **初版**：基于分析报告 + 基础信息
2. **测试**：让 AI 用人设 MD 生成回复，对比真实语料
3. **修正**：调整不准确的特征描述
4. **精简**：删除无关信息，保留核心特征
5. **重复**：直到生成效果满意

## 脚本清单

| 脚本 | 功能 | 使用阶段 |
|------|------|----------|
| `scan_chat_data.py` | 自动扫描本地 QQ/微信数据 | 阶段一 |
| `hook_qq_key.py` | Frida Hook 截获 QQ 密钥 | 阶段一 |
| `decrypt_qq_with_key.py` | SQLCipher 解密 QQ 数据库 | 阶段一 |
| `export_wechat.py` | 微信消息导出（WCDB 解析） | 阶段一 |
| `export_qq.py` | QQ 消息导出（MSG 格式解析） | 阶段一 |
| `merge_export.py` | 合并为统一 CSV | 阶段一 |
| `analyze_speech.py` | 语言特征分析 | 阶段二 |
| `distill_persona.py` | 从分析报告蒸馏成人设 MD | 阶段三 |

## 使用示例

### 完整流程

```bash
# 阶段一：提取聊天记录
python scripts/scan_chat_data.py
python scripts/hook_qq_key.py
python scripts/decrypt_qq_with_key.py
python scripts/export_wechat.py --input decrypted/ --output wechat.csv
python scripts/export_qq.py --input decrypted.db --output qq.csv
python scripts/merge_export.py --wechat wechat.csv --qq qq.csv --output all_messages.csv

# 阶段二：语言特征分析
python scripts/analyze_speech.py --input all_messages.csv --output speech_report.txt

# 阶段三：蒸馏成人设 MD
python scripts/distill_persona.py --report speech_report.txt --docs ./project_docs/ --output persona_skill.md
```

### 快速开始（已有 CSV）

如果已经有导出的 CSV 文件，可以直接从阶段二开始：

```bash
python scripts/analyze_speech.py --input all_messages.csv --output speech_report.txt
python scripts/distill_persona.py --report speech_report.txt --output persona_skill.md
```

## 适用范围与可移植性

### 适用场景

| 场景 | 是否支持 | 说明 |
|------|---------|------|
| 本机完整流程 | ✅ 支持 | 从原始数据到最终人设 MD，一键执行 |
| 换一台自己的电脑 | ✅ 支持 | 需在新电脑重新执行**阶段一（数据提取）** |
| 分享给朋友使用 | ✅ 支持 | 朋友使用自己的聊天数据，跑相同脚本 |
| 直接拷贝解密后数据给朋友 | ❌ 不支持 | 涉及隐私，且朋友无你的密钥无法使用 |
| 跨平台（Windows→Mac） | ⚠️ 部分支持 | 阶段二/三（分析+蒸馏）跨平台，阶段一需适配 |

### 前置条件

**每台目标机器必须各自完成**：

1. **安装聊天软件**：微信/QQ 需在本机安装并登录
2. **重新解密**：密钥是**本机+本账号**特有的，必须重新执行：
   - 微信：运行 `pywxdump` 从本机内存提取密钥
   - QQ：运行 Frida Hook 脚本截获本机密钥
3. **导出 CSV**：使用解密后的本地数据库，运行导出脚本

**可以跨机器共享的**：
- ✅ Skill 脚本（`scripts/` 目录）
- ✅ 技术文档（`SKILL.md`、`QUICKSTART.md`）
- ✅ 已导出的 CSV 文件（如果愿意分享）
- ✅ 已生成的人设 MD（如果愿意分享）

**不能跨机器共享的**：
- ❌ 原始加密数据库（密钥不匹配）
- ❌ 密钥文件（`all_keys.json`、Frida Hook 抓到的密钥）
- ❌ 解密后的数据库（包含隐私，且绑定本机账号）

### 快速开始（不同场景）

**场景 1：本机首次使用**
```bash
# 完整流程（阶段一→二→三）
python scripts/scan_chat_data.py
python scripts/hook_qq_key.py
python scripts/export_wechat.py --input decrypted/ --output wechat.csv
python scripts/export_qq.py --input decrypted.db --output qq.csv
python scripts/merge_export.py --wechat wechat.csv --qq qq.csv --output all_messages.csv
python scripts/analyze_speech.py --input all_messages.csv --output speech_report.txt
python scripts/distill_persona.py --report speech_report.txt --output persona_skill.md
```

**场景 2：换了一台电脑（已有旧电脑的 CSV）**
```bash
# 跳过阶段一，直接从阶段二开始
python scripts/analyze_speech.py --input all_messages.csv --output speech_report.txt
python scripts/distill_persona.py --report speech_report.txt --output persona_skill.md
```

**场景 3：分享给朋友使用**
```bash
# 朋友需要在自己电脑上完整执行阶段一→二→三
# 你可以分享：scripts/ 目录、SKILL.md、QUICKSTART.md
# 朋友使用自己的微信/QQ数据，运行相同脚本
```

**场景 4：只有解密后的数据库（无原始加密数据）**
```bash
# 从导出步骤开始
python scripts/export_wechat.py --input decrypted/ --output wechat.csv
python scripts/export_qq.py --input decrypted.db --output qq.csv
python scripts/merge_export.py --wechat wechat.csv --qq qq.csv --output all_messages.csv
python scripts/analyze_speech.py --input all_messages.csv --output speech_report.txt
python scripts/distill_persona.py --report speech_report.txt --output persona_skill.md
```

### 隐私与安全

1. **本地处理原则**：所有解密和分析都在本地进行，无网络传输
2. **密钥安全**：密钥文件（`all_keys.json`、Hook 日志）需妥善保管，建议加入 `.gitignore`
3. **数据共享**：如果分享 CSV 或人设 MD，需确保已去除敏感信息
4. **合法合规**：仅用于提取**自己的**聊天记录，不得用于监控他人

---

## 技术要点

### 加密机制

| 特性 | 微信 | QQ |
|------|------|-----|
| 加密算法 | AES-256-CBC / SQLCipher | SQLCipher |
| 密钥来源 | 微信进程内存 | KernelUtil.dll |
| 密钥获取 | pywxdump 自动提取 | Frida Hook 截获 |
| 消息格式 | WCDB Protobuf | QQ MSG 自定义 |

### 常见问题

**Q: 微信解密失败？**
- 确保微信处于登录状态
- 尝试使用 `pywxdump bias_addr` 自动定位密钥
- 检查微信版本是否受支持

**Q: QQ Hook 抓不到密钥？**
- QQ 登录时会重启进程，Hook 脚本需能自动重新 attach
- 使用 `.bak` 备份文件触发解密流程
- 检查 `KernelUtil.dll` 版本是否匹配

**Q: 消息内容乱码？**
- 微信：检查 WCDB protobuf 解析是否正确
- QQ：MSG 格式可能变化，需调整提取逻辑

**Q: 人设 MD 效果不好？**
- 检查分析报告是否准确（样本量是否足够）
- 补充更多项目文档/简历信息
- 调整模拟指南的规则描述
- 增加"禁忌"部分（明确不应该做什么）

## 输出规范

### 人设 MD 模板

```markdown
# <人名> Skill

## 语言风格特征

### 高频口头禅
- <口头禅1>: <出现频率>
- <口头禅2>: <出现频率>

### 句尾偏好
- 高频：<句尾字1>、<句尾字2>
- 低频：<句尾字3>、<句尾字4>

### 典型句式
- <句式1>
- <句式2>

### 标点习惯
- <标点1>: <偏好描述>
- <标点2>: <偏好描述>

## 人设知识图谱

### 基本信息
- 姓名: <姓名>
- 民族: <民族>
- 星座: <星座>
- MBTI: <MBTI>

### 职业路径
- <时间>: <公司> - <职位>
- <时间>: <公司> - <职位>

### 教育背景
- <学校> - <专业> - <时间>

### 城市记忆
- <城市>: <情感倾向> - <关键记忆>

### 兴趣偏好
- <兴趣1>: <偏好描述>
- <兴趣2>: <偏好描述>

## 模拟指南

### 聊天风格
1. <规则1>
2. <规则2>
3. <规则3>

### 正式写作风格
1. <规则1>
2. <规则2>

### 禁忌
- 不用<表达方式1>
- 不用<表达方式2>
```

## 安全与合规

⚠️ **重要提示**：
1. 本 Skill 仅用于提取**自己的**聊天记录
2. 密钥提取仅在本地进行，不会上传到任何服务器
3. 解密后的数据建议本地存储，谨慎分享
4. 遵守相关法律法规和平台用户协议
5. 生成的人设 Skill 仅用于个人 AI 助手，不得用于欺骗或冒充

---

*Skill 版本: 1.0*
*最后更新: 2026-06-19*
