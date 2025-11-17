from typing import List, Tuple
from core.card import Card
from core.utils import fisher_yates_shuffle, is_valid_position

class SimpleGame:
    """
    简单模式：经典网格翻牌。使用二维列表存储 Card 实例。
    初始化：生成成对的卡片，将其洗牌后填充到网格中。
    支持操作：
      - 翻牌：翻开指定位置的卡片
      - 检查配对：在连续两次翻牌后进行配对判断并更新状态
      - 获取当前网格状态（便于界面渲染）
    """
    def __init__(self, rows: int, cols: int, patterns: List[str] = None):
        """
        rows x cols 必须为偶数个卡片总数，因为需要成对。
        patterns: 可选的图案标记集合，如 ["A","B","C",...]
        """
        if (rows * cols) % 2 != 0:
            raise ValueError("网格总数必须为偶数，以确保成对卡片。")
        self.rows = rows
        self.cols = cols
        total = rows * cols

        # 生成成对的图案集合
        if patterns is None:
            # 给出简单的默认图案标识
            patterns = [chr(ord('A') + i) for i in range(total // 2)]
        needed = total // 2
        if len(patterns) < needed:
            # 如不足，重复扩展并截取
            reps = (needed + len(patterns) - 1) // len(patterns)
            patterns = (patterns * reps)[:needed]

        paired_ids = []
        for i in range(needed):
            paired_ids.extend([patterns[i], patterns[i]])

        # 洗牌后填充网格
        shuffled = fisher_yates_shuffle(paired_ids)
        self.grid: List[List[Card]] = []
        idx = 0
        for r in range(rows):
            row_cards = []
            for c in range(cols):
                row_cards.append(Card(shuffled[idx]))
                idx += 1
            self.grid.append(row_cards)

        self._first_selected: Tuple[int, int] = None
        self._second_selected: Tuple[int, int] = None
        self.score: int = 0
        self.fail_count: int = 0
        self.shuffle_threshold: int = 8
        self.pending_shuffle: bool = False

    def get_card(self, row: int, col: int) -> Card:
        if not is_valid_position(row, col, self.rows, self.cols):
            raise IndexError("坐标超出网格范围。")
        return self.grid[row][col]

    def flip_card(self, row: int, col: int) -> bool:
        """
        翻开位于 (row, col) 的卡片。
        返回值为布尔，表示是否已完成一次配对检查并更新分数/状态。
        逻辑：
          - 不能翻已经匹配的卡或当前正在翻的同一张
          - 第一次翻牌记录为第一张
          - 第二次翻牌后进行配对判断：
              如果相同id，标记两张为 matched，并累积分数
              否则将两张在下一步隐藏
        """
        if not is_valid_position(row, col, self.rows, self.cols):
            raise IndexError("坐标超出网格范围。")

        card = self.grid[row][col]
        if card.is_matched or card.is_flipped:
            return False  # 无法再次翻开或已配对

        card.flip()

        if self._first_selected is None:
            self._first_selected = (row, col)
            return False
        else:
            self._second_selected = (row, col)
            return self._evaluate_pair()

    def _evaluate_pair(self) -> bool:
        """
        检查当前两张翻开的卡片是否配对。
        返回值：是否完成一次配对处理（并且清空选中状态）。
        """
        r1, c1 = self._first_selected
        r2, c2 = self._second_selected
        card1 = self.grid[r1][c1]
        card2 = self.grid[r2][c2]

        # 确保ID比较是字符串比较
        id1 = str(card1.id).strip()
        id2 = str(card2.id).strip()
        
        matched = (id1 == id2)
        
        if matched:
            card1.set_matched()
            card2.set_matched()
            # 通过基础分值和权重累加分数
            pair_score = card1.score_weight + card2.score_weight
            self.score += pair_score
            self.fail_count = 0  # 重置失败计数
            print(f"配对成功！卡片ID: {id1} == {id2}")
        else:
            self.fail_count += 1
            print(f"配对失败！卡片ID: {id1} != {id2}, 失败次数: {self.fail_count}")
            # 检查是否需要洗牌
            if self.fail_count >= self.shuffle_threshold:
                self.pending_shuffle = True
                print(f"触发洗牌！连续失败 {self.fail_count} 次")

        # 重置选中记录，准备下一轮
        self._first_selected = None
        self._second_selected = None

        # 返回是否配对成功
        return matched

    def hide_all_flipped(self) -> None:
        """
        将所有处于翻开但未匹配的卡片隐藏回背面状态。
        """
        for row in self.grid:
            for card in row:
                if card.is_flipped and not card.is_matched:
                    card.hide()
        
        # 如果需要洗牌，执行洗牌操作
        if self.pending_shuffle:
            self._shuffle_unmatched()
            self.pending_shuffle = False
    
    def _shuffle_unmatched(self) -> None:
        """
        洗牌未匹配的卡片（只改变位置，不改变ID）
        """
        unmatched_cards = []
        unmatched_positions = []
        
        # 收集所有未匹配的卡片及其位置
        for r in range(self.rows):
            for c in range(self.cols):
                card = self.grid[r][c]
                if not card.is_matched:
                    card.is_flipped = False  # 盖回卡片
                    unmatched_cards.append(card)
                    unmatched_positions.append((r, c))
        
        # 洗牌卡片列表（只改变顺序，不改变ID）
        shuffled_cards = fisher_yates_shuffle(unmatched_cards.copy())
        
        # 将洗牌后的卡片重新分配到原来的位置
        for i, (r, c) in enumerate(unmatched_positions):
            self.grid[r][c] = shuffled_cards[i]

    def is_completed(self) -> bool:
        """检查所有卡片是否均已配对完成。"""
        for row in self.grid:
            for card in row:
                if not card.is_matched:
                    return False
        return True

    def get_grid_state(self) -> List[List[Tuple[str, bool, bool]]]:
        """
        返回简单的网格状态，便于前端渲染。
        每个元素为 (id, is_flipped, is_matched)
        """
        state = []
        for r in range(self.rows):
            row_state = []
            for c in range(self.cols):
                card = self.grid[r][c]
                row_state.append((card.id, card.is_flipped, card.is_matched))
            state.append(row_state)
        return state

    def reset(self) -> None:
        """
        重置游戏为初始状态（保留原始图案分布，只清理状态）。
        """
        self._first_selected = None
        self._second_selected = None
        self.score = 0
        for row in self.grid:
            for card in row:
                card.is_flipped = False
                card.is_matched = False
