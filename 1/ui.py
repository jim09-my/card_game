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
        
        # 颜色配置
        self.colors = {
            'background': (240, 240, 245),
            'card_back': (70, 130, 180),
            'card_front': (255, 255, 255),
            'matched': (144, 238, 144),
            'text': (50, 50, 50),
            'button': (100, 150, 200),
            'button_hover': (120, 170, 220),
            'title': (30, 80, 150),
            'victory': (255, 215, 0)
        }
        
        # 字体初始化
        self.title_font = pygame.font.SysFont('arial', 48, bold=True)
        self.menu_font = pygame.font.SysFont('arial', 36)
        self.card_font = pygame.font.SysFont('arial', 32, bold=True)
        self.info_font = pygame.font.SysFont('arial', 24)
        self.small_font = pygame.font.SysFont('arial', 18)
        
        # 界面元素定义
        self.menu_buttons = {
            "start_game": pygame.Rect(400, 250, 200, 50),    # Simple Game
            "hard_game": pygame.Rect(400, 330, 200, 50),    # Hard Game
            "exit": pygame.Rect(400, 410, 200, 50)          # Exit
        }
        
        self.victory_buttons = {
            "restart": pygame.Rect(300, 400, 180, 50),     # Play Again
            "menu": pygame.Rect(520, 400, 180, 50)         # Main Menu
        }
    
    def render(self, game_state: str, current_game, waiting_to_hide: bool):
        """主渲染函数"""
        self.screen.fill(self.colors['background'])
        
        if game_state == "menu":
            self.render_main_menu()
        elif game_state == "game":
            self.render_game_interface(current_game, waiting_to_hide)
        elif game_state == "victory":
            self.render_victory_interface(current_game)
        
        pygame.display.flip()
    
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
        mode_text = "Mode: Simple"
        mode_surface = self.menu_font.render(mode_text, True, self.colors['title'])
        self.screen.blit(mode_surface, (50, 20))
        
        score_text = f"Score: {game.score}"
        score_surface = self.menu_font.render(score_text, True, self.colors['text'])
        self.screen.blit(score_surface, (50, 70))
        
        progress = self.calculate_progress(game)
        progress_text = f"Progress: {progress}%"
        progress_surface = self.menu_font.render(progress_text, True, self.colors['text'])
        self.screen.blit(progress_surface, (50, 120))
        
        # 卡片网格
        self.render_card_grid(game)
        
        # 操作提示
        hint_text = "ESC: Menu | R: Restart"
        if waiting_to_hide:
            hint_text += " | Processing..."
        
        hint_surface = self.small_font.render(hint_text, True, (100, 100, 100))
        hint_x = self.width - hint_surface.get_width() - 20
        hint_y = self.height - 40
        self.screen.blit(hint_surface, (hint_x, hint_y))
    
    def render_card_grid(self, game):
        """渲染卡片网格"""
        grid_state = game.get_grid_state()
        rows, cols = game.rows, game.cols
        
        # 布局参数
        card_width, card_height = 80, 100
        spacing = 15
        grid_width = cols * (card_width + spacing) - spacing
        grid_height = rows * (card_height + spacing) - spacing
        start_x = (self.width - grid_width) // 2
        start_y = 150
        
        # 绘制每张卡片
        for r in range(rows):
            for c in range(cols):
                card_id, is_flipped, is_matched = grid_state[r][c]
                x = start_x + c * (card_width + spacing)
                y = start_y + r * (card_height + spacing)
                self.render_single_card(x, y, card_width, card_height, 
                                     card_id, is_flipped, is_matched)
    
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
        
        # 卡片内容
        if is_flipped or is_matched:
            text = self.card_font.render(str(card_id), True, (0, 0, 0))
        else:
            text = self.card_font.render("?", True, (255, 255, 255))
        
        text_rect = text.get_rect(center=(x + width//2, y + height//2))
        self.screen.blit(text, text_rect)
    
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
        victory_text = self.title_font.render("🎉 You Win! 🎉", True, self.colors['victory'])
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
                return button_id
        return None
    
    def get_victory_action(self, mouse_pos):
        """获取胜利界面点击动作"""
        for button_id, rect in self.victory_buttons.items():
            if rect.collidepoint(mouse_pos):
                return button_id
        return None
    
    def get_card_position(self, mouse_pos, game):
        """获取点击的卡片位置"""
        if not game:
            return None
        
        x, y = mouse_pos
        
        # 布局参数
        card_width, card_height = 80, 100
        spacing = 15
        grid_width = game.cols * (card_width + spacing) - spacing
        grid_height = game.rows * (card_height + spacing) - spacing
        start_x = (self.width - grid_width) // 2
        start_y = 150
        
        # 检查网格范围
        if not (start_x <= x <= start_x + grid_width and
                start_y <= y <= start_y + grid_height):
            return None
        
        # 计算卡片位置
        col = (x - start_x) // (card_width + spacing)
        row = (y - start_y) // (card_height + spacing)
        
        if 0 <= row < game.rows and 0 <= col < game.cols:
            return (row, col)
        
        return None