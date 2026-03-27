#!/usr/bin/env python3
"""Grade the script outputs based on assertions - Iteration 3."""

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

        if name == "包含热榜分析部分":
            if "热榜分析" in script_content or "## 热榜分析" in script_content:
                passed = True
                evidence = "脚本包含热榜分析部分"
            else:
                evidence = "脚本缺少热榜分析部分"

        elif name == "包含情绪深度分析":
            checks = ["表层情绪", "深层情绪", "情绪矛盾", "情绪出口"]
            found = sum(1 for c in checks if c in script_content)
            if found >= 3:
                passed = True
                evidence = f"包含情绪深度分析（{found}/4项）"
            else:
                evidence = f"情绪深度分析不完整（{found}/4项）"

        elif name == "包含主题深度挖掘":
            checks = ["话题现象", "背后议题", "核心痛点", "价值主张"]
            found = sum(1 for c in checks if c in script_content)
            if found >= 3:
                passed = True
                evidence = f"包含主题深度挖掘（{found}/4项）"
            else:
                evidence = f"主题深度挖掘不完整（{found}/4项）"

        elif name == "包含推演结果":
            checks = ["推演场景", "推演风格", "推演故事线"]
            found = sum(1 for c in checks if c in script_content)
            if found >= 2:
                passed = True
                evidence = f"包含推演结果（{found}/3项）"
            else:
                evidence = f"推演结果不完整（{found}/3项）"

        elif name == "时长15-30秒":
            shot_count = len(re.findall(r'镜头\d+', script_content))
            if 4 <= shot_count <= 8:
                passed = True
                evidence = f"脚本包含{shot_count}个镜头，符合15-30秒要求"
            else:
                evidence = f"脚本包含{shot_count}个镜头，不符合15-30秒要求"

        elif name == "无服装特写镜头":
            forbidden_patterns = [
                r'特写.*西装', r'特写.*外套', r'特写.*卫衣', r'特写.*牛仔',
                r'服装细节', r'质地特写', r'标签展示', r'面料特写',
                r'镜头特写.*外套', r'镜头特写.*西装'
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

        elif name == "前3秒有钩子":
            hook_patterns = [r'前3秒钩子', r'钩子', r'【.*钩子']
            if any(re.search(p, script_content) for p in hook_patterns):
                passed = True
                evidence = "前3秒设置了钩子"
            else:
                evidence = "未发现前3秒钩子设置"

        elif name == "受众一致性":
            if "受众画像" in script_content:
                passed = True
                evidence = "脚本受众与服饰受众一致"
            else:
                evidence = "受众一致性不明确"

        elif name == "无价格和购买信息":
            price_pattern = r'¥\d+|价格.*元|购买链接|评论区.*链接'
            if not re.search(price_pattern, script_content):
                passed = True
                evidence = "脚本不包含价格和购买信息"
            else:
                evidence = "脚本包含价格或购买信息"

        elif name == "无教学式内容":
            teaching_pattern = r'拍摄建议|音乐建议|标签建议|发布建议|配乐建议|封面建议'
            if not re.search(teaching_pattern, script_content):
                passed = True
                evidence = "脚本不包含教学式内容"
            else:
                evidence = "脚本包含教学式内容"

        results.append({
            "text": name,
            "passed": passed,
            "evidence": evidence
        })

    return results

def main():
    base_path = "/Users/Abner/.claude/skills/hot-script-generator/workspace/iteration-3"
    evals = ["workplace-anxiety", "healing-lifestyle", "emotional-relationship"]
    configs = ["with_skill", "without_skill"]

    for eval_name in evals:
        with open(f"{base_path}/{eval_name}/eval_metadata.json", "r") as f:
            eval_metadata = json.load(f)

        for config in configs:
            script_path = f"{base_path}/{eval_name}/{config}/outputs/script.md"
            if os.path.exists(script_path):
                with open(script_path, "r") as f:
                    script_content = f.read()

                results = grade_script(script_content, eval_metadata)

                grading = {
                    "eval_id": eval_metadata["eval_id"],
                    "eval_name": eval_name,
                    "config": config,
                    "expectations": results
                }

                output_path = f"{base_path}/{eval_name}/{config}/grading.json"
                with open(output_path, "w") as f:
                    json.dump(grading, f, ensure_ascii=False, indent=2)

                print(f"Graded {eval_name}/{config}: {sum(1 for r in results if r['passed'])}/{len(results)} passed")

if __name__ == "__main__":
    main()