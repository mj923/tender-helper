#!/usr/bin/env python3
"""
parse_toc.py — 提取招标文件 PDF 目录，建立章节→页码映射表
用法: python parse_toc.py <pdf_path> [--max-pages 15]
输出: JSON，包含章节名→起始页码的映射
"""

import argparse, json, re, sys
import pdfplumber

def extract_toc(pdf_path, max_pages=15):
    toc = {}
    current_part = None
    # 匹配模式1: "第X章 章节名 ........... 页码"（含中文省略号）
    pattern_full = re.compile(r'^第[一二三四五六七八九十百千0-9]+[章节]?\s+(.+?)[\s\.·]+(\d{1,4})\s*$')
    # 匹配模式2: "一、 章节名 ............ 页码"
    pattern_section = re.compile(r'^[（(]?[一二三四五六七八九十0-9]+[）)][\.\s]+(.+?)[\s\.·]+(\d{1,4})\s*$')
    # 匹配模式3: "X.X 章节名 ........... 页码"
    pattern_numeric = re.compile(r'^\d+\.\d*\s+(.+?)[\s\.·]+(\d{1,4})\s*$')
    # 匹配模式4: 第X章（无页码）
    pattern_chapter_no_page = re.compile(r'^第[一二三四五六七八九十百千0-9]+[章节]?\s+(.+?)$')

    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        for i in range(min(max_pages, total_pages)):
            page = pdf.pages[i]
            lines = (page.extract_text() or '').split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                # 跳过明显非目录行
                if len(line) < 4 or len(line) > 120:
                    continue
                # 排除标题/版权页内容
                skip_patterns = ['采购文件', '招标文件', '公开招标', '电子标', '服务类（']
                if any(sp in line for sp in skip_patterns):
                    continue

                matched = False
                # 模式1: 第X章 + 页码（最准确）
                m = pattern_full.match(line)
                if m:
                    name, page_str = m.group(1).strip(), m.group(2).strip()
                    page_num = int(page_str)
                    if len(name) >= 2 and page_num <= total_pages:
                        toc[name] = page_num
                        matched = True

                # 模式2: 一、二、 + 页码
                if not matched:
                    m = pattern_section.match(line)
                    if m:
                        name, page_str = m.group(1).strip(), m.group(2).strip()
                        page_num = int(page_str)
                        if len(name) >= 2 and page_num <= total_pages:
                            toc[name] = page_num
                            matched = True

                # 模式3: 数字编号 + 页码
                if not matched:
                    m = pattern_numeric.match(line)
                    if m:
                        name, page_str = m.group(1).strip(), m.group(2).strip()
                        page_num = int(page_str)
                        if len(name) >= 3 and page_num <= total_pages:
                            toc[name] = page_num
                            matched = True

                # 模式4: 第X章无页码（记录位置，用当前偏移页）
                if not matched:
                    m = pattern_chapter_no_page.match(line)
                    if m:
                        name = m.group(1).strip()
                        if len(name) >= 2:
                            # 使用当前页面作为近似页码
                            toc[name] = i + 1

    # 清理：去除页码重复的短名（保留长名）
    page_to_names = {}
    for name, page in toc.items():
        page_to_names.setdefault(page, []).append(name)
    cleaned = {}
    for page, names in page_to_names.items():
        # 保留最长的名称
        best = max(names, key=len)
        cleaned[best] = page

    return {
        "total_pages": total_pages,
        "toc": cleaned,
        "page_ranges": _compute_ranges(cleaned, total_pages)
    }

def _compute_ranges(toc, total_pages):
    """根据目录条目计算每个章节的起止页码范围"""
    sorted_items = sorted(toc.items(), key=lambda x: x[1])
    ranges = {}
    for i, (name, start_page) in enumerate(sorted_items):
        if i + 1 < len(sorted_items):
            end_page = sorted_items[i + 1][1] - 1
        else:
            end_page = total_pages
        ranges[name] = {"start": start_page, "end": end_page}
    return ranges

def main():
    parser = argparse.ArgumentParser(description="Extract TOC from tender PDF")
    parser.add_argument("pdf_path", help="Path to PDF file")
    parser.add_argument("--max-pages", type=int, default=15, help="Max pages to scan for TOC (default: 15)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    result = extract_toc(args.pdf_path, args.max_pages)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"PDF: {args.pdf_path}")
        print(f"Total pages: {result['total_pages']}")
        print(f"TOC entries found: {len(result['toc'])}")
        print("\n--- TOC ---")
        for name, page in sorted(result['toc'].items(), key=lambda x: x[1]):
            print(f"  Page {page:3d}: {name}")
        print("\n--- Page Ranges ---")
        for name, rng in result['page_ranges'].items():
            print(f"  {name}: pages {rng['start']}-{rng['end']}")

if __name__ == "__main__":
    main()
