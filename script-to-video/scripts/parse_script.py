#!/usr/bin/env python3
"""
剧本解析器 - 支持多格式剧本文件解析
支持格式: TXT, Markdown, DOCX, PDF, Final Draft (.fdx)
"""

import re
import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from enum import Enum


class ElementType(Enum):
    """剧本元素类型"""
    SCENE_HEADING = "scene_heading"      # 场景标题
    ACTION = "action"                     # 动作描述
    CHARACTER = "character"               # 角色名
    DIALOGUE = "dialogue"                 # 对白
    PARENTHETICAL = "parenthetical"       # 动作指示（括号内）
    TRANSITION = "transition"             # 转场
    NOTE = "note"                         # 备注


@dataclass
class ScriptElement:
    """剧本元素"""
    type: ElementType
    content: str
    line_number: int
    metadata: Dict = field(default_factory=dict)


@dataclass
class Scene:
    """场景"""
    number: int
    heading: str
    location: str
    time_of_day: str
    int_ext: str  # INT. / EXT.
    elements: List[ScriptElement] = field(default_factory=list)
    characters: List[str] = field(default_factory=list)
    estimated_duration: float = 0.0  # 预估时长（秒）

    def to_dict(self):
        return {
            "number": self.number,
            "heading": self.heading,
            "location": self.location,
            "time_of_day": self.time_of_day,
            "int_ext": self.int_ext,
            "characters": self.characters,
            "estimated_duration": self.estimated_duration,
            "element_count": len(self.elements)
        }


@dataclass
class ParsedScript:
    """解析后的剧本"""
    title: str
    scenes: List[Scene] = field(default_factory=list)
    all_characters: List[str] = field(default_factory=list)
    all_locations: List[str] = field(default_factory=list)
    total_duration: float = 0.0
    metadata: Dict = field(default_factory=dict)


class ScriptParser:
    """剧本解析器"""

    # 场景标题正则 - 匹配 INT./EXT. 开头的行
    SCENE_HEADING_PATTERN = re.compile(
        r'^(INT\.|EXT\.|INT/EXT\.|I/E\.)\s*(.+?)(?:\s*[-–—]\s*(.+))?$',
        re.IGNORECASE
    )

    # 中文场景标题正则 - 匹配 "场景X" 或 "第X场" 格式
    CN_SCENE_HEADING_PATTERN = re.compile(
        r'^(?:场景|第)\s*(\d+)\s*(?:场|幕)?[：:\s]*(.+)?$'
    )

    # 角色名正则 - 全大写或特定格式
    CHARACTER_PATTERN = re.compile(r'^([A-Z][A-Z\s]+|[\u4e00-\u9fa5]{1,4})(?:\s*\(.*\))?$')

    # 括号动作指示
    PARENTHETICAL_PATTERN = re.compile(r'^\s*\((.+)\)\s*$')

    # 转场正则
    TRANSITION_PATTERN = re.compile(
        r'^(FADE IN:|FADE OUT\.|CUT TO:|DISSOLVE TO:|SMASH CUT:|MATCH CUT:)',
        re.IGNORECASE
    )

    def __init__(self):
        self.scenes: List[Scene] = []
        self.current_scene: Optional[Scene] = None
        self.all_characters: set = set()
        self.all_locations: set = set()
        self.scene_count = 0

    def parse_file(self, file_path: str) -> ParsedScript:
        """解析剧本文件"""
        path = Path(file_path)
        suffix = path.suffix.lower()

        if suffix == '.fdx':
            return self._parse_final_draft(path)
        elif suffix == '.docx':
            return self._parse_docx(path)
        elif suffix == '.pdf':
            return self._parse_pdf(path)
        else:  # .txt, .md, etc.
            return self._parse_text(path)

    def parse_text(self, text: str, title: str = "Untitled") -> ParsedScript:
        """解析剧本文本"""
        lines = text.split('\n')
        self._reset()

        for i, line in enumerate(lines, 1):
            self._parse_line(line.strip(), i)

        # 完成最后一个场景
        if self.current_scene:
            self._finalize_scene()

        # 计算总时长
        total_duration = sum(s.estimated_duration for s in self.scenes)

        return ParsedScript(
            title=title,
            scenes=self.scenes,
            all_characters=sorted(list(self.all_characters)),
            all_locations=sorted(list(self.all_locations)),
            total_duration=total_duration,
            metadata={
                "scene_count": len(self.scenes),
                "character_count": len(self.all_characters),
                "location_count": len(self.all_locations)
            }
        )

    def _reset(self):
        """重置解析器状态"""
        self.scenes = []
        self.current_scene = None
        self.all_characters = set()
        self.all_locations = set()
        self.scene_count = 0

    def _parse_line(self, line: str, line_number: int):
        """解析单行"""
        if not line:
            return

        # 检查场景标题
        scene_match = self.SCENE_HEADING_PATTERN.match(line)
        cn_scene_match = self.CN_SCENE_HEADING_PATTERN.match(line)

        if scene_match or cn_scene_match:
            # 完成上一个场景
            if self.current_scene:
                self._finalize_scene()

            # 开始新场景
            self.scene_count += 1
            if scene_match:
                int_ext = scene_match.group(1).upper()
                location = scene_match.group(2).strip()
                time_of_day = scene_match.group(3).strip() if scene_match.group(3) else "DAY"
            else:
                int_ext = "INT."
                location = cn_scene_match.group(2) or f"场景{cn_scene_match.group(1)}"
                time_of_day = "DAY"

            self.current_scene = Scene(
                number=self.scene_count,
                heading=line,
                location=location,
                time_of_day=time_of_day,
                int_ext=int_ext
            )
            self.all_locations.add(location)
            return

        # 如果还没有场景,创建一个默认场景
        if not self.current_scene:
            self.scene_count += 1
            self.current_scene = Scene(
                number=self.scene_count,
                heading="SCENE 1",
                location="UNKNOWN",
                time_of_day="DAY",
                int_ext="INT."
            )

        # 检查转场
        if self.TRANSITION_PATTERN.match(line):
            self.current_scene.elements.append(ScriptElement(
                type=ElementType.TRANSITION,
                content=line,
                line_number=line_number
            ))
            return

        # 检查括号动作指示
        paren_match = self.PARENTHETICAL_PATTERN.match(line)
        if paren_match:
            self.current_scene.elements.append(ScriptElement(
                type=ElementType.PARENTHETICAL,
                content=paren_match.group(1),
                line_number=line_number
            ))
            return

        # 检查角色名
        if self.CHARACTER_PATTERN.match(line) and len(line) < 30:
            char_name = line.split('(')[0].strip()
            self.current_scene.elements.append(ScriptElement(
                type=ElementType.CHARACTER,
                content=char_name,
                line_number=line_number
            ))
            self.all_characters.add(char_name)
            if char_name not in self.current_scene.characters:
                self.current_scene.characters.append(char_name)
            return

        # 判断是对白还是动作描述
        # 如果上一个元素是角色名,则为对白
        if (self.current_scene.elements and
            self.current_scene.elements[-1].type == ElementType.CHARACTER):
            self.current_scene.elements.append(ScriptElement(
                type=ElementType.DIALOGUE,
                content=line,
                line_number=line_number
            ))
        else:
            self.current_scene.elements.append(ScriptElement(
                type=ElementType.ACTION,
                content=line,
                line_number=line_number
            ))

    def _finalize_scene(self):
        """完成当前场景的处理"""
        if self.current_scene:
            # 估算场景时长 (基于对白和动作数量)
            dialogue_count = sum(1 for e in self.current_scene.elements
                                if e.type == ElementType.DIALOGUE)
            action_count = sum(1 for e in self.current_scene.elements
                              if e.type == ElementType.ACTION)

            # 粗略估算: 每句对白3秒, 每个动作描述5秒
            self.current_scene.estimated_duration = dialogue_count * 3 + action_count * 5

            self.scenes.append(self.current_scene)

    def _parse_text(self, path: Path) -> ParsedScript:
        """解析纯文本文件"""
        text = path.read_text(encoding='utf-8')
        return self.parse_text(text, title=path.stem)

    def _parse_docx(self, path: Path) -> ParsedScript:
        """解析 DOCX 文件"""
        try:
            from docx import Document
            doc = Document(str(path))
            text = '\n'.join([para.text for para in doc.paragraphs])
            return self.parse_text(text, title=path.stem)
        except ImportError:
            raise ImportError("请安装 python-docx: pip install python-docx")

    def _parse_pdf(self, path: Path) -> ParsedScript:
        """解析 PDF 文件"""
        try:
            import pdfplumber
            text_parts = []
            with pdfplumber.open(str(path)) as pdf:
                for page in pdf.pages:
                    text_parts.append(page.extract_text() or '')
            text = '\n'.join(text_parts)
            return self.parse_text(text, title=path.stem)
        except ImportError:
            raise ImportError("请安装 pdfplumber: pip install pdfplumber")

    def _parse_final_draft(self, path: Path) -> ParsedScript:
        """解析 Final Draft (.fdx) 文件"""
        import xml.etree.ElementTree as ET

        tree = ET.parse(str(path))
        root = tree.getroot()

        self._reset()
        title = path.stem

        # 查找标题
        title_page = root.find('.//TitlePage')
        if title_page is not None:
            content = title_page.find('.//Content')
            if content is not None and content.text:
                title = content.text.strip()

        # 解析内容
        for para in root.findall('.//Paragraph'):
            para_type = para.get('Type', '')
            text_elem = para.find('Text')
            text = text_elem.text if text_elem is not None and text_elem.text else ''

            if para_type == 'Scene Heading':
                self._parse_line(text, 0)
            elif para_type == 'Character':
                self._parse_line(text.upper(), 0)
            elif para_type == 'Dialogue':
                if self.current_scene:
                    self.current_scene.elements.append(ScriptElement(
                        type=ElementType.DIALOGUE,
                        content=text,
                        line_number=0
                    ))
            elif para_type == 'Parenthetical':
                if self.current_scene:
                    self.current_scene.elements.append(ScriptElement(
                        type=ElementType.PARENTHETICAL,
                        content=text,
                        line_number=0
                    ))
            elif para_type == 'Action':
                if self.current_scene:
                    self.current_scene.elements.append(ScriptElement(
                        type=ElementType.ACTION,
                        content=text,
                        line_number=0
                    ))
            elif para_type == 'Transition':
                if self.current_scene:
                    self.current_scene.elements.append(ScriptElement(
                        type=ElementType.TRANSITION,
                        content=text,
                        line_number=0
                    ))

        if self.current_scene:
            self._finalize_scene()

        total_duration = sum(s.estimated_duration for s in self.scenes)

        return ParsedScript(
            title=title,
            scenes=self.scenes,
            all_characters=sorted(list(self.all_characters)),
            all_locations=sorted(list(self.all_locations)),
            total_duration=total_duration,
            metadata={
                "scene_count": len(self.scenes),
                "character_count": len(self.all_characters),
                "location_count": len(self.all_locations),
                "format": "Final Draft"
            }
        )


def parse_script(file_path: str) -> Dict:
    """
    解析剧本文件的便捷函数

    Args:
        file_path: 剧本文件路径

    Returns:
        解析结果字典
    """
    parser = ScriptParser()
    result = parser.parse_file(file_path)

    return {
        "title": result.title,
        "metadata": result.metadata,
        "total_duration_seconds": result.total_duration,
        "total_duration_formatted": f"{int(result.total_duration // 60)}:{int(result.total_duration % 60):02d}",
        "all_characters": result.all_characters,
        "all_locations": result.all_locations,
        "scenes": [scene.to_dict() for scene in result.scenes]
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python parse_script.py <script_file>")
        print("Supported formats: .txt, .md, .docx, .pdf, .fdx")
        sys.exit(1)

    result = parse_script(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False, indent=2))
