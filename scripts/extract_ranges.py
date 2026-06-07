#!/usr/bin/env python3
"""
extract_ranges.py — 根据 TOC 映射表，定向提取招标文件 PDF 的关键章节内容
用法:
  # 先提取目录
  python parse_toc.py tender.pdf --json > /tmp/toc.json
  # 再定向提取关键章节
  python extract_ranges.py tender.pdf /tmp/toc.json --output /tmp/extracted.md

功能：
- 根据 page_ranges 提取指定章节内容
- 支持指定白名单章节名（只提取关键章节）
- 支持黑名单关键词（跳过设备参数表、格式模板页）
- 输出结构化 Markdown
"""

import argparse, json, re, sys
import pdfplumber

# 章节名关键词：包含这些关键词的章节一定会提取
KEY_CHAPTER_KEYWORDS = [
    '投标邀请', '投标须知', '资格审查', '评标方法', '评标标准',
    '采购需求', '技术要求', '商务要求', '合同', '投标文件组成',
    '投标文件格式', '资格证明', '开标一览表', '分项报价',
]

# 章节名关键词：包含这些关键词的章节跳过（纯设备清单/参数表）
SKIP_CHAPTER_KEYWORDS = [
    '服务器（数据中心',
    '服务器（数据中心B',
    '基础软件',
    '支撑软件',
    '安全设备',
    '安全软件',
    '密码产品',
    '终端系统',
    '网络系统',
    '容灾系统',
    '数据中心网络',
    '核心骨干网',
    '系统集成',
    '信息系统迁移',
    '建设期租赁',
    '安全生产',
    '采购清单一览表',
    '详细技术参数',
]

# 每页最大字符数，防止单页过长
MAX_CHARS_PER_PAGE = 6000

def load_toc(toc_path):
    with open(toc_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('page_ranges', {}), data.get('total_pages', 0)

def is_skip_chapter(name):
    return any(kw in name for kw in SKIP_CHAPTER_KEYWORDS)

def is_key_chapter(name):
    return any(kw in name for kw in KEY_CHAPTER_KEYWORDS)

def extract_pages(pdf_path, page_range):
    """提取指定页码范围的内容"""
    start, end = page_range['start'], page_range['end']
    pages_content = []
    with pdfplumber.open(pdf_path) as pdf:
        for i in range(start - 1, min(end, len(pdf.pages))):
            page = pdf.pages[i]
            text = (page.extract_text() or '').strip()
            if text:
                # 截断过长的页面
                if len(text) > MAX_CHARS_PER_PAGE:
                    text = text[:MAX_CHARS_PER_PAGE] + '\n[... 内容过长已截断 ...]'
                pages_content.append(f"\n--- Page {i+1} ---\n{text}")
    return '\n'.join(pages_content)

def extract_key_chapters(pdf_path, toc_path, output_path=None, min_chars=200):
    """提取关键章节内容，跳过纯参数表"""
    page_ranges, total_pages = load_toc(toc_path)
    output_parts = []
    skipped = []

    output_parts.append(f"# 定向解析结果\n")
    output_parts.append(f"> 总页数: {total_pages}")
    output_parts.append(f"> 目录条目: {len(page_ranges)}")
    output_parts.append(f"> 提取章节数: 0（计算中）\n---\n")

    extracted_count = 0
    for name, rng in sorted(page_ranges.items(), key=lambda x: x[1]['start']):
        page_count = rng['end'] - rng['start'] + 1

        # 判断是否跳过
        if is_skip_chapter(name):
            skipped.append(f"[SKIP] {name} (pages {rng['start']}-{rng['end']}, {page_count}p)")

        # 只有以下情况才提取：
        # 1. 章节名包含关键章节关键词
        # 2. 或用户未指定白名单（全部提取）
        # 3. 且不是跳过章节
        if is_key_chapter(name) and not is_skip_chapter(name):
            # 对于超长章节（如采购需求），只提取前N页
            if page_count > 100:
                # 采购需求章节：提取起始页开始的80页
                rng = {"start": rng['start'], "end": rng['start'] + 79}
                name = f"{name}（前80页，共{page_count}页）"

            content = extract_pages(pdf_path, rng)
            if len(content) >= min_chars:
                output_parts.append(f"\n## {name}\n")
                output_parts.append(f"> 页码范围: {rng['start']}-{rng['end']}")
                output_parts.append(content)
                extracted_count += 1
            else:
                skipped.append(f"[SKIP-EMPTY] {name} (pages {rng['start']}-{rng['end']}, 内容过短)")

    # 写入提取摘要
    summary = f"\n---\n\n## 提取摘要\n\n"
    summary += f"- 提取章节: {extracted_count} 个\n"
    summary += f"- 跳过章节: {len(skipped)} 个\n"
    if skipped:
        summary += f"\n### 跳过的章节\n\n"
        for s in skipped:
            summary += f"- {s}\n"

    # 替换占位符
    full_output = '\n'.join(output_parts)
    full_output = full_output.replace(
        "提取章节数: 0（计算中）",
        f"提取章节数: {extracted_count}"
    ) + summary

    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_output)
        print(f"[OK] Extracted {extracted_count} chapters to {output_path}")
    else:
        print(full_output)

    return extracted_count, skipped

def main():
    parser = argparse.ArgumentParser(description="Extract key chapters from tender PDF using TOC")
    parser.add_argument("pdf_path", help="Path to PDF file")
    parser.add_argument("toc_json", help="Path to TOC JSON (from parse_toc.py)")
    parser.add_argument("--output", "-o", help="Output Markdown file path")
    parser.add_argument("--all", action="store_true", help="Extract all chapters (no filtering)")
    parser.add_argument("--min-chars", type=int, default=200, help="Min chars per chapter (default: 200)")
    args = parser.parse_args()

    if args.all:
        # 全量提取模式
        page_ranges, total_pages = load_toc(args.toc_json)
        output_parts = [f"# 全量解析结果\n> PDF: {args.pdf_path}\n> 总页数: {total_pages}\n"]
        with pdfplumber.open(args.pdf_path) as pdf:
            for name, rng in sorted(page_ranges.items(), key=lambda x: x[1]['start']):
                content = extract_pages(args.pdf_path, rng)
                output_parts.append(f"\n## {name}\n> Pages {rng['start']}-{rng['end']}\n{content}")
        result = '\n'.join(output_parts)
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"[OK] Full extraction saved to {args.output}")
        else:
            print(result)
    else:
        extract_key_chapters(args.pdf_path, args.toc_json, args.output, args.min_chars)

if __name__ == "__main__":
    main()
