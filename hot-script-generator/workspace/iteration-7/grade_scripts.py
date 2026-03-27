#!/usr/bin/env python3
"""Grade the script outputs - Iteration 7."""

import json
import os
import re

def grade_script(script_content, eval_metadata):
    """Grade a script based on assertions."""
    results = []

    for assertion in eval_metadata["assertions"]:
        name = assertion["name"]
        passed = False
        evidence = ""

        if name == "包含批量热点分析报告":
            if "批量热点分析报告" in script_content:
                passed = True
                evidence = "包含批量热点分析报告"
            else:
                evidence = "缺少批量热点分析报告"

        elif name == "包含热点质量评估":
            if "质量评估" in script_content or "热点质量" in script_content or "评级" in script_content:
                passed = True
                evidence = "包含热点质量评估"
            else:
                evidence = "缺少热点质量评估"

        elif name == "包含季节适配检测":
            if "季节适配" in script_content or "季节匹配" in script_content:
                passed = True
                evidence = "包含季节适配检测"
            else:
                evidence = "缺少季节适配检测"

        elif name == "包含多样化维度标注":
            checks = ["开场钩子", "叙事结构", "视觉风格", "情绪基调"]
            found = sum(1 for c in checks if c in script_content)
            if found >= 2:
                passed = True
                evidence = f"包含多样化维度标注（{found}/4项）"
            else:
                evidence = f"多样化维度标注不完整（{found}/4项）"

        elif name == "包含BGM建议":
            checks = ["BGM", "音乐风格", "情绪匹配", "节奏"]
            found = sum(1 for c in checks if c in script_content)
            if found >= 2:
                passed = True
                evidence = f"包含BGM建议（{found}/4项）"
            else:
                evidence = f"BGM建议不完整（{found}/4项）"

        elif name == "包含标题建议":
            if "标题建议" in script_content or "标题" in script_content:
                # Check for multiple titles (1. 2. 3. pattern or similar)
                title_patterns = re.findall(r'标题.*?[""「」]', script_content)
                if len(title_patterns) >= 1 or "标题建议" in script_content:
                    passed = True
                    evidence = "包含标题建议"
                else:
                    evidence = "标题建议不完整"
            else:
                evidence = "缺少标题建议"

        elif name == "包含话题标签推荐":
            if "话题标签" in script_content or "#" in script_content:
                passed = True
                evidence = "包含话题标签推荐"
            else:
                evidence = "缺少话题标签推荐"

        elif name == "包含脚本自检报告":
            if "自检报告" in script_content or ("钩子强度" in script_content and "情绪弧线" in script_content):
                passed = True
                evidence = "包含脚本自检报告"
            else:
                evidence = "缺少脚本自检报告"

        elif name == "自检报告有总分":
            # Check for score pattern like "总分" or "分/100" or star ratings
            if re.search(r'总分[：:]\s*\d+', script_content) or re.search(r'\d+/100', script_content) or re.search(r'⭐{3,5}', script_content):
                passed = True
                evidence = "自检报告包含总分和等级"
            else:
                evidence = "自检报告缺少总分"

        elif name == "无服装特写镜头":
            forbidden_patterns = [
                r'画面特写.*卫衣', r'特写.*质感', r'细节图', r'面料特写',
                r'袖口.*特写', r'落肩设计.*特写'
            ]
            found_forbidden = []
            for pattern in forbidden_patterns:
                if re.search(pattern, script_content):
                    found_forbidden.append(pattern)
            if not found_forbidden:
                passed = True
                evidence = "脚本无服装特写镜头"
            else:
                evidence = f"发现服装特写"

        elif name == "无价格和购买信息":
            price_pattern = r'¥\d+|价格|下单|购买链接|产品信息|优惠'
            if not re.search(price_pattern, script_content):
                passed = True
                evidence = "脚本不包含价格和购买信息"
            else:
                evidence = "脚本包含价格或购买信息"

        elif name == "叙事为主":
            if "故事线" in script_content or "故事" in script_content:
                passed = True
                evidence = "脚本以叙事为主"
            else:
                evidence = "脚本叙事性不足"

        results.append({
            "text": name,
            "passed": passed,
            "evidence": evidence
        })

    return results

def main():
    base_path = "/Users/Abner/.claude/skills/hot-script-generator/workspace/iteration-7/batch-hotspots"
    configs = ["with_skill", "without_skill"]

    with open(f"{base_path}/eval_metadata.json", "r") as f:
        eval_metadata = json.load(f)

    for config in configs:
        script_path = f"{base_path}/{config}/outputs/script.md"
        if os.path.exists(script_path):
            with open(script_path, "r") as f:
                script_content = f.read()

            results = grade_script(script_content, eval_metadata)

            grading = {
                "eval_id": 1,
                "eval_name": "batch-hotspots",
                "config": config,
                "expectations": results
            }

            output_path = f"{base_path}/{config}/grading.json"
            with open(output_path, "w") as f:
                json.dump(grading, f, ensure_ascii=False, indent=2)

            print(f"Graded {config}: {sum(1 for r in results if r['passed'])}/{len(results)} passed")

if __name__ == "__main__":
    main()