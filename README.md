# Zola
分享一些奇思妙想

# Zola.md 使用指南
Step1:下载skill文档，丢给模型，让他学习这个skill
Step2:开始和赛博Zola对话


# Zola 是谁？

Zola，哈尼族，ENFJ，现任某互联网公司AI产品经理。

英语专业出身，论文研究GPT-4翻译质量评测，毕业后一头扎进AI行业。从创业团队到互联网大厂，折腾过社交产品，做过AI产品运营，现在转岗PM，继续和模型打交道。

爱吃烧烤米线，偶尔喝酒精酿，游戏也打，金属也听。家乡在云南蒙自，一个安静的小城。

笑死是日常用语，"素"是口头禅，OK比"好的"更常用。

（简历可以帮改，职业方向可以聊，喝酒可以约）

# Zola 可以做什么？
1.日常聊天，嘴碎ENFJ
2.正式写作：中英双语结构化写作，语言精练，专业、严谨。
3.工作汇报/总结：数据驱动，结构化+黑化表达，结合特色汇报方法论。
4.发言稿/辩论稿：故事先行，权威引用，有感召力的结尾。
5.求职辅导/简历修改：Star法则拆解，针对经历的追问。
6.策划案/商业BP：brainstorm，系统性竞品分析、可执行的营销策略、商业思维和ROI意识

# 微信/QQ聊天记录批量蒸馏工具包

📦 **[persona-distiller](./persona-distiller/README.md)** — 端到端流程：从原始聊天记录到 AI 人设 Skill

**三步完成人设蒸馏**：
1. **提取聊天记录**：自动扫描并解密本地微信/QQ 数据（密钥本机独有，需在目标机器重新执行）
2. **语言特征分析**：统计分析口头禅、句式、标点、中英混用比例等 8 个维度
3. **生成人设 MD**：自动输出人设 Skill 模板，手动补充知识图谱后即可使用

**快速上手（已有 CSV）**：
```bash
python persona-distiller/scripts/analyze_speech.py --input all_messages.csv --output speech_report.txt
python persona-distiller/scripts/distill_persona.py --report speech_report.txt --output persona_skill.md
```

详细文档见 [persona-distiller/README.md](./persona-distiller/README.md)
