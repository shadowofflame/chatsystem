"""
Tree-of-Thoughts style deep reasoning helper.
Generates multiple thought branches and scores them to pick the best answer.
支持流式输出，边思考边输出。
"""

import json
from dataclasses import dataclass
from typing import List, Optional, Tuple, Callable, Generator, Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI


# 流式事件类型
class StreamEvent:
    """流式事件"""
    THINKING_START = "thinking_start"      # 开始思考
    THINKING_STEP = "thinking_step"        # 思考步骤
    THINKING_SCORE = "thinking_score"      # 评分结果
    THINKING_LAYER = "thinking_layer"      # 层级信息
    THINKING_BEST = "thinking_best"        # 最佳路径
    THINKING_END = "thinking_end"          # 思考结束
    RESPONSE_CHUNK = "response_chunk"      # 响应片段
    RESPONSE_END = "response_end"          # 响应结束
    ERROR = "error"                        # 错误


@dataclass
class Thought:
    content: str
    score: float
    path: List[str]


class TreeOfThoughtReasoner:
    """Lightweight Tree-of-Thought reasoning helper with streaming support."""

    def __init__(
        self,
        llm: ChatOpenAI,
        default_branches: int = 5,
        default_depth: int = 3,
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
    ) -> dict:
        """Run a small tree search and return the best reasoning path.
        
        Returns:
            dict: {
                "thinking_process": str,  # 思考过程
                "best_score": float,      # 最佳得分
                "final_answer": str,      # 最终答案
                "success": bool           # 是否成功
            }
        """
        # 非流式版本：收集所有事件然后返回
        thinking_steps = []
        best_score = 0.0
        final_answer = ""
        success = False
        
        for event in self.solve_stream(problem, context, max_branches, max_depth):
            event_type = event.get("type", "")
            if event_type in [StreamEvent.THINKING_START, StreamEvent.THINKING_LAYER, 
                              StreamEvent.THINKING_STEP, StreamEvent.THINKING_SCORE,
                              StreamEvent.THINKING_BEST]:
                thinking_steps.append(event.get("content", ""))
            elif event_type == StreamEvent.THINKING_END:
                best_score = event.get("best_score", 0.0)
                final_answer = event.get("final_answer", "")
                success = event.get("success", False)
        
        return {
            "thinking_process": "\n".join(thinking_steps),
            "best_score": best_score,
            "final_answer": final_answer,
            "success": success
        }
    
    def solve_stream(
        self,
        problem: str,
        context: str = "",
        max_branches: Optional[int] = None,
        max_depth: Optional[int] = None,
    ) -> Generator[dict, None, None]:
        """
        流式版本的 solve，边思考边输出事件。
        
        Yields:
            dict: 包含 type 和 content 的事件字典
        """
        branches = max_branches or self.default_branches
        depth_limit = max_depth or self.default_depth

        # 开始事件
        yield {
            "type": StreamEvent.THINKING_START,
            "content": f"🎯 问题: {problem}\n⚙️ 参数: 分支数={branches}, 深度={depth_limit}"
        }

        frontier: List[Thought] = [Thought(content=problem, score=0.0, path=[problem])]
        best: Optional[Thought] = None

        for depth in range(depth_limit):
            yield {
                "type": StreamEvent.THINKING_LAYER,
                "content": f"📊 第 {depth + 1}/{depth_limit} 层探索...",
                "layer": depth + 1,
                "total_layers": depth_limit
            }
            
            next_frontier: List[Thought] = []
            for node in frontier:
                proposals = self._propose(problem, context, node.path, branches)
                
                current_path = ' → '.join(node.path[-2:]) if len(node.path) > 1 else '(起点)'
                yield {
                    "type": StreamEvent.THINKING_STEP,
                    "content": f"  └─ 当前路径: {current_path}",
                    "path": current_path
                }
                
                for i, proposal in enumerate(proposals, 1):
                    score, reason = self._score(problem, context, proposal)
                    thought_path = node.path + [proposal]
                    combined = f"思路: {proposal}\n理由: {reason}"
                    candidate = Thought(content=combined, score=score, path=thought_path)
                    next_frontier.append(candidate)
                    
                    # 输出评分事件
                    short_proposal = proposal[:50] + ('...' if len(proposal) > 50 else '')
                    yield {
                        "type": StreamEvent.THINKING_SCORE,
                        "content": f"     {i}. [{score:.1f}分] {short_proposal}",
                        "proposal": proposal,
                        "score": score,
                        "reason": reason
                    }
                    
                    if best is None or score > best.score:
                        best = candidate
            
            frontier = sorted(next_frontier, key=lambda t: t.score, reverse=True)[:branches]
            yield {
                "type": StreamEvent.THINKING_STEP,
                "content": f"  ✅ 保留前 {len(frontier)} 个最优思路"
            }
            
            if not frontier:
                break

        if best is None:
            yield {
                "type": StreamEvent.THINKING_END,
                "content": "❌ 未能生成有效思路",
                "best_score": 0.0,
                "final_answer": "未能生成有效思路，请尝试提供更多信息。",
                "success": False
            }
            return

        # 输出最佳路径
        best_path_text = "\n".join(f"  Step {i+1}: {item}" for i, item in enumerate(best.path[1:]))
        yield {
            "type": StreamEvent.THINKING_BEST,
            "content": f"🏆 最佳推理路径:\n{best_path_text or '  (无)'}\n💯 最终得分: {best.score:.2f}",
            "best_path": best.path,
            "best_score": best.score
        }
        
        yield {
            "type": StreamEvent.THINKING_END,
            "content": "✅ 深度思考完成",
            "best_score": best.score,
            "final_answer": best.content,
            "success": True
        }
