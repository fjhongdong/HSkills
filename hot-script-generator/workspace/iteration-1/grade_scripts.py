#!/usr/bin/env python3
"""Grade the script outputs based on assertions."""

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

        if name == "时长控制在20秒左右":
            # Check number of shots (镜头)
            shot_count = len(re.findall(r'镜头\d+', script_content))
            if 4 <= shot_count <= 6:
                passed = True
                evidence = f"脚本包含{shot_count}个镜头，符合20秒左右要求"
            else:
                evidence = f"脚本包含{shot_count}个镜头，不符合20秒左右要求"

        elif name == "服饰自然融入叙事":
            # Check if 服饰 is mentioned naturally
            if "服饰：" in script_content or "服饰:" in script_content:
                passed = True
                evidence = "服饰描述以自然方式融入脚本"
            else:
                evidence = "脚本中服饰描述不够自然"

        elif name == "无价格和购买信息":
            # Check for price, purchase links
            price_pattern = r'¥\d+|价格|购买|链接|评论区'
            if not re.search(price_pattern, script_content):
                passed = True
                evidence = "脚本不包含价格和购买信息"
            else:
                evidence = "脚本包含价格或购买信息"

        elif name == "无教学式内容":
            # Check for teaching content
            teaching_pattern = r'拍摄建议|音乐建议|标签建议|场景建议|文案.*备选'
            if not re.search(teaching_pattern, script_content):
                passed = True
                evidence = "脚本不包含教学式内容"
            else:
                evidence = "脚本包含教学式内容"

        elif name == "叙事为主":
            # Check for story-driven content
            if "故事线" in script_content or "【故事线】" in script_content:
                passed = True
                evidence = "脚本以叙事为主"
            else:
                evidence = "脚本叙事性不足"

        elif name == "包含情绪/主题/场景/故事线提炼":
            # Check for all elements
            required = ["情绪", "主题", "场景", "故事线"]
            found = [elem for elem in required if f"【{elem}】" in script_content or f"**{elem}**" in script_content]
            if len(found) == 4:
                passed = True
                evidence = f"脚本包含完整的情绪、主题、场景、故事线提炼"
            else:
                evidence = f"脚本缺少部分提炼元素，只找到：{found}"

        results.append({
            "text": name,
            "passed": passed,
            "evidence": evidence
        })

    return results

def main():
    base_path = "/Users/Abner/.claude/skills/hot-script-generator/workspace/iteration-1"

    evals = ["workplace-anxiety", "healing-lifestyle", "emotional-relationship"]
    configs = ["with_skill", "without_skill"]

    for eval_name in evals:
        # Read eval metadata
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