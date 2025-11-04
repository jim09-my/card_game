
import heapq
from typing import List, Tuple

class ScoreBoard:
    """
    得分系统：使用最大堆实时追踪最高得分配对。
    在 Python 中，通过存储负数来实现最大堆。
    """
    def __init__(self):
        # 存储配对得分的最小堆（实际为负数的最大堆）
        self.max_heap: List[int] = []
        self.total_score: int = 0

    def add_match(self, score: int) -> None:
        """
        记录一次成功的配对得分。
        """
        # 存入负数实现最大堆
        heapq.heappush(self.max_heap, -score)
        self.total_score += score

    def get_highest_score_pair(self) -> int:
        """
        获取当前记录的最高配对得分。
        """
        if not self.max_heap:
            return 0
        # 堆顶元素（负数的最小）取反即为最大得分
        return -self.max_heap[0]

    def get_total_score(self) -> int:
        """
        获取所有配对的总分。
        """
        return self.total_score

    def get_match_history(self) -> List[int]:
        """
        返回按分数降序排列的配对历史得分（不修改原堆）。
        """
        # 复制并取出负值，然后排序
        return sorted([-s for s in self.max_heap], reverse=True)

# 示例用途：
# score_board = ScoreBoard()
# score_board.add_match(25)
# score_board.add_match(15)
# print(score_board.get_highest_score_pair()) # 输出: 25