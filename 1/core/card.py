

import time  # 引入时间模块


class Card:
    def __init__(self, card_id: str, score_weight: int = 10):
        self.id = card_id
        self.is_flipped = False
        self.is_matched = False
        self.score_weight = score_weight
        # 【新增】用于 RiskTracker 追踪的属性
        # 初始化为一个很小的数（例如 0.0 或当前时间），表示从未被翻看
        self.last_flipped_time: float = 0.0

    def flip(self):
        """
        翻开卡片，并更新最后翻看时间。
        """
        if not self.is_flipped:
            self.is_flipped = True
            # 【新增】更新时间戳，用于 RiskTracker 
            self.last_flipped_time = time.time()

    def hide(self):
        if not self.is_matched:
            self.is_flipped = False

    def set_matched(self):
        self.is_matched = True
        self.is_flipped = True
        # 【可选】卡片匹配后，将时间戳设为一个极大值（或直接在 RiskTracker 中移除），
        # 以确保它不会被误判为“风险卡片”。不过，通常在 DynamicMazeGame 逻辑中处理移除更安全。
        # self.last_flipped_time = float('inf')