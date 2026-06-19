# -*- coding: utf-8 -*-
"""
语言特征分析工具 - 从聊天记录提取个人语言风格

用法:
    python analyze_speech.py --input messages.csv --output report.txt
    python analyze_speech.py --input messages.csv --is-self-col 4 --content-col 6
"""
import os
import io
import sys
import re
import csv
import collections
import random
import argparse

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def parse_args():
    parser = argparse.ArgumentParser(description='分析个人聊天记录语言特征')
    parser.add_argument('--input', '-i', required=True, help='输入文件 (CSV或TXT)')
    parser.add_argument('--output', '-o', help='输出报告文件 (默认输出到控制台)')
    parser.add_argument('--is-self-col', type=int, default=4, help='"是否我的发言"列索引 (从1开始, CSV默认第4列)')
    parser.add_argument('--content-col', type=int, default=6, help='"消息内容"列索引 (从1开始, CSV默认第6列)')
    parser.add_argument('--platform-col', type=int, default=2, help='"平台"列索引 (CSV默认第2列)')
    parser.add_argument('--type-col', type=int, default=5, help='"消息类型"列索引 (CSV默认第5列)')
    parser.add_argument('--sample', type=int, default=30, help='随机长句样本数量 (默认30)')
    parser.add_argument('--min-length', type=int, default=2, help='最小文本长度过滤 (默认2字)')
    return parser.parse_args()


def extract_from_csv(filepath, is_self_col, content_col, platform_col, type_col, min_length):
    """从CSV提取"我的发言"文本"""
    self_texts = []
    
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.reader(f)
        header = next(reader, None)  # skip header
        
        for row in reader:
            if len(row) < max(is_self_col, content_col):
                continue
            
            is_self = row[is_self_col - 1].strip()
            content = row[content_col - 1].strip()
            
            if is_self in ['是', 'True', '1', 'yes', 'Y'] and content and len(content) >= min_length:
                self_texts.append(content)
    
    return self_texts


def extract_from_txt(filepath, min_length):
    """从TXT提取文本（简单按行提取）"""
    texts = []
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.strip()
            if line and len(line) >= min_length:
                texts.append(line)
    return texts


def analyze_particles(texts):
    """分析语气词/口语表达频率"""
    particles = [
        # 基础语气词
        '啊', '呀', '呢', '吧', '哦', '哈', '嘛', '噢', '嘿', '哎', '额', '嗯', '唔', '耶',
        # 笑声
        '哈哈', '呜呜', '啊啊', '哈哈哈', '哈哈哈哈', '嘿嘿', '嘻嘻', '呵呵',
        # 粗口/感叹
        '卧槽', '我去', '靠', '草', '牛逼', '牛批', 'nb', 'NB',
        # 确认/回应
        '真的', '确实', '真的假的', '不会吧', '好吧', '行吧', '算了',
        '懂了', '明白了', '了解了', '知道', '知道了',
        '可以的', '没问题', '好的', '好', '行', 'ok', 'OK', 'Ok',
        '谢谢', '感谢', '谢啦', '多谢', 'thanks', 'Thanks',
        '太好了', '太棒了', '太牛了', '牛啊', '强', '厉害',
        '等一下', '等会儿', '等等', '稍等',
        '怎么了', '咋了', '什么事', '干嘛',
        '嗯嗯', '好的好的', '对对', '是是',
        # 网络用语
        '笑死', '笑死我了', '笑发财', '绝了',
        '妈', '艹', '操', '日', 'sb', 'SB',
        'hhh', '233', '2333', '666', '999',
        '芜湖', '冲', '起飞', '寄', '寄了', '绷不住', '破防', '乐', '乐了',
        '确实', '确实的', '属实', '纯纯', '大无语', '无语',
        '不是', '不是吧', '无语子', '汗', '汗了',
        '懂我', '懂不懂', '你懂什么',
        # 新增口头禅
        '斯密马赛', '好家伙', '妈嘟', '嗷嗷', '太抽象了', '属于是',
        '素', '素素', '素滴',
    ]
    
    counter = collections.Counter()
    for p in particles:
        cnt = sum(1 for t in texts if p in t)
        if cnt > 0:
            counter[p] = cnt
    
    return counter


def analyze_endings(texts, min_len=2, max_len=60):
    """分析句尾字频率"""
    endings = collections.Counter()
    for t in texts:
        t = t.strip()
        if min_len <= len(t) <= max_len:
            endings[t[-1]] += 1
    return endings


def analyze_short_phrases(texts, min_len=1, max_len=12):
    """分析高频短句"""
    short = collections.Counter()
    for t in texts:
        t = t.strip()
        if min_len <= len(t) <= max_len:
            short[t] += 1
    return short


def analyze_medium_phrases(texts, min_len=13, max_len=50):
    """分析典型中长句"""
    medium = collections.Counter()
    for t in texts:
        t = t.strip()
        if min_len <= len(t) <= max_len:
            medium[t] += 1
    return medium


def analyze_punctuation(texts):
    """分析标点符号使用"""
    punct = collections.Counter()
    punct_chars = '？！。，、~～…··；：""''（）【】《》!?.,~;:\'"()[]{}^_@#¥%&*+—–-'
    for t in texts:
        for ch in t:
            if ch in punct_chars:
                punct[ch] += 1
    return punct


def analyze_stats(texts):
    """基础文本统计"""
    has_english = sum(1 for t in texts if re.search(r'[a-zA-Z]{2,}', t))
    has_emoji = sum(1 for t in texts if re.search(r'[\U0001f600-\U0001f64f\U0001f300-\U0001f5ff\U0001f680-\U0001f6ff\U0001f1e0-\U0001f1ff\U00002702-\U000027b0]', t))
    avg_len = sum(len(t) for t in texts) / len(texts) if texts else 0
    
    # 长度分布
    len_dist = collections.Counter()
    for t in texts:
        l = len(t)
        if l <= 5:
            len_dist['1-5字'] += 1
        elif l <= 15:
            len_dist['6-15字'] += 1
        elif l <= 30:
            len_dist['16-30字'] += 1
        elif l <= 50:
            len_dist['31-50字'] += 1
        else:
            len_dist['50字+'] += 1
    
    return {
        'total': len(texts),
        'avg_len': avg_len,
        'english_ratio': has_english / len(texts) if texts else 0,
        'emoji_ratio': has_emoji / len(texts) if texts else 0,
        'len_dist': len_dist
    }


def analyze_scenarios(texts):
    """分析场景关键词覆盖"""
    scenarios = {
        '技术/编程': ['代码', '程序', 'bug', 'api', '函数', '数据库', '服务器', 'python', 'java', 'js', 'css', 'html', 'git', 'linux', '前端', '后端', '框架', '开发', '编译', '部署', 'sql', '算法', '加密', '解密', 'hook', 'frida', '逆向', '抓包', 'prompt', 'ai', '模型', 'gpt', 'llm'],
        '日常闲聊': ['吃饭', '睡觉', '洗澡', '出门', '回来', '明天', '今天', '晚上', '早上', '下午', '中午', '周末', '外卖', '奶茶', '咖啡'],
        '学习/工作': ['考试', '作业', '论文', '课', '复习', '预习', '老师', '学校', '大学', '高中', '成绩', '绩点', '选课', '上班', '下班', '开会', '汇报', 'ppt', '文档'],
        '情感/吐槽': ['烦', '累', '难过', '开心', '无聊', '生气', '崩溃', '焦虑', 'emo', '抑郁', '压力', '无语', '离谱', '抽象'],
        '游戏': ['游戏', '段位', '排位', '匹配', '队友', '对面', '副本', 'boss', '王者', '原神', '联盟', 'lol', '吃鸡', '通宵'],
        '网络用语': ['绝了', '寄了', '蚌埠住', '绷不住', '笑死', '离谱', '逆天', '好家伙', '不会吧', '确实', '整活', '好活', '烂活'],
    }
    
    results = {}
    for scenario, keywords in scenarios.items():
        hit = sum(1 for t in texts if any(k in t.lower() for k in keywords))
        results[scenario] = hit
    
    return results


def get_random_samples(texts, min_len=50, max_len=300, count=30):
    """获取随机长句样本"""
    long_texts = [t for t in texts if min_len <= len(t) <= max_len]
    if len(long_texts) <= count:
        return long_texts
    random.seed(42)
    return random.sample(long_texts, count)


def generate_report(texts, args):
    """生成完整分析报告"""
    lines = []
    
    lines.append("=" * 60)
    lines.append("语言特征分析报告")
    lines.append("=" * 60)
    lines.append("")
    
    # 基础统计
    stats = analyze_stats(texts)
    lines.append("=== 基础文本统计 ===")
    lines.append(f"  总文本数: {stats['total']}")
    lines.append(f"  平均长度: {stats['avg_len']:.1f} 字")
    lines.append(f"  含英文(>=2字母): {int(stats['english_ratio'] * stats['total'])} ({int(stats['english_ratio'] * 100)}%)")
    lines.append(f"  含emoji: {int(stats['emoji_ratio'] * stats['total'])} ({int(stats['emoji_ratio'] * 100)}%)")
    lines.append("")
    lines.append("=== 长度分布 ===")
    for k, v in stats['len_dist'].most_common():
        pct = v * 100 // stats['total'] if stats['total'] else 0
        lines.append(f"  {k}: {v} ({pct}%)")
    lines.append("")
    
    # 语气词
    particles = analyze_particles(texts)
    lines.append("=== 语气词/口语表达频率 TOP 60 ===")
    for w, c in particles.most_common(60):
        pct = c * 100 // len(texts)
        lines.append(f"  {w!r}: {c} ({pct}%)")
    lines.append("")
    
    # 句尾字
    endings = analyze_endings(texts)
    lines.append("=== 句尾字频率 TOP 30 ===")
    for w, c in endings.most_common(30):
        lines.append(f"  {w!r}: {c}")
    lines.append("")
    
    # 高频短句
    short = analyze_short_phrases(texts)
    lines.append("=== 高频短句 (1-12字) TOP 80 ===")
    for w, c in short.most_common(80):
        lines.append(f"  {w!r}: {c}")
    lines.append("")
    
    # 典型中长句
    medium = analyze_medium_phrases(texts)
    lines.append("=== 典型中长句 (13-50字) TOP 50 ===")
    for w, c in medium.most_common(50):
        lines.append(f"  {w!r}: {c}")
    lines.append("")
    
    # 标点符号
    punct = analyze_punctuation(texts)
    lines.append("=== 标点符号 TOP 20 ===")
    for w, c in punct.most_common(20):
        lines.append(f"  {w!r}: {c}")
    lines.append("")
    
    # 场景分布
    scenarios = analyze_scenarios(texts)
    lines.append("=== 场景关键词覆盖率 ===")
    for scenario, hit in scenarios.items():
        pct = hit * 100 // len(texts) if texts else 0
        lines.append(f"  {scenario}: {hit} ({pct}%)")
    lines.append("")
    
    # 随机长句样本
    samples = get_random_samples(texts, count=args.sample)
    lines.append(f"=== 随机长句样本 (50-300字) × {len(samples)} ===")
    for t in samples:
        lines.append(f"  [{len(t)}字] {t}")
        lines.append("")
    
    return "\n".join(lines)


def main():
    args = parse_args()
    
    # 判断输入文件类型
    ext = os.path.splitext(args.input)[1].lower()
    
    if ext == '.csv':
        print(f"从 CSV 提取: {args.input}")
        texts = extract_from_csv(
            args.input, 
            args.is_self_col, 
            args.content_col,
            args.platform_col,
            args.type_col,
            args.min_length
        )
    else:
        print(f"从 TXT 提取: {args.input}")
        texts = extract_from_txt(args.input, args.min_length)
    
    if not texts:
        print("ERROR: 没有提取到文本，请检查输入文件格式")
        sys.exit(1)
    
    print(f"提取到 {len(texts)} 条文本")
    
    # 生成报告
    report = generate_report(texts, args)
    
    # 输出
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"报告已保存: {args.output}")
    else:
        print(report)


if __name__ == '__main__':
    main()
