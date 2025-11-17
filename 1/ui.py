import pygame
from typing import Tuple, Optional, List, Dict, Any

class GameUI:
    """游戏界面渲染器"""

    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        
        # 初始化字体系统
        pygame.font.init()
        self.title_font = pygame.font.Font(None, 72)
        self.menu_font = pygame.font.Font(None, 36)
        self.card_font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        self.button_font = pygame.font.Font(None, 28)
        self.input_font = pygame.font.Font(None, 18)
        
        # 【关键修复】加载中文字体，解决中文乱码问题
        self.message_font = pygame.font.Font(None, 36)
        self.chinese_font_path = self.find_chinese_font()
        if self.chinese_font_path:
            self.chinese_font = pygame.font.Font(self.chinese_font_path, 36)  # 用于渲染中文
            self.chinese_menu_font = pygame.font.Font(self.chinese_font_path, 36)
            self.chinese_button_font = pygame.font.Font(self.chinese_font_path, 28)
            self.chinese_title_font = pygame.font.Font(self.chinese_font_path, 72)
            self.chinese_small_font = pygame.font.Font(self.chinese_font_path, 20)
        else:
            # 如果找不到中文字体，回退到默认字体（可能乱码，但不会报错）
            self.chinese_font = pygame.font.Font(None, 36)
            self.chinese_menu_font = pygame.font.Font(None, 36)
            self.chinese_button_font = pygame.font.Font(None, 28)
            self.chinese_title_font = pygame.font.Font(None, 72)

        # 定义颜色方案
        self.colors = {
            'background': (135, 206, 235),         # 天蓝色背景
            'card_front': (255, 255, 255),         # 白色卡牌正面
            'card_back': (70, 130, 180),           # 蓝色卡牌背面
            'matched': (144, 238, 144),            # 浅绿色，配对成功
            'victory': (50, 205, 50),              # 绿色，胜利
            'defeat': (200, 60, 60),               # 红色，失败
            'button': (70, 130, 180),              # 蓝色按钮
            'button_hover': (100, 160, 210),       # 亮蓝色，按钮悬停
            'button_disabled': (160, 160, 160),    # 灰色，按钮禁用
            'text': (255, 255, 255),               # 白色文字
            'hud_bg': (255, 255, 255, 200),        # 半透明白色HUD背景
            'leaderboard_bg': (240, 248, 255),     # 淡蓝色背景
            'leaderboard_border': (100, 149, 237), # 蓝色边框
            'input_bg': (255, 255, 255),           # 白色输入框背景
            'input_border': (0, 0, 0),             # 黑色输入框边框
            'message_bg': (0, 0, 0, 180),          # 半透明黑色消息背景
            'message_text': (255, 255, 255),       # 白色消息文字
        }
        
        # 初始化按钮布局
        self.init_buttons()
        self.init_login_inputs()
        self.init_register_inputs()
        
        # 消息显示
        self.message = None
        self.message_timer = 0
        self.message_duration = 3000  # 消息显示持续时间（毫秒）
        
        # 输入框状态
        self.login_username = ""
        self.login_password = ""
        self.register_username = ""
        self.register_password = ""
        self.input_active = None  # 'login_username', 'login_password', 'register_username', 'register_password'
        self.input_text = ""

    def find_chinese_font(self):
        """尝试查找系统中常用的中文字体路径"""
        import os
        # 常见中文字体路径（Windows、macOS、Linux）
        possible_fonts = [
            "C:/Windows/Fonts/simhei.ttf",          # Windows 黑体
            "C:/Windows/Fonts/simsun.ttc",          # Windows 宋体
            "/System/Library/Fonts/PingFang.ttc",   # macOS 苹方
            "/System/Library/Fonts/STHeiti Light.ttc",  # macOS 华文黑体
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",  # Linux 文泉驿微米黑
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",  # Noto Sans CJK
        ]
        for font_path in possible_fonts:
            if os.path.exists(font_path):
                return font_path
        return None  # 找不到则返回 None

    def init_buttons(self):
        """初始化所有按钮的位置"""
        # 为已登录和未登录分别初始化按钮（使用 action id -> rect 映射，label 单独维护）
        button_width, button_height = 300, 56

        # 未登录 菜单（更少项，居中）
        self.menu_buttons_logged_out: Dict[str, pygame.Rect] = {}
        self.menu_labels_logged_out: Dict[str, str] = {}
        logged_out = [
            ("register", "注册"),
            ("login", "登录"),
            ("exit", "退出"),
        ]
        button_spacing = 14
        total_h = len(logged_out) * button_height + (len(logged_out) - 1) * button_spacing
        start_y = max(180, (self.height - total_h) // 2)
        for i, (action, label) in enumerate(logged_out):
            x = (self.width - button_width) // 2
            y = start_y + i * (button_height + button_spacing)
            rect = pygame.Rect(x, y, button_width, button_height)
            self.menu_buttons_logged_out[action] = rect
            self.menu_labels_logged_out[action] = label

        # 已登录 主菜单（更多项，稍微靠上）
        self.menu_buttons_logged_in: Dict[str, pygame.Rect] = {}
        self.menu_labels_logged_in: Dict[str, str] = {}
        logged_in = [
            ("start_game", "开始简单模式"),
            ("hard_game", "开始困难模式"),
            ("leaderboard", "排行榜"),
            ("shop", "商城"),
            ("history", "历史记录"),
            ("exit", "退出游戏"),
        ]
        button_spacing = 12
        total_h = len(logged_in) * button_height + (len(logged_in) - 1) * button_spacing
        start_y = 220
        for i, (action, label) in enumerate(logged_in):
            x = (self.width - button_width) // 2
            y = start_y + i * (button_height + button_spacing)
            rect = pygame.Rect(x, y, button_width, button_height)
            self.menu_buttons_logged_in[action] = rect
            self.menu_labels_logged_in[action] = label

    def init_login_inputs(self):
        """初始化登录输入框和按钮"""
        # 输入框
        self.login_username_input = pygame.Rect((self.width - 300) // 2, 300, 300, 40)
        self.login_password_input = pygame.Rect((self.width - 300) // 2, 360, 300, 40)
        # 按钮 - 修复位置计算，使按钮更大更容易点击
        button_width, button_height = 120, 45
        button_spacing = 15
        total_buttons_width = button_width * 2 + button_spacing
        start_x = (self.width - total_buttons_width) // 2
        self.login_buttons = {
            "login": pygame.Rect(start_x, 420, button_width, button_height),
            "back": pygame.Rect(start_x + button_width + button_spacing, 420, button_width, button_height)
        }

    def init_register_inputs(self):
        """初始化注册输入框和按钮（简化版，无邮箱）"""
        # 输入框（移除邮箱输入框）
        self.register_username_input = pygame.Rect((self.width - 300) // 2, 300, 300, 40)
        self.register_password_input = pygame.Rect((self.width - 300) // 2, 360, 300, 40)
        # 按钮 - 修复位置计算，使按钮更大更容易点击
        button_width, button_height = 120, 45
        button_spacing = 15
        total_buttons_width = button_width * 2 + button_spacing
        start_x = (self.width - total_buttons_width) // 2
        self.register_buttons = {
            "register": pygame.Rect(start_x, 420, button_width, button_height),
            "back": pygame.Rect(start_x + button_width + button_spacing, 420, button_width, button_height)
        }

    def reset_login_inputs(self):
        """重置登录输入"""
        self.login_username = ""
        self.login_password = ""
        self.input_text = ""
        self.input_active = None

    def reset_register_inputs(self):
        """重置注册输入（简化版，无邮箱）"""
        self.register_username = ""
        self.register_password = ""
        self.input_text = ""
        self.input_active = None

    def get_menu_action(self, mouse_pos, user_logged_in: bool = False):
        """获取主菜单点击动作，根据登录状态返回对应 action id"""
        if user_logged_in:
            for action_id, button_rect in self.menu_buttons_logged_in.items():
                if button_rect.collidepoint(mouse_pos):
                    return action_id
        else:
            for action_id, button_rect in self.menu_buttons_logged_out.items():
                if button_rect.collidepoint(mouse_pos):
                    return action_id
        return None

    def get_login_action(self, mouse_pos):
        """获取登录界面点击动作"""
        for button_id, button_rect in self.login_buttons.items():
            if button_rect.collidepoint(mouse_pos):
                return button_id
        return None

    def get_register_action(self, mouse_pos):
        """获取注册界面点击动作"""
        for button_id, button_rect in self.register_buttons.items():
            if button_rect.collidepoint(mouse_pos):
                return button_id
        return None

    def get_shop_action(self, mouse_pos):
        """获取商城界面点击动作"""
        buy_delay_button = pygame.Rect((self.width - 200) // 2, 220, 200, 60)
        buy_block_button = pygame.Rect((self.width - 200) // 2, 300, 200, 60)
        buy_reveal_button = pygame.Rect((self.width - 200) // 2, 380, 200, 60)
        back_button = pygame.Rect((self.width - 150) // 2, 460, 150, 40)
        
        if buy_delay_button.collidepoint(mouse_pos):
            return "buy_delay"
        elif buy_block_button.collidepoint(mouse_pos):
            return "buy_block"
        elif buy_reveal_button.collidepoint(mouse_pos):
            return "buy_reveal"
        elif back_button.collidepoint(mouse_pos):
            return "back"
        return None

    def get_history_action(self, mouse_pos):
        """获取历史记录界面点击动作"""
        back_button = pygame.Rect((self.width - 150) // 2, 420, 150, 40)
        if back_button.collidepoint(mouse_pos):
            return "back"
        return None

    def get_game_action(self, mouse_pos, current_game):
        """获取游戏界面点击动作（按钮检测）"""
        # 注意：这个方法只检测按钮，不检测卡牌
        # 按钮位置需要与render_game_interface中的位置一致
        # 由于按钮位置是动态计算的，我们需要重新计算
        
        # 计算按钮位置（与render_game_interface中的逻辑完全一致）
        button_y = 500  # 默认位置
        if current_game and hasattr(current_game, 'get_grid_state'):
            grid_state = current_game.get_grid_state()
            rows = len(grid_state)
            cols = len(grid_state[0]) if rows > 0 else 0
            
            # 使用与render_game_interface相同的卡牌尺寸计算
            if rows <= 4 and cols <= 4:
                card_width, card_height = 100, 120
                spacing = 15
            else:
                card_width, card_height = 60, 80
                spacing = 8
            
            # 计算总宽度和起始位置，确保居中（与render_game_interface一致）
            total_width = cols * (card_width + spacing) - spacing
            total_height = rows * (card_height + spacing) - spacing
            start_x = (self.width - total_width) // 2
            start_y = 100  # HUD下方
            
            # 确保不会超出屏幕（与render_game_interface一致）
            max_y = start_y + total_height
            if max_y > self.height - 120:  # 留出按钮空间
                # 如果超出，缩小卡牌尺寸
                scale = (self.height - 120 - start_y) / total_height
                card_width = int(card_width * scale)
                card_height = int(card_height * scale)
                spacing = int(spacing * scale)
                total_width = cols * (card_width + spacing) - spacing
                start_x = (self.width - total_width) // 2
                total_height = rows * (card_height + spacing) - spacing
            
            # 计算按钮位置，确保在卡牌网格下方（与render_game_interface一致）
            grid_bottom = start_y + rows * (card_height + spacing) - spacing
            button_y = grid_bottom + 20
            # 确保按钮不会超出屏幕
            if button_y > self.height - 50:
                button_y = self.height - 50
        
        # 按钮位置（与render_game_interface一致）
        delay_button = pygame.Rect(50, button_y, 100, 40)
        block_button = pygame.Rect(160, button_y, 100, 40)
        restart_button = pygame.Rect(270, button_y, 100, 40)
        menu_button = pygame.Rect(380, button_y, 100, 40)
        
        print(f"道具按钮检测 - 鼠标位置: {mouse_pos}")
        print(f"延时按钮区域: {delay_button}, 阻挡按钮区域: {block_button}")
        print(f"延时按钮碰撞: {delay_button.collidepoint(mouse_pos)}, 阻挡按钮碰撞: {block_button.collidepoint(mouse_pos)}")
        
        if delay_button.collidepoint(mouse_pos):
            print("检测到延时按钮点击")
            return "delay"
        elif block_button.collidepoint(mouse_pos):
            print("检测到阻挡按钮点击")
            return "block"
        elif restart_button.collidepoint(mouse_pos):
            return "restart"
        elif menu_button.collidepoint(mouse_pos):
            return "menu"
        return None

    def get_victory_action(self, mouse_pos):
        """获取胜利界面点击动作"""
        restart_button = pygame.Rect(300, 300, 150, 40)
        menu_button = pygame.Rect(500, 300, 150, 40)
        if restart_button.collidepoint(mouse_pos):
            return "restart"
        elif menu_button.collidepoint(mouse_pos):
            return "menu"
        return None

    def get_defeat_action(self, mouse_pos):
        """获取失败界面点击动作"""
        restart_button = pygame.Rect(300, 300, 150, 40)
        menu_button = pygame.Rect(500, 300, 150, 40)
        if restart_button.collidepoint(mouse_pos):
            return "restart"
        elif menu_button.collidepoint(mouse_pos):
            return "menu"
        return None

    def get_leaderboard_action(self, mouse_pos):
        """获取排行榜界面点击动作"""
        back_button = pygame.Rect(400, 420, 150, 40)
        refresh_button = pygame.Rect(200, 420, 150, 40)
        if back_button.collidepoint(mouse_pos):
            return "back"
        elif refresh_button.collidepoint(mouse_pos):
            return "refresh"
        return None

    def get_login_username(self):
        """获取登录用户名"""
        return self.login_username

    def get_login_password(self):
        """获取登录密码"""
        return self.login_password

    def get_register_username(self):
        """获取注册用户名"""
        return self.register_username

    def get_register_password(self):
        """获取注册密码"""
        return self.register_password
    

    def render(self, game_state: str, current_game, waiting_to_hide: bool, elapsed_time: int, step_count: int, points: int, user_logged_in: bool, username: str, user_items=None):
        """根据游戏状态渲染界面"""
        self.screen.fill(self.colors['background'])

        if game_state == "menu":
            self.render_menu(user_logged_in)
        elif game_state == "login":
            self.render_login_interface()
        elif game_state == "register":
            self.render_register_interface()
        elif game_state == "shop":
            self.render_shop_interface(points, user_items)
        elif game_state == "history":
            self.render_history_interface([])
        elif game_state == "game":
            self.render_game_interface(current_game, waiting_to_hide, elapsed_time, step_count, points)
        elif game_state == "victory":
            self.render_game_interface(current_game, waiting_to_hide, elapsed_time, step_count, points)
            # 获取积分信息（从游戏对象或传入参数）
            points_earned = getattr(current_game, 'points_earned', 0) if current_game else 0
            self.render_victory_interface(points_earned, points)
        elif game_state == "defeat":
            self.render_game_interface(current_game, waiting_to_hide, elapsed_time, step_count, points)
            self.render_defeat_interface()
        elif game_state == "leaderboard":
            self.render_leaderboard_interface({})

        # 显示消息（检查是否超时）
        if self.message:
            current_time = pygame.time.get_ticks()
            if current_time - self.message_timer < self.message_duration:
                self.render_message(self.message)
            else:
                self.message = None  # 消息超时，清除

        pygame.display.flip()

    def render_menu(self, user_logged_in: bool = False):
        """渲染主菜单界面，根据登录状态显示不同按钮"""
        # 绘制标题
        title_text = self.chinese_title_font.render("*记忆迷宫*", True, (50, 50, 150))
        title_rect = title_text.get_rect(center=(self.width // 2, 150))
        self.screen.blit(title_text, title_rect)

        # 绘制按钮（根据登录状态选择集合）
        mouse_pos = pygame.mouse.get_pos()
        if user_logged_in:
            buttons = self.menu_buttons_logged_in
            labels = self.menu_labels_logged_in
        else:
            buttons = self.menu_buttons_logged_out
            labels = self.menu_labels_logged_out

        for action_id, button_rect in buttons.items():
            if button_rect.collidepoint(mouse_pos):
                bg_color = self.colors['button_hover']
            else:
                bg_color = self.colors['button']
            pygame.draw.rect(self.screen, bg_color, button_rect, border_radius=10)
            pygame.draw.rect(self.screen, (50, 50, 50), button_rect, 2, border_radius=10)
            label = labels.get(action_id, action_id)
            text_surface = self.chinese_button_font.render(label, True, self.colors['text'])
            text_rect = text_surface.get_rect(center=button_rect.center)
            self.screen.blit(text_surface, text_rect)

    def render_login_interface(self):
        """渲染登录界面"""
        self.screen.fill(self.colors['background'])
        # 绘制标题
        title_text = self.chinese_title_font.render("登录", True, (50, 50, 150))
        title_rect = title_text.get_rect(center=(self.width // 2, 200))
        self.screen.blit(title_text, title_rect)
        # 将标签与输入框放在同一水平线上
        input_w, input_h = 260, 40
        gap = 20  # 增加间距，让输入框向右移动

        # 用户名行
        username_y = 300
        username_label_surf = self.chinese_small_font.render("用户名:", True, self.colors['text'])
        label_w, label_h = self.input_font.size("用户名:")
        total_w = label_w + gap + input_w
        start_x = (self.width - total_w) // 2
        label_x = start_x
        label_y = username_y + (input_h - label_h) // 2
        self.screen.blit(username_label_surf, (label_x, label_y))
        self.login_username_input = pygame.Rect(start_x + label_w + gap, username_y, input_w, input_h)
        # 绘制输入框，如果激活则高亮边框
        border_color = (100, 200, 255) if self.input_active == 'login_username' else self.colors['input_border']
        pygame.draw.rect(self.screen, self.colors['input_bg'], self.login_username_input)
        pygame.draw.rect(self.screen, border_color, self.login_username_input, 3 if self.input_active == 'login_username' else 2)
        # 显示输入的文字
        if self.login_username:
            # 截断文字以适应输入框宽度
            max_width = self.login_username_input.width - 10
            display_text = self.login_username
            text_width, _ = self.input_font.size(display_text)
            if text_width > max_width:
                # 如果文字太长，从末尾截断并显示省略号
                while text_width > max_width - 20 and len(display_text) > 0:
                    display_text = display_text[1:]
                    text_width, _ = self.input_font.size("..." + display_text)
                display_text = "..." + display_text
            text_surface = self.input_font.render(display_text, True, (0, 0, 0))
            text_rect = text_surface.get_rect(midleft=(self.login_username_input.x + 5, self.login_username_input.centery))
            self.screen.blit(text_surface, text_rect)

        # 密码行
        password_y = username_y + 60
        password_label_surf = self.chinese_small_font.render("密码:", True, self.colors['text'])
        label_w2, label_h2 = self.input_font.size("密码:")
        label_x2 = start_x
        label_y2 = password_y + (input_h - label_h2) // 2
        self.screen.blit(password_label_surf, (label_x2, label_y2))
        self.login_password_input = pygame.Rect(start_x + label_w + gap, password_y, input_w, input_h)
        # 绘制输入框，如果激活则高亮边框
        border_color = (100, 200, 255) if self.input_active == 'login_password' else self.colors['input_border']
        pygame.draw.rect(self.screen, self.colors['input_bg'], self.login_password_input)
        pygame.draw.rect(self.screen, border_color, self.login_password_input, 3 if self.input_active == 'login_password' else 2)
        # 显示密码（用星号代替）
        if self.login_password:
            password_display = '*' * len(self.login_password)
            # 截断文字以适应输入框宽度
            max_width = self.login_password_input.width - 10
            text_width, _ = self.input_font.size(password_display)
            if text_width > max_width:
                # 如果文字太长，从末尾截断
                while text_width > max_width - 20 and len(password_display) > 0:
                    password_display = password_display[1:]
                    text_width, _ = self.input_font.size("..." + password_display)
                password_display = "..." + password_display
            text_surface = self.input_font.render(password_display, True, (0, 0, 0))
            text_rect = text_surface.get_rect(midleft=(self.login_password_input.x + 5, self.login_password_input.centery))
            self.screen.blit(text_surface, text_rect)
        
        # 按钮
        mouse_pos = pygame.mouse.get_pos()
        for button_id, button_rect in self.login_buttons.items():
            if button_rect.collidepoint(mouse_pos):
                bg_color = self.colors['button_hover']
            else:
                bg_color = self.colors['button']
            pygame.draw.rect(self.screen, bg_color, button_rect, border_radius=10)
            pygame.draw.rect(self.screen, (50, 50, 50), button_rect, 2, border_radius=10)
            button_label = "登录" if button_id == "login" else "返回"
            text_surface = self.chinese_button_font.render(button_label, True, self.colors['text'])
            text_rect = text_surface.get_rect(center=button_rect.center)
            self.screen.blit(text_surface, text_rect)

    def render_register_interface(self):
        """渲染注册界面"""
        self.screen.fill(self.colors['background'])
        
        # 绘制标题
        title_text = self.chinese_title_font.render("注册", True, (50, 50, 150))
        title_rect = title_text.get_rect(center=(self.width // 2, 200))
        self.screen.blit(title_text, title_rect)
        
        # 将标签与输入框放在同一水平线上
        input_w, input_h = 260, 40
        gap = 20  # 增加间距，让输入框向右移动

        # 用户名行
        username_y = 300
        username_label_surf = self.chinese_small_font.render("用户名:", True, self.colors['text'])
        label_w, label_h = self.input_font.size("用户名:")
        total_w = label_w + gap + input_w
        start_x = (self.width - total_w) // 2
        label_x = start_x
        label_y = username_y + (input_h - label_h) // 2
        self.screen.blit(username_label_surf, (label_x, label_y))
        self.register_username_input = pygame.Rect(start_x + label_w + gap, username_y, input_w, input_h)
        # 绘制输入框，如果激活则高亮边框
        border_color = (100, 200, 255) if self.input_active == 'register_username' else self.colors['input_border']
        pygame.draw.rect(self.screen, self.colors['input_bg'], self.register_username_input)
        pygame.draw.rect(self.screen, border_color, self.register_username_input, 3 if self.input_active == 'register_username' else 2)
        # 显示输入的文字
        if self.register_username:
            # 截断文字以适应输入框宽度
            max_width = self.register_username_input.width - 10
            display_text = self.register_username
            text_width, _ = self.input_font.size(display_text)
            if text_width > max_width:
                # 如果文字太长，从末尾截断并显示省略号
                while text_width > max_width - 20 and len(display_text) > 0:
                    display_text = display_text[1:]
                    text_width, _ = self.input_font.size("..." + display_text)
                display_text = "..." + display_text
            text_surface = self.input_font.render(display_text, True, (0, 0, 0))
            text_rect = text_surface.get_rect(midleft=(self.register_username_input.x + 5, self.register_username_input.centery))
            self.screen.blit(text_surface, text_rect)

        # 密码行（移除邮箱行）
        password_y = username_y + 60
        password_label_surf = self.chinese_small_font.render("密码:", True, self.colors['text'])
        label_w2, label_h2 = self.input_font.size("密码:")
        label_x2 = start_x
        label_y2 = password_y + (input_h - label_h2) // 2
        self.screen.blit(password_label_surf, (label_x2, label_y2))
        self.register_password_input = pygame.Rect(start_x + label_w + gap, password_y, input_w, input_h)
        # 绘制输入框，如果激活则高亮边框
        border_color = (100, 200, 255) if self.input_active == 'register_password' else self.colors['input_border']
        pygame.draw.rect(self.screen, self.colors['input_bg'], self.register_password_input)
        pygame.draw.rect(self.screen, border_color, self.register_password_input, 3 if self.input_active == 'register_password' else 2)
        # 显示密码（用星号代替）
        if self.register_password:
            password_display = '*' * len(self.register_password)
            # 截断文字以适应输入框宽度
            max_width = self.register_password_input.width - 10
            text_width, _ = self.input_font.size(password_display)
            if text_width > max_width:
                # 如果文字太长，从末尾截断
                while text_width > max_width - 20 and len(password_display) > 0:
                    password_display = password_display[1:]
                    text_width, _ = self.input_font.size("..." + password_display)
                password_display = "..." + password_display
            text_surface = self.input_font.render(password_display, True, (0, 0, 0))
            text_rect = text_surface.get_rect(midleft=(self.register_password_input.x + 5, self.register_password_input.centery))
            self.screen.blit(text_surface, text_rect)
        
        # 按钮
        mouse_pos = pygame.mouse.get_pos()
        for button_id, button_rect in self.register_buttons.items():
            if button_rect.collidepoint(mouse_pos):
                bg_color = self.colors['button_hover']
            else:
                bg_color = self.colors['button']
            pygame.draw.rect(self.screen, bg_color, button_rect, border_radius=10)
            pygame.draw.rect(self.screen, (50, 50, 50), button_rect, 2, border_radius=10)
            button_label = "注册" if button_id == "register" else "返回"
            text_surface = self.chinese_button_font.render(button_label, True, self.colors['text'])
            text_rect = text_surface.get_rect(center=button_rect.center)
            self.screen.blit(text_surface, text_rect)

    def render_shop_interface(self, points=0, user_items=None):
        """渲染商城界面"""
        self.screen.fill(self.colors['background'])
        
        # 绘制标题
        title_text = self.chinese_title_font.render("商城", True, (50, 50, 150))
        title_rect = title_text.get_rect(center=(self.width // 2, 100))
        self.screen.blit(title_text, title_rect)
        
        # 显示用户当前积分
        points_text = self.chinese_font.render(f"当前积分: {points}", True, (50, 150, 50))
        points_rect = points_text.get_rect(center=(self.width // 2, 150))
        self.screen.blit(points_text, points_rect)
        
        # 道具价格信息
        item_costs = {
            "delay": {"name": "延时道具", "cost": 10, "desc": "增加30秒游戏时间"},
            "block": {"name": "阻挡道具", "cost": 15, "desc": "冻结对手5秒"},
            "reveal": {"name": "翻牌道具", "cost": 20, "desc": "直接翻开一张卡片"}
        }
        
        # 获取道具数量
        if user_items is None:
            user_items = {"delay": 0, "block": 0, "reveal": 0}
        
        # 按钮
        mouse_pos = pygame.mouse.get_pos()
        buy_delay_button = pygame.Rect((self.width - 200) // 2, 220, 200, 60)
        buy_block_button = pygame.Rect((self.width - 200) // 2, 300, 200, 60)
        buy_reveal_button = pygame.Rect((self.width - 200) // 2, 380, 200, 60)
        back_button = pygame.Rect((self.width - 150) // 2, 460, 150, 40)
        
        # 延时道具按钮
        if buy_delay_button.collidepoint(mouse_pos):
            bg_color = self.colors['button_hover']
        else:
            bg_color = self.colors['button']
        pygame.draw.rect(self.screen, bg_color, buy_delay_button, border_radius=10)
        pygame.draw.rect(self.screen, (50, 50, 50), buy_delay_button, 2, border_radius=10)
        delay_text = self.chinese_button_font.render(f"延时道具 ({item_costs['delay']['cost']}积分)", True, self.colors['text'])
        delay_rect = delay_text.get_rect(center=(buy_delay_button.centerx, buy_delay_button.y + 15))
        self.screen.blit(delay_text, delay_rect)
        delay_desc = self.menu_font.render(f"{item_costs['delay']['desc']} | 拥有: {user_items.get('delay', 0)}", True, (100, 100, 100))
        delay_desc_rect = delay_desc.get_rect(center=(buy_delay_button.centerx, buy_delay_button.y + 40))
        self.screen.blit(delay_desc, delay_desc_rect)
        
        # 阻挡道具按钮
        if buy_block_button.collidepoint(mouse_pos):
            bg_color = self.colors['button_hover']
        else:
            bg_color = self.colors['button']
        pygame.draw.rect(self.screen, bg_color, buy_block_button, border_radius=10)
        pygame.draw.rect(self.screen, (50, 50, 50), buy_block_button, 2, border_radius=10)
        block_text = self.chinese_button_font.render(f"阻挡道具 ({item_costs['block']['cost']}积分)", True, self.colors['text'])
        block_rect = block_text.get_rect(center=(buy_block_button.centerx, buy_block_button.y + 15))
        self.screen.blit(block_text, block_rect)
        block_desc = self.menu_font.render(f"{item_costs['block']['desc']} | 拥有: {user_items.get('block', 0)}", True, (100, 100, 100))
        block_desc_rect = block_desc.get_rect(center=(buy_block_button.centerx, buy_block_button.y + 40))
        self.screen.blit(block_desc, block_desc_rect)
        
        # 翻牌道具按钮
        if buy_reveal_button.collidepoint(mouse_pos):
            bg_color = self.colors['button_hover']
        else:
            bg_color = self.colors['button']
        pygame.draw.rect(self.screen, bg_color, buy_reveal_button, border_radius=10)
        pygame.draw.rect(self.screen, (50, 50, 50), buy_reveal_button, 2, border_radius=10)
        reveal_text = self.chinese_button_font.render(f"翻牌道具 ({item_costs['reveal']['cost']}积分)", True, self.colors['text'])
        reveal_rect = reveal_text.get_rect(center=(buy_reveal_button.centerx, buy_reveal_button.y + 15))
        self.screen.blit(reveal_text, reveal_rect)
        reveal_desc = self.menu_font.render(f"{item_costs['reveal']['desc']} | 拥有: {user_items.get('reveal', 0)}", True, (100, 100, 100))
        reveal_desc_rect = reveal_desc.get_rect(center=(buy_reveal_button.centerx, buy_reveal_button.y + 40))
        self.screen.blit(reveal_desc, reveal_desc_rect)
        
        # 返回按钮
        if back_button.collidepoint(mouse_pos):
            bg_color = self.colors['button_hover']
        else:
            bg_color = self.colors['button']
        pygame.draw.rect(self.screen, bg_color, back_button, border_radius=10)
        pygame.draw.rect(self.screen, (50, 50, 50), back_button, 2, border_radius=10)
        back_text = self.chinese_button_font.render("返回", True, self.colors['text'])
        back_rect = back_text.get_rect(center=back_button.center)
        self.screen.blit(back_text, back_rect)

    def render_history_interface(self, history_data):
        """渲染历史记录界面"""
        self.screen.fill(self.colors['background'])
        # 绘制标题
        title_text = self.chinese_title_font.render("历史记录", True, (50, 50, 150))
        title_rect = title_text.get_rect(center=(self.width // 2, 200))
        self.screen.blit(title_text, title_rect)
        # 提示无数据
        no_data_text = self.menu_font.render("暂无历史记录", True, self.colors['text'])
        no_data_rect = no_data_text.get_rect(center=(self.width // 2, 400))
        self.screen.blit(no_data_text, no_data_rect)
        # 返回按钮
        back_button = pygame.Rect((self.width - 150) // 2, 460, 150, 40)
        mouse_pos = pygame.mouse.get_pos()
        if back_button.collidepoint(mouse_pos):
            bg_color = self.colors['button_hover']
        else:
            bg_color = self.colors['button']
        pygame.draw.rect(self.screen, bg_color, back_button, border_radius=10)
        pygame.draw.rect(self.screen, (50, 50, 50), back_button, 2, border_radius=10)
        back_text = self.chinese_button_font.render("返回", True, self.colors['text'])
        back_rect = back_text.get_rect(center=back_button.center)
        self.screen.blit(back_text, back_rect)

    def render_game_interface(self, current_game, waiting_to_hide: bool, elapsed_time: int, step_count: int, points: int):
        """渲染游戏界面，包括计时器、步数、卡牌等"""
        # 绘制背景
        self.screen.fill(self.colors['background'])
        # 绘制HUD（计时器、步数、积分）
        hud_y = 20
        
        # 检查是否是困难模式，如果是则显示剩余时间
        if hasattr(current_game, 'get_remaining_time_ms'):
            remaining_time_ms = current_game.get_remaining_time_ms()
            remaining_time_sec = remaining_time_ms // 1000
            timer_text = self.menu_font.render(f"剩余时间: {remaining_time_sec} 秒", True, self.colors['text'])
        else:
            # 简单模式显示已用时间
            timer_text = self.menu_font.render(f"时间: {elapsed_time} 秒", True, self.colors['text'])
        
        self.screen.blit(timer_text, (50, hud_y))
        steps_text = self.menu_font.render(f"步数: {step_count}", True, self.colors['text'])
        self.screen.blit(steps_text, (250, hud_y))
        points_text = self.menu_font.render(f"积分: {points}", True, self.colors['text'])
        self.screen.blit(points_text, (450, hud_y))
        # 渲染卡牌网格
        if hasattr(current_game, 'get_grid_state'):
            grid_state = current_game.get_grid_state()
            rows = len(grid_state)
            cols = len(grid_state[0]) if rows > 0 else 0
            
            # 根据网格大小调整卡牌尺寸，确保界面美观
            if rows <= 4 and cols <= 4:
                # 简单模式：4x4，使用较大的卡牌
                card_width, card_height = 100, 120
                spacing = 15
            else:
                # 困难模式：7x7，使用较小的卡牌
                card_width, card_height = 60, 80
                spacing = 8
            
            # 计算总宽度和起始位置，确保居中
            total_width = cols * (card_width + spacing) - spacing
            total_height = rows * (card_height + spacing) - spacing
            start_x = (self.width - total_width) // 2
            start_y = 100  # HUD下方
            
            # 确保不会超出屏幕
            max_y = start_y + total_height
            if max_y > self.height - 120:  # 留出按钮空间
                # 如果超出，缩小卡牌尺寸
                scale = (self.height - 120 - start_y) / total_height
                card_width = int(card_width * scale)
                card_height = int(card_height * scale)
                spacing = int(spacing * scale)
                total_width = cols * (card_width + spacing) - spacing
                start_x = (self.width - total_width) // 2
            
            for r in range(rows):
                for c in range(cols):
                    card_id, is_flipped, is_matched = grid_state[r][c]
                    x = start_x + c * (card_width + spacing)
                    y = start_y + r * (card_height + spacing)
                    self.render_single_card(x, y, card_width, card_height, card_id, is_flipped, is_matched)
            
            # 计算按钮位置，确保在卡牌网格下方
            grid_bottom = start_y + rows * (card_height + spacing) - spacing
            button_y = grid_bottom + 20
            # 确保按钮不会超出屏幕
            if button_y > self.height - 50:
                button_y = self.height - 50
        else:
            button_y = 500
        
        # 渲染游戏按钮
        delay_button = pygame.Rect(50, button_y, 100, 40)
        block_button = pygame.Rect(160, button_y, 100, 40)
        restart_button = pygame.Rect(270, button_y, 100, 40)
        menu_button = pygame.Rect(380, button_y, 100, 40)
        mouse_pos = pygame.mouse.get_pos()
        
        # 获取道具数量（仅困难模式显示）
        delay_count = 0
        block_count = 0
        if hasattr(current_game, 'get_item_counts'):
            counts = current_game.get_item_counts()
            delay_count = counts.get('delay', 0)
            block_count = counts.get('block', 0)
        
        # 延时按钮
        if delay_button.collidepoint(mouse_pos):
            bg_color = self.colors['button_hover']
        else:
            bg_color = self.colors['button']
        pygame.draw.rect(self.screen, bg_color, delay_button, border_radius=10)
        pygame.draw.rect(self.screen, (50, 50, 50), delay_button, 2, border_radius=10)
        delay_text = self.chinese_button_font.render(f"延时({delay_count})", True, self.colors['text'])
        delay_rect = delay_text.get_rect(center=delay_button.center)
        self.screen.blit(delay_text, delay_rect)
        
        # 阻挡按钮
        if block_button.collidepoint(mouse_pos):
            bg_color = self.colors['button_hover']
        else:
            bg_color = self.colors['button']
        pygame.draw.rect(self.screen, bg_color, block_button, border_radius=10)
        pygame.draw.rect(self.screen, (50, 50, 50), block_button, 2, border_radius=10)
        block_text = self.chinese_button_font.render(f"阻挡({block_count})", True, self.colors['text'])
        block_rect = block_text.get_rect(center=block_button.center)
        self.screen.blit(block_text, block_rect)
        if restart_button.collidepoint(mouse_pos):
            bg_color = self.colors['button_hover']
        else:
            bg_color = self.colors['button']
        pygame.draw.rect(self.screen, bg_color, restart_button, border_radius=10)
        pygame.draw.rect(self.screen, (50, 50, 50), restart_button, 2, border_radius=10)
        restart_text = self.chinese_button_font.render("重启", True, self.colors['text'])
        restart_rect = restart_text.get_rect(center=restart_button.center)
        self.screen.blit(restart_text, restart_rect)
        if menu_button.collidepoint(mouse_pos):
            bg_color = self.colors['button_hover']
        else:
            bg_color = self.colors['button']
        pygame.draw.rect(self.screen, bg_color, menu_button, border_radius=10)
        pygame.draw.rect(self.screen, (50, 50, 50), menu_button, 2, border_radius=10)
        menu_text = self.chinese_button_font.render("菜单", True, self.colors['text'])
        menu_rect = menu_text.get_rect(center=menu_button.center)
        self.screen.blit(menu_text, menu_rect)

    def render_single_card(self, x, y, width, height, card_id, is_flipped, is_matched):
        """渲染单张卡牌"""
        if is_matched:
            color = self.colors['matched']
        elif is_flipped:
            color = self.colors['card_front']
        else:
            color = self.colors['card_back']
        # 绘制卡牌背景
        pygame.draw.rect(self.screen, color, (x, y, width, height), border_radius=8)
        pygame.draw.rect(self.screen, (50, 50, 50), (x, y, width, height), 2, border_radius=8)
        # 如果卡牌翻开且未匹配，显示卡牌ID
        if is_flipped and not is_matched:
            card_text = self.card_font.render(str(card_id), True, (0, 0, 0))
            text_rect = card_text.get_rect(center=(x + width // 2, y + height // 2))
            self.screen.blit(card_text, text_rect)
        elif is_matched:
            matched_text = self.card_font.render("✓", True, (0, 0, 0))
            text_rect = matched_text.get_rect(center=(x + width // 2, y + height // 2))
            self.screen.blit(matched_text, text_rect)

    def render_victory_interface(self, points_earned=0, total_points=0):
        """渲染胜利界面"""
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        victory_text = self.chinese_title_font.render("🎉 恭喜胜利！ 🎉", True, self.colors['victory'])
        victory_rect = victory_text.get_rect(center=(self.width // 2, 200))
        self.screen.blit(victory_text, victory_rect)
        
        # 显示积分奖励信息
        if points_earned > 0:
            reward_text = self.chinese_font.render(f"获得 {points_earned} 积分！", True, self.colors['text'])
            reward_rect = reward_text.get_rect(center=(self.width // 2, 250))
            self.screen.blit(reward_text, reward_rect)
            
            total_text = self.chinese_font.render(f"当前总积分: {total_points}", True, self.colors['text'])
            total_rect = total_text.get_rect(center=(self.width // 2, 280))
            self.screen.blit(total_text, total_rect)
        
        restart_button = pygame.Rect(300, 350, 150, 40)
        menu_button = pygame.Rect(500, 350, 150, 40)
        mouse_pos = pygame.mouse.get_pos()
        if restart_button.collidepoint(mouse_pos):
            bg_color = self.colors['button_hover']
        else:
            bg_color = self.colors['button']
        pygame.draw.rect(self.screen, bg_color, restart_button, border_radius=10)
        pygame.draw.rect(self.screen, (50, 50, 50), restart_button, 2, border_radius=10)
        restart_text = self.chinese_button_font.render("重新开始", True, self.colors['text'])
        restart_rect = restart_text.get_rect(center=restart_button.center)
        self.screen.blit(restart_text, restart_rect)
        if menu_button.collidepoint(mouse_pos):
            bg_color = self.colors['button_hover']
        else:
            bg_color = self.colors['button']
        pygame.draw.rect(self.screen, bg_color, menu_button, border_radius=10)
        pygame.draw.rect(self.screen, (50, 50, 50), menu_button, 2, border_radius=10)
        menu_text = self.chinese_button_font.render("返回菜单", True, self.colors['text'])
        menu_rect = menu_text.get_rect(center=menu_button.center)
        self.screen.blit(menu_text, menu_rect)

    def render_defeat_interface(self):
        """渲染失败界面"""
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        defeat_text = self.chinese_title_font.render("😞 时间到！ 😞", True, self.colors['defeat'])
        defeat_rect = defeat_text.get_rect(center=(self.width // 2, 200))
        self.screen.blit(defeat_text, defeat_rect)
        restart_button = pygame.Rect(300, 300, 150, 40)
        menu_button = pygame.Rect(500, 300, 150, 40)
        mouse_pos = pygame.mouse.get_pos()
        if restart_button.collidepoint(mouse_pos):
            bg_color = self.colors['button_hover']
        else:
            bg_color = self.colors['button']
        pygame.draw.rect(self.screen, bg_color, restart_button, border_radius=10)
        pygame.draw.rect(self.screen, (50, 50, 50), restart_button, 2, border_radius=10)
        restart_text = self.chinese_button_font.render("重新开始", True, self.colors['text'])
        restart_rect = restart_text.get_rect(center=restart_button.center)
        self.screen.blit(restart_text, restart_rect)
        if menu_button.collidepoint(mouse_pos):
            bg_color = self.colors['button_hover']
        else:
            bg_color = self.colors['button']
        pygame.draw.rect(self.screen, bg_color, menu_button, border_radius=10)
        pygame.draw.rect(self.screen, (50, 50, 50), menu_button, 2, border_radius=10)
        menu_text = self.chinese_button_font.render("返回菜单", True, self.colors['text'])
        menu_rect = menu_text.get_rect(center=menu_button.center)
        self.screen.blit(menu_text, menu_rect)

    def render_leaderboard_interface(self, leaderboard_data):
        """渲染排行榜界面"""
        self.screen.fill(self.colors['background'])
        title_text = self.chinese_title_font.render("🏆 排行榜 🏆", True, (50, 50, 150))
        title_rect = title_text.get_rect(center=(self.width // 2, 100))
        self.screen.blit(title_text, title_rect)
        y_offset = 200
        if leaderboard_data and 'leaderboard' in leaderboard_data:
            leaderboard = leaderboard_data['leaderboard']
            for idx, entry in enumerate(leaderboard[:10]):
                rank = idx + 1
                name = entry.get('username', '未知')
                time_str = f"{entry.get('time_seconds', 0)}s"
                steps = entry.get('steps', 0)
                score = entry.get('score', 0)
                entry_text = f"{rank}. {name} - 时间: {time_str} - 步数: {steps} - 得分: {score}"
                entry_surface = self.menu_font.render(entry_text, True, self.colors['text'])
                entry_rect = entry_surface.get_rect(center=(self.width // 2, y_offset + idx * 40))
                self.screen.blit(entry_surface, entry_rect)
        else:
            no_data_text = self.menu_font.render("暂无排行榜数据", True, self.colors['text'])
            no_data_rect = no_data_text.get_rect(center=(self.width // 2, 300))
            self.screen.blit(no_data_text, no_data_rect)
        back_button = pygame.Rect(200, 500, 150, 40)
        refresh_button = pygame.Rect(500, 500, 150, 40)
        mouse_pos = pygame.mouse.get_pos()
        if back_button.collidepoint(mouse_pos):
            bg_color = self.colors['button_hover']
        else:
            bg_color = self.colors['button']
        pygame.draw.rect(self.screen, bg_color, back_button, border_radius=10)
        pygame.draw.rect(self.screen, (50, 50, 50), back_button, 2, border_radius=10)
        back_text = self.chinese_button_font.render("返回", True, self.colors['text'])
        back_rect = back_text.get_rect(center=back_button.center)
        self.screen.blit(back_text, back_rect)
        if refresh_button.collidepoint(mouse_pos):
            bg_color = self.colors['button_hover']
        else:
            bg_color = self.colors['button']
        pygame.draw.rect(self.screen, bg_color, refresh_button, border_radius=10)
        pygame.draw.rect(self.screen, (50, 50, 50), refresh_button, 2, border_radius=10)
        refresh_text = self.chinese_button_font.render("刷新", True, self.colors['text'])
        refresh_rect = refresh_text.get_rect(center=refresh_button.center)
        self.screen.blit(refresh_text, refresh_rect)

    def show_message(self, title, detail=""):
        """显示消息提示"""
        if detail:
            self.message = f"{title}: {detail}"
        else:
            self.message = title
        self.message_timer = pygame.time.get_ticks()
    
    def render_message(self, message):
        """渲染消息提示"""
        if not message:
            return
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        # 使用中文字体渲染消息
        if self.chinese_font_path:
            msg_surface = self.chinese_font.render(message, True, self.colors['message_text'])
        else:
            msg_surface = self.message_font.render(message, True, self.colors['message_text'])
        msg_rect = msg_surface.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(msg_surface, msg_rect)

    def handle_input_click(self, mouse_pos, game_state):
        """处理输入框点击，激活对应的输入框"""
        # 先检查是否是按钮点击，如果是按钮点击，不处理输入框
        if game_state == "login":
            # 检查是否是按钮点击
            is_button_click = False
            for button_rect in self.login_buttons.values():
                if button_rect.collidepoint(mouse_pos):
                    is_button_click = True
                    break
            if is_button_click:
                return  # 如果是按钮点击，不处理输入框
            
            if self.login_username_input.collidepoint(mouse_pos):
                self.input_active = 'login_username'
            elif self.login_password_input.collidepoint(mouse_pos):
                self.input_active = 'login_password'
            else:
                self.input_active = None
        elif game_state == "register":
            # 检查是否是按钮点击
            is_button_click = False
            for button_rect in self.register_buttons.values():
                if button_rect.collidepoint(mouse_pos):
                    is_button_click = True
                    break
            if is_button_click:
                return  # 如果是按钮点击，不处理输入框
            
            if self.register_username_input.collidepoint(mouse_pos):
                self.input_active = 'register_username'
            elif self.register_password_input.collidepoint(mouse_pos):
                self.input_active = 'register_password'
            else:
                self.input_active = None

    def handle_key_input(self, event):
        """处理键盘输入"""
        if self.input_active is None:
            return
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                # 删除最后一个字符
                if self.input_active == 'login_username':
                    self.login_username = self.login_username[:-1]
                elif self.input_active == 'login_password':
                    self.login_password = self.login_password[:-1]
                elif self.input_active == 'register_username':
                    self.register_username = self.register_username[:-1]
                elif self.input_active == 'register_password':
                    self.register_password = self.register_password[:-1]
            elif event.key == pygame.K_TAB:
                # Tab键切换输入框
                if self.input_active == 'login_username':
                    self.input_active = 'login_password'
                elif self.input_active == 'login_password':
                    self.input_active = 'login_username'
                elif self.input_active == 'register_username':
                    self.input_active = 'register_password'
                elif self.input_active == 'register_password':
                    self.input_active = 'register_username'
            elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                # Enter键不处理，由按钮点击处理
                pass
            else:
                # 普通字符输入
                char = event.unicode
                # 如果unicode为空，尝试从key获取字符（处理某些键盘布局问题）
                if not char or len(char) == 0:
                    # 尝试从key code转换为字符
                    if pygame.K_a <= event.key <= pygame.K_z:
                        # 字母键
                        shift_pressed = pygame.key.get_mods() & pygame.KMOD_SHIFT
                        if shift_pressed:
                            char = chr(ord('A') + (event.key - pygame.K_a))
                        else:
                            char = chr(ord('a') + (event.key - pygame.K_a))
                    elif pygame.K_0 <= event.key <= pygame.K_9:
                        # 数字键
                        char = chr(ord('0') + (event.key - pygame.K_0))
                    elif event.key == pygame.K_SPACE:
                        char = ' '
                    elif event.key == pygame.K_MINUS:
                        char = '-' if not (pygame.key.get_mods() & pygame.KMOD_SHIFT) else '_'
                    elif event.key == pygame.K_PERIOD:
                        char = '.'
                    elif event.key == pygame.K_2:
                        # Shift+2 通常是 @ 符号
                        if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                            char = '@'
                        else:
                            char = '2'
                    else:
                        # 其他特殊字符，尝试使用unicode（这是最可靠的方法）
                        char = event.unicode if event.unicode else ''
                
                # 处理字符输入
                if char and len(char) > 0:
                    # 允许所有可打印字符（包括字母、数字、特殊字符）
                    if char.isprintable() or char in ['@', '.', '-', '_']:
                        # 限制输入长度
                        if self.input_active == 'login_username':
                            max_length = 20
                            if len(self.login_username) < max_length:
                                self.login_username += char
                        elif self.input_active == 'login_password':
                            max_length = 20
                            if len(self.login_password) < max_length:
                                self.login_password += char
                        elif self.input_active == 'register_username':
                            max_length = 20
                            if len(self.register_username) < max_length:
                                self.register_username += char
                        elif self.input_active == 'register_password':
                            max_length = 20
                            if len(self.register_password) < max_length:
                                self.register_password += char

    def handle_text_input(self, text):
        """处理文本输入"""
        if self.input_active is None:
            return
        
        # 处理字符输入
        if text and len(text) > 0:
            if text.isprintable() or text in ['@', '.', '-', '_']:
                # 限制输入长度
                if self.input_active == 'login_username':
                    max_length = 20
                    if len(self.login_username) < max_length:
                        self.login_username += text
                elif self.input_active == 'login_password':
                    max_length = 20
                    if len(self.login_password) < max_length:
                        self.login_password += text
                elif self.input_active == 'register_username':
                    max_length = 20
                    if len(self.register_username) < max_length:
                        self.register_username += text
                elif self.input_active == 'register_password':
                    max_length = 20
                    if len(self.register_password) < max_length:
                        self.register_password += text

    def get_card_position(self, mouse_pos, current_game):
        """根据鼠标位置获取卡牌位置（必须与渲染逻辑一致）"""
        if not current_game or not hasattr(current_game, 'get_grid_state'):
            return None
        
        grid_state = current_game.get_grid_state()
        rows = len(grid_state)
        cols = len(grid_state[0]) if rows > 0 else 0
        
        # 使用与渲染相同的尺寸计算逻辑
        if rows <= 4 and cols <= 4:
            # 简单模式：4x4，使用较大的卡牌
            card_width, card_height = 100, 120
            spacing = 15
        else:
            # 困难模式：7x7，使用较小的卡牌
            card_width, card_height = 60, 80
            spacing = 8
        
        # 计算总宽度和起始位置，确保居中（与渲染逻辑一致）
        total_width = cols * (card_width + spacing) - spacing
        total_height = rows * (card_height + spacing) - spacing
        start_x = (self.width - total_width) // 2
        start_y = 100  # HUD下方
        
        # 确保不会超出屏幕（与渲染逻辑一致）
        max_y = start_y + total_height
        if max_y > self.height - 120:  # 留出按钮空间
            # 如果超出，缩小卡牌尺寸
            scale = (self.height - 120 - start_y) / total_height
            card_width = int(card_width * scale)
            card_height = int(card_height * scale)
            spacing = int(spacing * scale)
            total_width = cols * (card_width + spacing) - spacing
            start_x = (self.width - total_width) // 2
        
        mouse_x, mouse_y = mouse_pos
        
        # 检查点击是否在卡牌区域内
        for r in range(rows):
            for c in range(cols):
                card_x = start_x + c * (card_width + spacing)
                card_y = start_y + r * (card_height + spacing)
                card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
                if card_rect.collidepoint(mouse_pos):
                    return (r, c)
        
        return None