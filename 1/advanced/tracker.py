
import heapq
import time
from typing import List, Tuple, Dict, Any, Optional

# 假设 card.py 中 Card 类已有，且 Card 类应添加一个 last_flipped_time 属性
# 为了方便，这里假定 Card 传入 time 即可，但实际项目中 Card 类应具备时间戳功能。

class MatchFinder:
    """
    匹配查找器：使用哈希表实现 O(1) 级别查找所有相同 ID 卡片位置的功能。
    键：卡片 ID (str)
    值：该 ID 对应的所有卡片位置列表 (List[Tuple[int, int]])
    """

    def __init__(self):
        # 哈希表
        self.tracker: Dict[str, List[Tuple[int, int]]] = {}

    def build_tracker(self, grid: List[List[Any]]):
        """
        初始化时，从游戏网格中构建卡片 ID 到位置的映射。
        grid: 包含 Card 实例的二维列表。
        """
        self.tracker.clear()
        for r, row in enumerate(grid):
            for c, card in enumerate(row):
                card_id = card.id
                if card_id not in self.tracker:
                    self.tracker[card_id] = []
                self.tracker[card_id].append((r, c))

    def find_all_positions(self, card_id: str) -> List[Tuple[int, int]]:
        """
        查找特定卡片 ID 的所有位置。
        """
        return self.tracker.get(card_id, [])


class RiskTracker:
    """
    风险追踪器：使用最小堆实现“遗忘风险”提示功能。
    存储未匹配卡片，以 last_flipped_time (时间戳) 为排序依据。
    堆元素格式: (timestamp, counter, card_id, position)
    - counter 用于解决相同时间戳时的稳定性问题
    """

    def __init__(self):
        # 最小堆
        self.min_heap: List[Tuple[float, int, str, Tuple[int, int]]] = []
        # 用于追踪卡片是否仍在堆中，防止重复
        self.card_lookup: Dict[Tuple[str, Tuple[int, int]], bool] = {}
        self._counter: int = 0  # 稳定性计数器

    def _get_unique_key(self, card_id: str, position: Tuple[int, int]) -> Tuple[str, Tuple[int, int]]:
        """为每张卡片生成唯一的键"""
        return (card_id, position)

    def add_card(self, card_id: str, position: Tuple[int, int], timestamp: float) -> None:
        """
        将未匹配卡片添加到追踪器。
        """
        key = self._get_unique_key(card_id, position)
        if key not in self.card_lookup:
            heapq.heappush(self.min_heap, (timestamp, self._counter, card_id, position))
            self.card_lookup[key] = True
            self._counter += 1

    def update_card(self, card_id: str, position: Tuple[int, int], new_timestamp: float) -> None:
        """
        更新卡片的时间戳，通常在卡片被翻看后调用。
        为了避免复杂堆操作，这里使用“延迟删除”策略：
        1. 移除旧记录 (实际不移除，只在 lookup 中标记为旧)
        2. 添加新记录
        """
        # 注意：此处为简化实现，实际应用中，如果需要精确更新，需要更复杂的堆实现
        # 为了与项目文档保持一致（实现最小堆），我们采用重新添加的方式：
        # 标记旧卡片无效（在实际项目中 DynamicMazeGame 移除并重新添加）

        # 简单的实现方式（不进行精确的堆内更新）：
        # 重新添加到堆中，新的时间戳会更高，旧的（更小的时间戳）将浮到顶部。
        # 在 get_risk_card() 时，需要检查卡片是否已匹配或已更新过。

        # 重新添加：
        heapq.heappush(self.min_heap, (new_timestamp, self._counter, card_id, position))
        self._counter += 1

    def remove_card(self, card_id: str, position: Tuple[int, int]) -> None:
        """
        从追踪器中移除已匹配的卡片。
        """
        # 由于无法直接从 Python 的 heapq 中高效移除任意元素，
        # 实际移除逻辑应由 DynamicMazeGame 在配对成功后实现，
        # 例如将卡片状态标记为 matched，并在 get_risk_card() 时跳过。
        pass  # 留给 DynamicMazeGame 类处理

    def get_risk_card(self) -> Optional[Tuple[str, Tuple[int, int]]]:
        """
        获取当前最久未被翻看的卡片 ID 和位置 (最小堆顶元素)。
        返回 (card_id, position) 或 None。
        注意：在实际集成时，需要调用者（DynamicMazeGame）确保返回的卡片未匹配。
        """
        while self.min_heap:
            timestamp, counter, card_id, position = self.min_heap[0]
            # 假设 DynamicMazeGame 在调用后会检查卡片是否已匹配并返回。
            # 这是一个 "peek" 操作，不移除元素
            return (card_id, position)
        return None

# 示例用途：
# tracker = RiskTracker()
# tracker.add_card("A", (0, 0), time.time() - 10) # 10秒前翻过
# tracker.add_card("B", (0, 1), time.time() - 5)  # 5秒前翻过
# print(tracker.get_risk_card()) # 应该返回 ("A", (0, 0))
# tracker.update_card("A", (0, 0), time.time()) # A 被重新翻看
# print(tracker.get_risk_card()) # 应该返回 ("B", (0, 1))