# -*- coding: utf-8 -*-
"""
人设蒸馏脚本 - 从语言特征分析报告蒸馏成人设 MD

用法:
    python distill_persona.py --report speech_report.txt --output persona.md
    python distill_persona.py --report speech_report.txt --docs ./docs/ --output persona.md
"""
import os
import io
import sys
import re
import argparse
import collections

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def parse_args():
    parser = argparse.ArgumentParser(description='从语言特征分析报告蒸馏成人设 MD')
    parser.add_argument('--report', '-r', required=True, help='语言特征分析报告文件')
    parser.add_argument('--docs', '-d', help='项目文档目录（可选，用于补充人设知识）')
    parser.add_argument('--output', '-o', required=True, help='输出人设 MD 文件')
    parser.add_argument('--name', '-n', help='人名（用于 MD 标题）')
    return parser.parse_args()


def parse_report(report_file):
    """解析语言特征分析报告，提取关键特征"""
    with open(report_file, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    features = {
        'total_texts': 0,
        'avg_len': 0,
        'english_ratio': 0,
        'emoji_ratio': 0,
        'len_dist': {},
        'particles': [],
        'endings': [],
        'short_phrases': [],
        'medium_phrases': [],
        'punctuation': [],
        'scenarios': {},
        'samples': []
    }
    
    # 解析基础统计
    m = re.search(r'总文本数:\s*(\d+)', content)
    if m:
        features['total_texts'] = int(m.group(1))
    
    m = re.search(r'平均长度:\s*([\d.]+)', content)
    if m:
        features['avg_len'] = float(m.group(1))
    
    m = re.search(r'含英文.*?:\s*\d+\s*\((\d+)%\)', content)
    if m:
        features['english_ratio'] = int(m.group(1))
    
    m = re.search(r'含emoji.*?:\s*\d+\s*\((\d+)%\)', content)
    if m:
        features['emoji_ratio'] = int(m.group(1))
    
    # 解析长度分布
    len_dist_match = re.search(r'=== 长度分布 ===(.*?)===', content, re.DOTALL)
    if len_dist_match:
        for line in len_dist_match.group(1).strip().split('\n'):
            m = re.match(r'\s*(\d+-\d+字|\d+字\+):\s*(\d+)\s*\((\d+)%\)', line.strip())
            if m:
                features['len_dist'][m.group(1)] = {'count': int(m.group(2)), 'pct': int(m.group(3))}
    
    # 解析语气词
    particles_match = re.search(r'=== 语气词/口语表达频率 TOP 60 ===(.*?)===', content, re.DOTALL)
    if particles_match:
        for line in particles_match.group(1).strip().split('\n'):
            m = re.match(r'\s*\'(.+?)\':\s*(\d+)\s*\((\d+)%\)', line.strip())
            if m:
                features['particles'].append({
                    'word': m.group(1),
                    'count': int(m.group(2)),
                    'pct': int(m.group(3))
                })
    
    # 解析句尾字
    endings_match = re.search(r'=== 句尾字频率 TOP 30 ===(.*?)===', content, re.DOTALL)
    if endings_match:
        for line in endings_match.group(1).strip().split('\n'):
            m = re.match(r'\s*\'(.+?)\':\s*(\d+)', line.strip())
            if m:
                features['endings'].append({
                    'char': m.group(1),
                    'count': int(m.group(2))
                })
    
    # 解析高频短句
    short_match = re.search(r'=== 高频短句.*?TOP 80 ===(.*?)===', content, re.DOTALL)
    if short_match:
        for line in short_match.group(1).strip().split('\n'):
            m = re.match(r'\s*\'(.+?)\':\s*(\d+)', line.strip())
            if m:
                features['short_phrases'].append({
                    'phrase': m.group(1),
                    'count': int(m.group(2))
                })
    
    # 解析标点符号
    punct_match = re.search(r'=== 标点符号 TOP 20 ===(.*?)===', content, re.DOTALL)
    if punct_match:
        for line in punct_match.group(1).strip().split('\n'):
            m = re.match(r'\s*\'(.+?)\':\s*(\d+)', line.strip())
            if m:
                features['punctuation'].append({
                    'char': m.group(1),
                    'count': int(m.group(2))
                })
    
    # 解析场景分布
    scenarios_match = re.search(r'=== 场景关键词覆盖率 ===(.*?)===', content, re.DOTALL)
    if scenarios_match:
        for line in scenarios_match.group(1).strip().split('\n'):
            m = re.match(r'\s*(.+?):\s*(\d+)\s*\((\d+)%\)', line.strip())
            if m:
                features['scenarios'][m.group(1)] = {
                    'count': int(m.group(2)),
                    'pct': int(m.group(3))
                })
    
    return features


def extract_top_particles(features, top_n=20):
    """提取高频口头禅"""
    particles = features['particles']
    # 过滤掉常见虚词（的、了、是、我等）
    stop_words = ['的', '了', '是', '我', '你', '他', '她', '它', '这', '那', '都', '也', '就', '还', '会', '能', '可以', '不', '没', '有', '在', '和', '与', '或', '但', '而', '如果', '因为', '所以']
    
    filtered = [p for p in particles if p['word'] not in stop_words and len(p['word']) > 1]
    return filtered[:top_n]


def extract_style_rules(features):
    """从特征中提取风格规则"""
    rules = []
    
    # 基于文本长度分布
    if features['len_dist']:
        short_pct = features['len_dist'].get('1-5字', {}).get('pct', 0)
        if short_pct > 50:
            rules.append(f"极简风格（{short_pct}% 发言 <= 5字）")
    
    # 基于标点
    punct = {p['char']: p['count'] for p in features['punctuation']}
    if '。' not in punct or punct.get('。', 0) < punct.get('！', 0):
        rules.append("标点随意，少用句号")
    
    # 基于英文比例
    if features['english_ratio'] > 10:
        rules.append(f"中英混用（{features['english_ratio']}% 含英文）")
    
    # 基于 Emoji 比例
    if features['emoji_ratio'] > 5:
        rules.append(f"常用 Emoji（{features['emoji_ratio']}% 含 Emoji）")
    
    return rules


def generate_persona_md(features, args):
    """生成人物设定 MD"""
    name = args.name or 'Persona'
    
    lines = []
    lines.append(f"# {name} Skill")
    lines.append("")
    lines.append("> 基于聊天记录语言特征分析生成的人设 Skill")
    lines.append(">")
    lines.append(f"> 数据来源: {args.report}")
    lines.append(f"> 分析样本: {features['total_texts']} 条文本")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # 语言风格特征
    lines.append("## 语言风格特征")
    lines.append("")
    
    # 高频口头禅
    lines.append("### 高频口头禅")
    lines.append("")
    top_particles = extract_top_particles(features, top_n=20)
    for p in top_particles[:10]:
        lines.append(f"- **{p['word']}**: 出现 {p['count']} 次 ({p['pct']}%)")
    lines.append("")
    
    # 句尾偏好
    lines.append("### 句尾偏好")
    lines.append("")
    endings = features['endings'][:10]
    ending_chars = [e['char'] for e in endings]
    lines.append(f"- 高频句尾字: {', '.join(ending_chars[:5])}")
    lines.append("")
    
    # 典型句式
    lines.append("### 典型句式")
    lines.append("")
    short_phrases = features['short_phrases'][:20]
    for phrase in short_phrases[:5]:
        lines.append(f"- \"{phrase['phrase']}\" (出现 {phrase['count']} 次)")
    lines.append("")
    
    # 标点习惯
    lines.append("### 标点习惯")
    lines.append("")
    punct = features['punctuation'][:10]
    for p in punct[:5]:
        lines.append(f"- **{p['char']}**: {p['count']} 次")
    lines.append("")
    
    # 文本长度分布
    lines.append("### 文本长度分布")
    lines.append("")
    if features['len_dist']:
        for k, v in features['len_dist'].items():
            lines.append(f"- **{k}**: {v['count']} 条 ({v['pct']}%)")
    lines.append(f"- **平均长度**: {features['avg_len']:.1f} 字")
    lines.append("")
    
    # 中英混用
    lines.append("### 语言混合度")
    lines.append("")
    lines.append(f"- **英文比例**: {features['english_ratio']}%")
    lines.append(f"- **Emoji 比例**: {features['emoji_ratio']}%")
    lines.append("")
    
    lines.append("---")
    lines.append("")
    
    # 人设知识图谱（需要用户补充）
    lines.append("## 人设知识图谱")
    lines.append("")
    lines.append("> ⚠️ 以下信息需要用户补充或确认")
    lines.append("")
    lines.append("### 基本信息")
    lines.append("- **姓名**: ")
    lines.append("- **民族**: ")
    lines.append("- **星座**: ")
    lines.append("- **MBTI**: ")
    lines.append("")
    lines.append("### 职业路径")
    lines.append("- ")
    lines.append("")
    lines.append("### 教育背景")
    lines.append("- ")
    lines.append("")
    lines.append("### 城市记忆")
    lines.append("- ")
    lines.append("")
    lines.append("### 兴趣偏好")
    lines.append("- ")
    lines.append("")
    
    lines.append("---")
    lines.append("")
    
    # 模拟指南
    lines.append("## 模拟指南")
    lines.append("")
    
    # 自动生成风格规则
    style_rules = extract_style_rules(features)
    lines.append("### 聊天风格")
    lines.append("")
    for i, rule in enumerate(style_rules, 1):
        lines.append(f"{i}. {rule}")
    lines.append("")
    lines.append("### 正式写作风格")
    lines.append("")
    lines.append("1. ")
    lines.append("")
    lines.append("### 禁忌")
    lines.append("")
    lines.append("- 不用")
    lines.append("- 不用")
    lines.append("")
    
    lines.append("---")
    lines.append("")
    lines.append(f"*生成时间: {args.report}*")
    lines.append(f"*样本量: {features['total_texts']} 条*")
    
    return "\n".join(lines)


def main():
    args = parse_args()
    
    # 解析报告
    print(f"解析报告: {args.report}")
    features = parse_report(args.report)
    
    print(f"提取到特征:")
    print(f"  - 总文本数: {features['total_texts']}")
    print(f"  - 高频口头禅: {len(features['particles'])}")
    print(f"  - 句尾字: {len(features['endings'])}")
    print(f"  - 高频短句: {len(features['short_phrases'])}")
    
    # 生成人设 MD
    md_content = generate_persona_md(features, args)
    
    # 保存
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"\n人设 MD 已保存: {args.output}")
    print("\n⚠️ 请手动补充以下部分:")
    print("  1. 人设知识图谱（基本信息、职业路径、教育背景等）")
    print("  2. 模拟指南（聊天风格、正式写作风格、禁忌）")
    print("  3. 根据随机长句样本调整典型句式")


if __name__ == '__main__':
    main()
