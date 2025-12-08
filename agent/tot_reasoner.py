"""
Tree-of-Thoughts style deep reasoning helper.
Generates multiple thought branches and scores them to pick the best answer.
"""

import json
from dataclasses import dataclass
from typing import List, Optional, Tuple

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI


@dataclass
class Thought:
    content: str
    score: float
    path: List[str]


class TreeOfThoughtReasoner:
    """Lightweight Tree-of-Thought reasoning helper."""

    def __init__(
        self,
        llm: ChatOpenAI,
        default_branches: int = 3,
        default_depth: int = 2,
    ) -> None:
        self.llm = llm
        self.default_branches = max(1, default_branches)
        self.default_depth = max(1, default_depth)

        self._propose_chain = (
            ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        "你是深度推理助手，使用分支思考（Tree-of-Thought）。\n"
                        "给定问题和上下文，提出最多{branches}个下一步思路，用简洁中文表述。\n"
                        "返回 JSON 数组字符串，每个元素是一个字符串，代表一个候选思路。",
                    ),
                    (
                        "human",
                        "问题: {problem}\n上下文: {context}\n当前路径: {path}\n请给出下一步候选思路",
                    ),
                ]
            )
            | self.llm
            | StrOutputParser()
        )

        self._score_chain = (
            ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        "你是评估员，给思路打分，0-10，10最好。\n"
                        "返回 JSON: {{\"score\": number, \"reason\": string}}。",
                    ),
                    (
                        "human",
                        "问题: {problem}\n上下文: {context}\n候选思路: {thought}\n请打分并简述理由",
                    ),
                ]
            )
            | self.llm
            | StrOutputParser()
        )

    def _propose(self, problem: str, context: str, path: List[str], branches: int) -> List[str]:
        raw = self._propose_chain.invoke(
            {"problem": problem, "context": context, "path": " -> ".join(path) or "(root)", "branches": branches}
        )
        try:
            data = json.loads(raw)
            if isinstance(data, list):
                return [str(item) for item in data][:branches]
        except Exception:
            pass
        return [line.strip("- ") for line in raw.splitlines() if line.strip()][:branches]

    def _score(self, problem: str, context: str, thought: str) -> Tuple[float, str]:
        raw = self._score_chain.invoke({"problem": problem, "context": context, "thought": thought})
        try:
            data = json.loads(raw)
            score = float(data.get("score", 0))
            reason = str(data.get("reason", ""))
            return score, reason
        except Exception:
            try:
                score_line = raw.strip().split()[0]
                score = float(score_line)
                return score, raw
            except Exception:
                return 0.0, raw

    def solve(
        self,
        problem: str,
        context: str = "",
        max_branches: Optional[int] = None,
        max_depth: Optional[int] = None,
    ) -> str:
        """Run a small tree search and return the best reasoning path."""
        branches = max_branches or self.default_branches
        depth_limit = max_depth or self.default_depth

        frontier: List[Thought] = [Thought(content=problem, score=0.0, path=[problem])]
        best: Optional[Thought] = None

        for depth in range(depth_limit):
            next_frontier: List[Thought] = []
            for node in frontier:
                proposals = self._propose(problem, context, node.path, branches)
                for proposal in proposals:
                    score, reason = self._score(problem, context, proposal)
                    thought_path = node.path + [proposal]
                    combined = f"思路: {proposal}\n理由: {reason}"
                    candidate = Thought(content=combined, score=score, path=thought_path)
                    next_frontier.append(candidate)
                    if best is None or score > best.score:
                        best = candidate
            frontier = sorted(next_frontier, key=lambda t: t.score, reverse=True)[:branches]
            if not frontier:
                break

        if best is None:
            return "未能生成有效思路，请尝试提供更多信息。"

        thoughts_text = "\n".join(f"Step {i+1}: {item}" for i, item in enumerate(best.path[1:]))
        return (
            "深度思考完成。\n"
            f"最佳路径得分: {best.score:.2f}\n"
            f"思考路径:\n{thoughts_text or '无'}\n"
            f"总结: {best.content}"
        )
