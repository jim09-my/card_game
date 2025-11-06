from typing import List, Tuple, Dict, Optional
from core.card import Card
from core.utils import fisher_yates_shuffle, is_valid_position


class DynamicMazeGame:
    """
    困难模式：使用图（邻接表）约束翻牌移动。
    - 节点：每个节点对应一张卡片（Card）
    - 边：允许从某节点移动到其邻居节点（四方向邻接）
    - 规则：第二次翻牌必须是第一次翻开的邻居节点
    - 与 SimpleGame 对齐的接口：flip_card、hide_all_flipped、is_completed、get_grid_state、get_card
    额外接口：bfs_shortest_path、get_graph_state、get_hint_info
    """

    def __init__(self, rows: int, cols: int, patterns: List[str] = None):
        if (rows * cols) % 2 != 0:
            raise ValueError("网格总数必须为偶数，以确保成对卡片。")

        self.rows = rows
        self.cols = cols
        total = rows * cols

        # 生成成对的图案集合
        if patterns is None:
            patterns = [chr(ord('A') + i) for i in range(total // 2)]
        needed = total // 2
        if len(patterns) < needed:
            reps = (needed + len(patterns) - 1) // len(patterns)
            patterns = (patterns * reps)[:needed]

        paired_ids: List[str] = []
        for i in range(needed):
            paired_ids.extend([patterns[i], patterns[i]])

        # 洗牌后按节点顺序分配
        shuffled = fisher_yates_shuffle(paired_ids)
        self.nodes: List[Card] = [Card(card_id) for card_id in shuffled]

        # 使用网格四向邻接生成连通图（邻接表）
        self.graph: Dict[int, List[int]] = self._build_grid_adjacency()

        # 选择状态与得分
        self._first_selected: Optional[Tuple[int, int]] = None
        self._second_selected: Optional[Tuple[int, int]] = None
        self.score: int = 0

    def _index(self, row: int, col: int) -> int:
        return row * self.cols + col

    def _rc_from_index(self, idx: int) -> Tuple[int, int]:
        return (idx // self.cols, idx % self.cols)

    def _build_grid_adjacency(self) -> Dict[int, List[int]]:
        """
        基于网格的四方向邻接（上/下/左/右），生成邻接表。
        保证图为连通（天然连通）。
        """
        graph: Dict[int, List[int]] = {}
        for r in range(self.rows):
            for c in range(self.cols):
                idx = self._index(r, c)
                neighbors: List[int] = []

                if is_valid_position(r - 1, c, self.rows, self.cols):
                    neighbors.append(self._index(r - 1, c))
                if is_valid_position(r + 1, c, self.rows, self.cols):
                    neighbors.append(self._index(r + 1, c))
                if is_valid_position(r, c - 1, self.rows, self.cols):
                    neighbors.append(self._index(r, c - 1))
                if is_valid_position(r, c + 1, self.rows, self.cols):
                    neighbors.append(self._index(r, c + 1))

                graph[idx] = neighbors
        return graph

    def bfs_shortest_path(self, start_idx: int, target_idx: int) -> int:
        """
        使用 BFS 计算从 start 到 target 的最短路径长度。
        若不可达返回 -1。若起点等于终点返回 0。
        """
        if start_idx == target_idx:
            return 0

        from collections import deque

        visited = set([start_idx])
        dist = {start_idx: 0}
        dq = deque([start_idx])

        while dq:
            u = dq.popleft()
            for v in self.graph.get(u, []):
                if v not in visited:
                    visited.add(v)
                    dist[v] = dist[u] + 1
                    if v == target_idx:
                        return dist[v]
                    dq.append(v)
        return -1

    def get_card(self, row: int, col: int) -> Card:
        if not is_valid_position(row, col, self.rows, self.cols):
            raise IndexError("坐标超出网格范围。")
        return self.nodes[self._index(row, col)]

    def flip_card(self, row: int, col: int) -> bool:
        """
        翻开位于 (row, col) 的卡片。
        - 第一次翻牌：任意节点允许
        - 第二次翻牌：必须是第一次的邻居节点（graph 中距离为 1）
        返回：是否配对成功（True 表示成功配对；False 表示未配对）
        失败时保留两张牌为翻开状态，等待外部调用 hide_all_flipped() 盖回。
        """
        if not is_valid_position(row, col, self.rows, self.cols):
            raise IndexError("坐标超出网格范围。")

        card = self.get_card(row, col)
        if card.is_matched or card.is_flipped:
            return False  # 已配对或已翻开，不可重复翻

        if self._first_selected is None:
            card.flip()
            self._first_selected = (row, col)
            return False

        # 第二次翻牌必须是第一次的邻居
        first_idx = self._index(*self._first_selected)
        cur_idx = self._index(row, col)
        if cur_idx not in self.graph.get(first_idx, []):
            # 非邻居，不允许翻牌
            return False

        card.flip()
        self._second_selected = (row, col)
        return self._evaluate_pair()

    def _evaluate_pair(self) -> bool:
        r1, c1 = self._first_selected
        r2, c2 = self._second_selected
        card1 = self.get_card(r1, c1)
        card2 = self.get_card(r2, c2)

        matched = False
        if card1.id == card2.id:
            card1.set_matched()
            card2.set_matched()
            pair_score = card1.score_weight + card2.score_weight
            self.score += pair_score
            matched = True

        # 重置选中记录（与 SimpleGame 对齐；失败由外部定时调用 hide_all_flipped 处理）
        self._first_selected = None
        self._second_selected = None
        return matched

    def hide_all_flipped(self) -> None:
        for card in self.nodes:
            if card.is_flipped and not card.is_matched:
                card.hide()

    def is_completed(self) -> bool:
        for card in self.nodes:
            if not card.is_matched:
                return False
        return True

    def get_grid_state(self) -> List[List[Tuple[str, bool, bool]]]:
        """
        适配现有 UI：返回二维网格状态 (id, is_flipped, is_matched)。
        虽然内部是图结构，但这里按照 rows×cols 映射到网格便于渲染。
        """
        state: List[List[Tuple[str, bool, bool]]] = []
        for r in range(self.rows):
            row_state: List[Tuple[str, bool, bool]] = []
            for c in range(self.cols):
                card = self.get_card(r, c)
                row_state.append((card.id, card.is_flipped, card.is_matched))
            state.append(row_state)
        return state

    def get_graph_state(self) -> Dict[str, List]:
        """
        返回用于图形渲染的节点与边信息（供 UI 后续集成）。
        nodes: 每个节点包含 index/row/col/id/is_flipped/is_matched
        edges: 无重复的无向边 (u, v) 列表
        """
        nodes: List[Dict] = []
        for idx, card in enumerate(self.nodes):
            r, c = self._rc_from_index(idx)
            nodes.append({
                "index": idx,
                "row": r,
                "col": c,
                "id": card.id,
                "is_flipped": card.is_flipped,
                "is_matched": card.is_matched,
            })

        edges: List[Tuple[int, int]] = []
        seen = set()
        for u, neighs in self.graph.items():
            for v in neighs:
                key = (min(u, v), max(u, v))
                if key not in seen:
                    seen.add(key)
                    edges.append(key)

        return {"nodes": nodes, "edges": edges}

    def get_hint_info(self) -> Tuple[Optional[Tuple[int, int]], List[Tuple[int, int]]]:
        """
        返回当前已选中的第一个节点及其邻居位置列表（行列坐标）。
        供 UI 高亮可选下一步位置使用。
        """
        if self._first_selected is None:
            return None, []
        first_idx = self._index(*self._first_selected)
        neighs = self.graph.get(first_idx, [])
        positions = [self._rc_from_index(idx) for idx in neighs]
        return self._first_selected, positions