# Zola

> **Personal AI Skills * Persona Distillation * Agent Configurations**

[![GitHub](https://img.shields.io/badge/GitHub-Zola--ops%2FZola-181717?style=flat\&logo=github)](https://github.com/Zola-ops/Zola)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)

---

## Overview

This repository is a collection of **personal AI tools and configurations** built around persona distillation - extracting your unique language patterns from chat history and turning them into AI agent skills that truly sound like *you*.

What is inside:

| Category | Description |
|----------|-------------|
| **Persona Distiller** | End-to-end toolkit to extract language features from WeChat/QQ chats and generate AI persona skills |
| **Zola Skill** | A fully distilled AI persona (ENFJ, AI PM from Yunnan) with detailed behavioral guidelines |
| **Agent Configs** | Structured prompts, writing templates, and task-specific configurations |

---

## Persona Distiller

The core tool - a complete pipeline that transforms raw chat logs into an AI persona skill.

```
Raw Chat Data -> Decrypt -> Export CSV -> Analyze -> Generate Persona MD
```

### Three-Stage Pipeline

| Stage | Input | Output | Time |
|-------|-------|--------|------|
| **Stage 1: Data Extraction** | Encrypted databases | `all_messages.csv` | 5-30 min |
| **Stage 2: Language Analysis** | `all_messages.csv` | `speech_report.txt` | 1-5 min |
| **Stage 3: Persona Distillation** | `speech_report.txt` | `persona_skill.md` | < 1 min |

### Analysis Dimensions (8 Axes)

| Dimension | What It Measures |
|-----------|-----------------|
| Catchphrase frequency | Top 60 filler/emotion words |
| Sentence-ending patterns | Top 30 ending characters |
| Short phrases (1-12 chars) | Top 80 high-frequency replies |
| Mid-length sentences (13-50 chars) | Top 50 typical sentence structures |
| Punctuation habits | Top 20 punctuation preferences |
| Text length distribution | Short vs. medium vs. long messages |
| Chinese-English mixing ratio | Bilingual communication patterns |
| Scene keyword coverage | Tech / daily / study / emotion / gaming |

### Quick Start (Already Have CSV?)

```bash
python persona-distiller/scripts/analyze_speech.py --input all_messages.csv --output speech_report.txt
python persona-distiller/scripts/distill_persona.py --report speech_report.txt --output persona_skill.md
```

### Scripts Overview

| Script | Function | Stage |
|--------|----------|-------|
| `scan_chat_data.py` | Auto-scan local WeChat/QQ data | 1 |
| `hook_qq_key.py` | Frida hook to capture QQ encryption key | 1 |
| `decrypt_qq_with_key.py` | SQLCipher decryption for QQ databases | 1 |
| `export_wechat.py` | WeChat message export (WCDB parsing) | 1 |
| `export_qq.py` | QQ message export (MSG format parsing) | 1 |
| `merge_export.py` | Merge into unified CSV format | 1 |
| `analyze_speech.py` | Language feature analysis | 2 |
| `distill_persona.py` | Generate persona MD from analysis | 3 |

> Full documentation: [persona-distiller/README.md](./persona-distiller/README.md) | [QUICKSTART.md](./persona-distiller/QUICKSTART.md)

---

## Zola Skill

A fully distilled persona demonstrating what the distillation pipeline produces.

### Who is Zola?

| | |
|---|---|
| **Name** | Zola (朱江笛) |
| **Ethnicity** | Hani (哈尼族) |
| **Origin** | Mengzi, Yunnan |
| **MBTI** | ENFJ |
| **Role** | AI Product Manager |
| **Education** | Zhongnan University of Economics and Law, English Major |

### Core Language Style

- **69% of messages are ≤ 5 characters** - ultra-concise
- **"笑死"** is the #1 emotion word (4,422 occurrences)
- **"素"** = "是" (signature pronunciation quirk)
- Heavy **Chinese-English mixing** in professional contexts (SOP, PM, RAG, agent, pipeline)
- **Punctuation-optional** style - "。。" replaces "...", "()" for parenthetical remarks

### Scenario-Specific Adaptations

| Scenario | Strategy |
|----------|----------|
| **Casual chat** | Think like sending a WeChat message, not writing an essay. Emotion over logic. |
| **Formal writing** | Structured, data-driven, bilingual (CN/EN). Policy language when needed. |
| **Work reports** | Data speaks. Fast iteration rhythm. SOP/framework thinking. |
| **Speeches** | Story-first opening, authoritative quotes, "How might we" endings. |
| **Career coaching** | STAR method for resumes. Cross-domain narrative. Information gap reduction. |
| **Business plans** | Research-first. Competitive analysis. ROI-aware. Funding logic clear. |

### What Zola Wont Do

- Use "呢" or "~" or literary/poetic language
- Stack "首先/其次/最后" (AI-flavored patterns)
- End with "你觉得呢？" (reverse questions)
- Write excessively long messages in casual contexts

> Full persona spec: [Zola.md](./Zola.md)

---

## Installation

```bash
# Clone the repository
git clone https://github.com/Zola-ops/Zola.git
cd Zola

# Install dependencies for Persona Distiller
pip install pywxdump frida psutil
```

### Prerequisites

- **Python 3.8+**
- **WeChat** or **QQ** installed on the target machine (for data extraction)
- **Frida** (for QQ key capture - install via `pip install frida`)
- **pywxdump** (for WeChat decryption - install via `pip install pywxdump`)

---

## Repository Structure

```
Zola/
├── README.md                          # This file
├── Zola.md                            # Full persona skill definition
├── LICENSE                            # MIT License
│
├── persona-distiller/                 # Chat distillation toolkit
│   ├── README.md                      # Detailed documentation
│   ├── QUICKSTART.md                  # Quick start guide
│   ├── SKILL.md                       # Skill template
│   ├── .gitignore                     # Excludes sensitive files
│   └── scripts/
│       ├── scan_chat_data.py          # Auto-scan local chat data
│       ├── hook_qq_key.py            # QQ key capture via Frida
│       ├── decrypt_qq_with_key.py    # QQ database decryption
│       ├── export_wechat.py          # WeChat export
│       ├── export_qq.py              # QQ export
│       ├── merge_export.py           # CSV merger
│       ├── analyze_speech.py         # Language analysis
│       └── distill_persona.py        # Persona generation
│
└── [future skills and configs...]
```

---

## Usage Scenarios

### Scenario 1: First Time (Full Pipeline)

```bash
# Step 1: Scan for chat data
python persona-distiller/scripts/scan_chat_data.py

# Step 2: Decrypt databases (WeChat example)
pywxdump bias_addr
pywxdump db_decrypt

# Step 3: Export to CSV
python persona-distiller/scripts/export_wechat.py --input decrypted/ --output wechat.csv

# Step 4: Merge
python persona-distiller/scripts/merge_export.py --wechat wechat.csv --qq qq.csv --output all_messages.csv

# Step 5: Analyze language features
python persona-distiller/scripts/analyze_speech.py --input all_messages.csv --output speech_report.txt

# Step 6: Generate persona skill
python persona-distiller/scripts/distill_persona.py --report speech_report.txt --output persona_skill.md
```

### Scenario 2: New Machine (Have CSV from Old Machine)

```bash
python persona-distiller/scripts/analyze_speech.py --input all_messages.csv --output speech_report.txt
python persona-distiller/scripts/distill_persona.py --report speech_report.txt --output persona_skill.md
```

### Scenario 3: Sharing with Friends

Friends run the full pipeline on **their own machine** using their own chat data. Share:
- `scripts/` directory
- Documentation files (`SKILL.md`, `QUICKSTART.md`)

> **Cannot share**: encrypted databases, decryption keys, or decrypted databases (machine-bound).

---

## Security and Privacy

| Principle | Details |
|-----------|---------|
| **Local-only processing** | All decryption and analysis happens locally - no network transmission |
| **Key safety** | Decryption keys are machine-specific. Add key files to `.gitignore` |
| **Data sharing** | Review CSV/persona MD for sensitive content before sharing |
| **Compliance** | Extract only **your own** chat history. Use persona skills for personal AI assistants only |
| **No impersonation** | Generated personas must not be used for deception or fraud |

---

## Output Files

| File | Description | Example Size |
|------|-------------|-------------|
| `wechat.csv` | WeChat messages | 31.6 MB (500K msgs) |
| `qq.csv` | QQ messages | 242 MB (4M msgs) |
| `all_messages.csv` | Merged messages | 312 MB (4.5M msgs) |
| `speech_report.txt` | Language analysis report | 10-50 KB |
| `persona_skill.md` | Generated persona skill | 5-20 KB |

### CSV Format

```csv
时间,平台,发送者,是否我的发言,消息类型,内容
2024-01-15 14:30:25,微信,张三,是,text,哈哈哈哈好啊
2024-01-15 14:30:30,微信,李四,否,text,你在干嘛
```

---

## FAQ

**Q: Can I use this on a different machine?**
A: Yes - but Stage 1 (data extraction) must be re-run on the new machine since encryption keys are machine-specific. CSV files are portable.

**Q: What if I already have decrypted databases?**
A: Skip to the export step and run from there.

**Q: How much chat history do I need?**
A: 10,000+ messages recommended for reliable analysis. More data = better persona.

**Q: Does this work with newer versions of WeChat/QQ?**
A: Depends on version changes. `pywxdump` and Frida hooks may need updates. Check the respective tool documentation.

---

## Contributing

Contributions are welcome! Areas where help is needed:

- **Platform support**: macOS/Linux data extraction scripts
- **New chat platforms**: Telegram, WhatsApp, iMessage parsers
- **Analysis dimensions**: Additional linguistic feature extractors
- **Documentation**: Translations, tutorials, video guides

```bash
# Fork -> Branch -> Commit -> Pull Request
git checkout -b feature/your-feature
git commit -m "Add your feature"
git push origin feature/your-feature
```

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Contact

- **Author**: 朱江笛 (Zola)
- **GitHub**: [@Zola-ops](https://github.com/Zola-ops)
- **Repository**: [Zola-ops/Zola](https://github.com/Zola-ops/Zola)

---

<p align="center">
  <i>Built with care for AI that sounds like you, not like a bot.</i>
</p>
