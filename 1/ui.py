"""
ui.py - 游戏界面渲染模块（英文版）
"""
import pygame
from typing import Tuple, Optional, List

class GameUI:
    """游戏界面渲染器"""
    
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        
        # 初始化字体
        pygame.font.init()
        self.title_font = pygame.font.Font(None, 72)
        self.menu_font = pygame.font.Font(None, 36)
        self.card_font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        
        # 定义颜色方案
        self.colors = {
            'background': (135, 206, 235),
            'card_front': (255, 255, 255),
            'card_back': (70, 130, 180),
            'matched': (144, 238, 144),
            'victory': (50, 205, 50),
            'button': (70, 130, 180),
            'button_hover': (100, 160, 210),
            'text': (255, 255, 255),
            'hud_bg': (255, 255, 255, 200),
            'leaderboard_bg': (240, 248, 255),
            'leaderboard_border': (100, 149, 237)
        }
        
        # 初始化按钮布局
        self.init_buttons()
        
    def init_buttons(self):
        """初始化所有按钮的位置"""
        # 主菜单按钮
        self.menu_buttons = {}
        button_width, button_height = 250, 60
        button_spacing = 30
        start_y = 300
        
        buttons = ["开始简单模式", "开始困难模式", "排行榜", "退出游戏"]
        for i, text in enumerate(buttons):
            x = (self.width - button_width) // 2
            y = start_y + i * (button_height + button_spacing)
            rect = pygame.Rect(x, y, button_width, button_height)
            self.menu_buttons[text] = rect
        
        # 游戏按钮
        self.game_buttons = {}
        button_width = 120
        button_height = 40
        button_spacing = 10
        start_x = 40
        start_y = 80
        
        game_buttons = ["delay", "block", "restart", "menu"]
        for i, key in enumerate(game_buttons):
            x = start_x + i * (button_width + button_spacing)
            y = start_y
            rect = pygame.Rect(x, y, button_width, button_height)
            self.game_buttons[key] = rect
        
        # 胜利界面按钮
        self.victory_buttons = {}
        button_width, button_height = 200, 50
        start_x = (self.width - 2 * button_width - 50) // 2
        start_y = 450
        
        buttons = ["重新开始", "主菜单"]
        for i, text in enumerate(buttons):
            x = start_x + i * (button_width + 50)
            y = start_y
            rect = pygame.Rect(x, y, button_width, button_height)
            self.victory_buttons[text] = rect
        
        # 排行榜按钮
        self.leaderboard_buttons = {}
        leaderboard_button_width, leaderboard_button_height = 150, 45
        start_x = (self.width - leaderboard_button_width) // 2
        start_y = 600
        
        leaderboard_buttons = ["返回主菜单", "刷新排行榜"]
        for i, text in enumerate(leaderboard_buttons):
            x = start_x + i * (leaderboard_button_width + 20)
            y = start_y
            rect = pygame.Rect(x, y, leaderboard_button_width, leaderboard_button_height)
            self.leaderboard_buttons[text] = rect
    
    def render(self, game_state: str, current_game, waiting_to_hide: bool):
        """根据游戏状态渲染界面"""
        self.screen.fill(self.colors['background'])
        
        if game_state == "menu":
            self.render_menu()
        elif game_state == "game":
            self.render_game_interface(current_game, waiting_to_hide)
        elif game_state == "victory":
            self.render_game_interface(current_game, waiting_to_hide)
            self.render_victory_interface(current_game)
        elif game_state == "defeat":
            self.render_game_interface(current_game, waiting_to_hide)
            self.render_defeat_interface(current_game)
        elif game_state == "leaderboard":
            self.render_leaderboard_interface(self.leaderboard_data)
        
        pygame.display.flip()
        self.render_menu()
    
    def render_menu(self):
        """渲染主菜单界面"""
        # 绘制标题
        title_text = self.title_font.render("🃏 记忆迷宫 🃏", True, (50, 50, 150))
        title_rect = title_text.get_rect(center=(self.width // 2, 150))
        self.screen.blit(title_text, title_rect)
        
        # 绘制副标题
        subtitle_text = self.menu_font.render("Memory Maze Game", True, (100, 100, 150))
        subtitle_rect = subtitle_text.get_rect(center=(self.width // 2, 200))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # 绘制按钮
        mouse_pos = pygame.mouse.get_pos()
        for button_id, button_rect in self.menu_buttons.items():
            # 按钮颜色
            if button_rect.collidepoint(mouse_pos):
                bg_color = self.colors['button_hover']
            else:
                bg_color = self.colors['button']
            
            # 绘制按钮
            pygame.draw.rect(self.screen, bg_color, button_rect, border_radius=10)
            pygame.draw.rect(self.screen, (50, 50, 50), button_rect, 2, border_radius=10)
            
            # 绘制按钮文字
            text_surface = self.menu_font.render(button_id, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=button_rect.center)
            self.screen.blit(text_surface, text_rect)
    
    def render_main_menu(self):
        """渲染主菜单"""
        # 绘制标题
        title_text = "Memory Match Game"
        title_surface = self.title_font.render(title_text, True, self.colors['title'])
        title_x = self.width // 2 - title_surface.get_width() // 2
        title_y = 100
        self.screen.blit(title_surface, (title_x, title_y))
        
        subtitle_text = "Find Matching Pairs"
        subtitle_surface = self.info_font.render(subtitle_text, True, (100, 100, 100))
        subtitle_x = self.width // 2 - subtitle_surface.get_width() // 2
        subtitle_y = 160
        self.screen.blit(subtitle_surface, (subtitle_x, subtitle_y))
        
        # 绘制菜单按钮
        mouse_pos = pygame.mouse.get_pos()
        button_texts = ["Simple Game", "Hard Game", "Exit"]  # 修改为要求的按钮文字
        
        for i, (button_id, button_rect) in enumerate(self.menu_buttons.items()):
            # 按钮颜色（悬停效果）
            if button_rect.collidepoint(mouse_pos):
                bg_color = self.colors['button_hover']
            else:
                bg_color = self.colors['button']
            
            # 绘制按钮背景
            pygame.draw.rect(self.screen, bg_color, button_rect, border_radius=10)
            pygame.draw.rect(self.screen, (50, 50, 50), button_rect, 2, border_radius=10)
            
            # 绘制按钮文字
            text_surface = self.menu_font.render(button_texts[i], True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=button_rect.center)
            self.screen.blit(text_surface, text_rect)
        
        # 绘制提示信息
        hint_text = "Click buttons to start game"
        hint_surface = self.small_font.render(hint_text, True, (150, 150, 150))
        hint_x = self.width // 2 - hint_surface.get_width() // 2
        hint_y = 500
        self.screen.blit(hint_surface, (hint_x, hint_y))
    
    def render_game_interface(self, game, waiting_to_hide: bool):
        """渲染游戏界面"""
        if not game:
            return
        
        # 游戏信息栏
        mode_text = "Mode: Game"
        mode_surface = self.menu_font.render(mode_text, True, self.colors['title'])
        self.screen.blit(mode_surface, (50, 20))
        
        score_text = f"Score: {game.score}"
        score_surface = self.menu_font.render(score_text, True, self.colors['text'])
        self.screen.blit(score_surface, (50, 70))
        
        progress = self.calculate_progress(game)
        progress_text = f"Progress: {progress}%"
        progress_surface = self.menu_font.render(progress_text, True, self.colors['text'])
        self.screen.blit(progress_surface, (50, 120))
        
        # 计时器
        if hasattr(game, 'get_remaining_time_ms'):
            remaining_ms = game.get_remaining_time_ms()
            remaining_s = max(0, remaining_ms // 1000)
            time_text = f"Timer: {remaining_s}s"
            time_surface = self.menu_font.render(time_text, True, (180, 60, 60))
            self.screen.blit(time_surface, (50, 170))

        # 洗牌提示与道具数量
        if hasattr(game, 'get_shuffle_status'):
            st = game.get_shuffle_status()
            warn_text = ""
            if st.get('recently_shuffled'):
                warn_text = "Shuffled!"
            else:
                if st.get('remaining') == 1 and not st.get('pending_shuffle'):
                    warn_text = "Warning: 1 more mismatch will shuffle"
            if warn_text:
                warn_surface = self.info_font.render(warn_text, True, (200, 100, 50))
                warn_x = self.width // 2 - warn_surface.get_width() // 2
                warn_y = 20
                self.screen.blit(warn_surface, (warn_x, warn_y))
        if hasattr(game, 'get_block_remaining_seconds'):
            left = game.get_block_remaining_seconds()
            if left > 0:
                block_text = f"Shuffle Block: {left}s"
                block_surface = self.info_font.render(block_text, True, (60, 140, 200))
                block_x = self.width // 2 - block_surface.get_width() // 2
                block_y = 50
                self.screen.blit(block_surface, (block_x, block_y))

        # 卡片网格
        self.render_card_grid(game)
        self.render_game_buttons(game)
        
        # 操作提示
        hint_text = "Use buttons: +5s | Block | Restart | Menu"
        if waiting_to_hide:
            hint_text += " | Processing..."
        
        hint_surface = self.small_font.render(hint_text, True, (100, 100, 100))
        hint_x = self.width - hint_surface.get_width() - 20
        hint_y = self.height - 40
        self.screen.blit(hint_surface, (hint_x, hint_y))
    
    def render_card_grid(self, game):
        grid_state = game.get_grid_state()
        rows, cols = game.rows, game.cols
        card_width, card_height, spacing, start_x, start_y = self._grid_layout(game)
        for r in range(rows):
            for c in range(cols):
                card_id, is_flipped, is_matched = grid_state[r][c]
                x = start_x + c * (card_width + spacing)
                y = start_y + r * (card_height + spacing)
                self.render_single_card(x, y, card_width, card_height, card_id, is_flipped, is_matched)

    def render_game_buttons(self, game):
        counts = game.get_item_counts() if hasattr(game, 'get_item_counts') else {"delay":0, "block":0}
        mouse_pos = pygame.mouse.get_pos()
        for key, rect in self.game_buttons.items():
            hover = rect.collidepoint(mouse_pos)
            bg = self.colors['button_hover'] if hover else self.colors['button']
            disabled = False
            label = ""
            if key == "delay":
                label = f"+5s ({counts.get('delay',0)})"
                disabled = counts.get('delay',0) <= 0
            elif key == "block":
                label = f"Block ({counts.get('block',0)})"
                disabled = counts.get('block',0) <= 0
            elif key == "restart":
                label = "Restart"
            elif key == "menu":
                label = "Menu"
            if disabled:
                bg = (160,160,160)
            pygame.draw.rect(self.screen, bg, rect, border_radius=10)
            pygame.draw.rect(self.screen, (50,50,50), rect, 2, border_radius=10)
            text_surface = self.menu_font.render(label, True, (255,255,255))
            text_rect = text_surface.get_rect(center=rect.center)
            self.screen.blit(text_surface, text_rect)
    
    def render_single_card(self, x, y, width, height, card_id, is_flipped, is_matched):
        """渲染单张卡片"""
        # 卡片颜色
        if is_matched:
            color = self.colors['matched']
        elif is_flipped:
            color = self.colors['card_front']
        else:
            color = self.colors['card_back']
        
        # 绘制卡片背景
        card_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, color, card_rect, border_radius=8)
        pygame.draw.rect(self.screen, (50, 50, 50), card_rect, 2, border_radius=8)
        
        text_surface = None
        if is_flipped or is_matched:
            if str(card_id) != "__SINGLE__":
                text_surface = self.card_font.render(str(card_id), True, (0, 0, 0))
        else:
            text_surface = self.card_font.render("?", True, (255, 255, 255))
        if text_surface:
            text_rect = text_surface.get_rect(center=(x + width//2, y + height//2))
            self.screen.blit(text_surface, text_rect)
    
    def render_victory_interface(self, game):
        """渲染胜利界面"""
        if not game:
            return
            
        # 半透明覆盖层
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        # 胜利消息框
        message_rect = pygame.Rect(200, 200, 600, 300)
        pygame.draw.rect(self.screen, (255, 255, 255), message_rect, border_radius=20)
        pygame.draw.rect(self.screen, (50, 50, 50), message_rect, 3, border_radius=20)
        
        # 胜利内容
        victory_text = self.title_font.render("🎉 You Won! 🎉", True, self.colors['victory'])
        score_text = self.menu_font.render(f"Final Score: {game.score}", True, (50, 50, 50))
        
        self.screen.blit(victory_text, (self.width//2 - victory_text.get_width()//2, 250))
        self.screen.blit(score_text, (self.width//2 - score_text.get_width()//2, 320))
        
        # 胜利按钮
        mouse_pos = pygame.mouse.get_pos()
        button_texts = ["Play Again", "Main Menu"]
        
        for i, (button_id, button_rect) in enumerate(self.victory_buttons.items()):
            # 按钮颜色
            if button_rect.collidepoint(mouse_pos):
                bg_color = self.colors['button_hover']
            else:
                bg_color = self.colors['button']
            
            # 绘制按钮
            pygame.draw.rect(self.screen, bg_color, button_rect, border_radius=10)
            pygame.draw.rect(self.screen, (50, 50, 50), button_rect, 2, border_radius=10)
            
            # 绘制按钮文字
            text_surface = self.menu_font.render(button_texts[i], True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=button_rect.center)
            self.screen.blit(text_surface, text_rect)
    
    def render_leaderboard_interface(self, leaderboard_data):
        """渲染排行榜界面"""
        # 绘制标题
        title_text = self.title_font.render("🏆 排行榜 🏆", True, self.colors['leaderboard_border'])
        title_rect = title_text.get_rect(center=(self.width // 2, 80))
        self.screen.blit(title_text, title_rect)
        
        # 绘制排行榜背景
        leaderboard_rect = pygame.Rect(150, 150, 700, 350)
        pygame.draw.rect(self.screen, self.colors['leaderboard_bg'], leaderboard_rect, border_radius=15)
        pygame.draw.rect(self.screen, self.colors['leaderboard_border'], leaderboard_rect, 3, border_radius=15)
        
        # 绘制排行榜头部
        header_font = self.menu_font
        headers = ["排名", "玩家", "时间", "步数", "模式"]
        header_widths = [60, 150, 150, 100, 120]
        
        header_start_x = 180
        header_y = 180
        
        for i, header in enumerate(headers):
            header_x = header_start_x + sum(header_widths[:i])
            header_surface = header_font.render(header, True, (50, 50, 150))
            self.screen.blit(header_surface, (header_x, header_y))
        
        # 绘制排行榜数据
        data_start_y = 220
        row_height = 30
        
        if hasattr(leaderboard_data, 'leaderboard_data') and leaderboard_data.leaderboard_data:
            leaderboard = leaderboard_data.leaderboard_data.get('leaderboard', [])
        else:
            leaderboard = []
        
        for i, entry in enumerate(leaderboard[:8]):  # 最多显示8条记录
            row_y = data_start_y + i * row_height
            rank_text = str(i + 1)
            username = entry.get('username', 'Unknown')
            time_str = f"{entry.get('time_seconds', 0)}s"
            steps = str(entry.get('steps', 0))
            game_mode = entry.get('game_mode', 'simple')
            
            rank_surface = self.small_font.render(rank_text, True, (0, 0, 0))
            username_surface = self.small_font.render(username, True, (0, 0, 0))
            time_surface = self.small_font.render(time_str, True, (0, 0, 0))
            steps_surface = self.small_font.render(steps, True, (0, 0, 0))
            mode_surface = self.small_font.render(game_mode, True, (0, 0, 0))
            
            # 绘制排名（使用颜色区分前三名）
            if i == 0:
                rank_color = (255, 215, 0)  # 金色
            elif i == 1:
                rank_color = (192, 192, 192)  # 银色
            elif i == 2:
                rank_color = (205, 127, 50)  # 铜色
            else:
                rank_color = (0, 0, 0)  # 黑色
            
            rank_surface = self.small_font.render(rank_text, True, rank_color)
            
            # 绘制数据
            row_start_x = 180
            self.screen.blit(rank_surface, (row_start_x, row_y))
            self.screen.blit(username_surface, (row_start_x + header_widths[0], row_y))
            self.screen.blit(time_surface, (row_start_x + header_widths[0] + header_widths[1], row_y))
            self.screen.blit(steps_surface, (row_start_x + header_widths[0] + header_widths[1] + header_widths[2], row_y))
            self.screen.blit(mode_surface, (row_start_x + header_widths[0] + header_widths[1] + header_widths[2] + header_widths[3], row_y))
        
        # 如果没有数据，显示提示信息
        if not leaderboard:
            no_data_text = self.menu_font.render("暂无排行榜数据", True, (100, 100, 100))
            no_data_rect = no_data_text.get_rect(center=(self.width // 2, 320))
            self.screen.blit(no_data_text, no_data_rect)
        
        # 绘制按钮
        mouse_pos = pygame.mouse.get_pos()
        for button_id, button_rect in self.leaderboard_buttons.items():
            # 按钮颜色
            if button_rect.collidepoint(mouse_pos):
                bg_color = self.colors['button_hover']
            else:
                bg_color = self.colors['button']
            
            # 绘制按钮
            pygame.draw.rect(self.screen, bg_color, button_rect, border_radius=10)
            pygame.draw.rect(self.screen, (50, 50, 50), button_rect, 2, border_radius=10)
            
            # 绘制按钮文字
            text_surface = self.menu_font.render(button_id, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=button_rect.center)
            self.screen.blit(text_surface, text_rect)
    
    def calculate_progress(self, game):
        """计算游戏进度"""
        total = game.rows * game.cols
        matched = 0
        
        for r in range(game.rows):
            for c in range(game.cols):
                card = game.get_card(r, c)
                if card.is_matched:
                    matched += 1
        
        return int((matched / total) * 100) if total > 0 else 0
    
    def get_menu_action(self, mouse_pos):
        """获取主菜单点击动作"""
        for button_id, rect in self.menu_buttons.items():
            if rect.collidepoint(mouse_pos):
                # 根据按钮文本映射到动作
                if button_id == "开始简单模式":
                    return "start_game"
                elif button_id == "开始困难模式":
                    return "hard_game"
                elif button_id == "排行榜":
                    return "leaderboard"
                elif button_id == "退出游戏":
                    return "exit"
        return None
    
    def get_victory_action(self, mouse_pos):
        """获取胜利界面点击动作"""
        for button_id, rect in self.victory_buttons.items():
            if rect.collidepoint(mouse_pos):
                return button_id
        return None

    def get_game_action(self, mouse_pos, game):
        for key, rect in self.game_buttons.items():
            if rect.collidepoint(mouse_pos):
                if key == "delay" and hasattr(game, 'get_item_counts') and game.get_item_counts().get('delay',0) <= 0:
                    return None
                if key == "block" and hasattr(game, 'get_item_counts') and game.get_item_counts().get('block',0) <= 0:
                    return None
                return key
        return None
    
    def get_card_position(self, mouse_pos, game):
        if not game:
            return None
        x, y = mouse_pos
        card_width, card_height, spacing, start_x, start_y = self._grid_layout(game)
        grid_width = game.cols * (card_width + spacing) - spacing
        grid_height = game.rows * (card_height + spacing) - spacing
        if not (start_x <= x <= start_x + grid_width and start_y <= y <= start_y + grid_height):
            return None
        col = (x - start_x) // (card_width + spacing)
        row = (y - start_y) // (card_height + spacing)
        if 0 <= row < game.rows and 0 <= col < game.cols:
            return (row, col)
        return None

    def _grid_layout(self, game):
        rows, cols = game.rows, game.cols
        spacing = 10
        hud_top = 150
        margin = 40
        available_w = self.width - 2 * margin
        available_h = self.height - hud_top - margin
        card_w_max = (available_w - (cols - 1) * spacing) // cols
        card_h_max = (available_h - (rows - 1) * spacing) // rows
        aspect = 1.25
        card_width = min(card_w_max, int(card_h_max / aspect))
        card_height = int(card_width * aspect)
        grid_width = cols * (card_width + spacing) - spacing
        grid_height = rows * (card_height + spacing) - spacing
        start_x = (self.width - grid_width) // 2
        start_y = hud_top + (available_h - grid_height) // 2
        return card_width, card_height, spacing, start_x, start_y

    def render_defeat_interface(self, game):
        if not game:
            return
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        message_rect = pygame.Rect(200, 200, 600, 300)
        pygame.draw.rect(self.screen, (255, 255, 255), message_rect, border_radius=20)
        pygame.draw.rect(self.screen, (50, 50, 50), message_rect, 3, border_radius=20)
        defeat_text = self.title_font.render("You Lost!", True, (200, 60, 60))
        score_text = self.menu_font.render(f"Final Score: {game.score}", True, (50, 50, 50))
        self.screen.blit(defeat_text, (self.width//2 - defeat_text.get_width()//2, 250))
        self.screen.blit(score_text, (self.width//2 - score_text.get_width()//2, 320))
        mouse_pos = pygame.mouse.get_pos()
        button_texts = ["Play Again", "Main Menu"]
        for i, (button_id, button_rect) in enumerate(self.victory_buttons.items()):
            if button_rect.collidepoint(mouse_pos):
                bg_color = self.colors['button_hover']
            else:
                bg_color = self.colors['button']
            pygame.draw.rect(self.screen, bg_color, button_rect, border_radius=10)
            pygame.draw.rect(self.screen, (50, 50, 50), button_rect, 2, border_radius=10)
            text_surface = self.menu_font.render(button_texts[i], True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=button_rect.center)
            self.screen.blit(text_surface, text_rect)

    def get_leaderboard_action(self, mouse_pos):
        """获取排行榜界面的点击动作"""
        for button_id, rect in self.leaderboard_buttons.items():
            if rect.collidepoint(mouse_pos):
                if button_id == "返回主菜单":
                    return "menu"
                elif button_id == "刷新排行榜":
                    return "refresh"
        return None