import pygame
import sys
import time
import os
from ui import GameUI
from modes.simple_mode import SimpleGame
from modes.dynamic_maze import DynamicMazeGame
from local_storage import LocalStorage

class MemoryMatchGame:
    """记忆迷宫游戏主控制器"""

    def __init__(self):
        # 初始化pygame和游戏状态
        pygame.init()
        self.screen = pygame.display.set_mode((1000, 700))
        pygame.display.set_caption("Memory Match Game")
        
        # 初始化UI模块
        self.ui = GameUI(self.screen)
        
        # 游戏状态
        self.current_game = None
        self.game_state = "menu"  # menu, login, register, shop, history, game, victory, defeat, leaderboard
        self.running = True
        self.clock = pygame.time.Clock()
        
        # 游戏计时
        self.start_time = 0
        self.elapsed_time = 0
        self.step_count = 0
        self.timer_active = False
        self.waiting_to_hide = False
        
        # 本地存储系统（替代后端）
        self.storage = LocalStorage()
        
        # 用户信息
        self.user_logged_in = False
        self.username = ""
        self.points = 0
        self.user_items = {"delay": 0, "block": 0, "reveal": 0}
        
        # 排行榜数据
        self.leaderboard_data = {"leaderboard": []}
    
    
    def run(self):
        """主游戏循环"""
        while self.running:
            # 处理事件
            self.handle_events()
            
            # 更新游戏状态
            self.update_game_state()
            
            # 渲染界面
            self.ui.render(self.game_state, self.current_game, self.waiting_to_hide, self.elapsed_time, self.step_count, self.points, self.user_logged_in, self.username, self.user_items)
            
            # 控制帧率
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

    def handle_events(self):
        """处理游戏事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            
            # ✅ 先处理文本输入
            elif event.type == pygame.TEXTINPUT:
                if self.game_state in ["login", "register"]:
                    if hasattr(self.ui, 'handle_text_input'):
                        self.ui.handle_text_input(event.text)
            
            elif event.type == pygame.KEYDOWN:
                # 先让UI处理特殊键（如退格）
                if self.game_state in ["login", "register"]:
                    if hasattr(self.ui, 'handle_key_input'):
                        if self.ui.handle_key_input(event):  # 返回True表示已处理
                            continue
                # 再处理功能键
                self.handle_keyboard(event.key)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    # 对于登录和注册界面，先处理输入框点击，再处理按钮点击
                    if self.game_state in ["login", "register"]:
                        if hasattr(self.ui, 'handle_input_click'):
                            self.ui.handle_input_click(mouse_pos, self.game_state)
                    self.handle_mouse_click(mouse_pos)

    def handle_keyboard(self, key):
        """处理键盘事件"""
        if key == pygame.K_ESCAPE:
            if self.game_state in ["game", "victory", "defeat", "leaderboard", "shop", "history", "login", "register"]:
                self.return_to_menu()
            else:
                self.running = False
        
        elif key == pygame.K_r and self.game_state == "game":
            self.restart_game()
        elif key == pygame.K_d and self.game_state == "game":
            self.use_delay_item()
        elif key == pygame.K_b and self.game_state == "game":
            self.use_block_item()

    def handle_mouse_click(self, mouse_pos):
        """处理鼠标点击事件"""
        if self.game_state == "menu":
            self.handle_menu_click(mouse_pos)
        elif self.game_state == "login":
            self.handle_login_click(mouse_pos)
        elif self.game_state == "register":
            self.handle_register_click(mouse_pos)
        elif self.game_state == "shop":
            self.handle_shop_click(mouse_pos)
        elif self.game_state == "history":
            self.handle_history_click(mouse_pos)
        elif self.game_state == "game":
            self.handle_game_click(mouse_pos)
        elif self.game_state == "victory":
            self.handle_victory_click(mouse_pos)
        elif self.game_state == "defeat":
            self.handle_defeat_click(mouse_pos)
        elif self.game_state == "leaderboard":
            self.handle_leaderboard_click(mouse_pos)
    
    def handle_menu_click(self, mouse_pos):
        """处理菜单界面的点击"""
        action = self.ui.get_menu_action(mouse_pos, self.user_logged_in)
        
        if action == "start_game":
            self.start_simple_mode()
        elif action == "hard_game":
            self.start_hard_mode()
        elif action == "leaderboard":
            self.show_leaderboard()
        elif action == "shop":
            self.show_shop()
        elif action == "history":
            self.show_history()
        elif action == "login":
            self.show_login()
        elif action == "register":
            self.show_register()
        elif action == "exit":
            self.running = False
    
    def handle_login_click(self, mouse_pos):
        """处理登录界面的点击"""
        action = self.ui.get_login_action(mouse_pos)
        if action == "login":
            username = self.ui.get_login_username()
            password = self.ui.get_login_password()
            self.authenticate_user(username, password)
        elif action == "back":
            self.return_to_menu()
    
    def handle_register_click(self, mouse_pos):
        """处理注册界面的点击"""
        action = self.ui.get_register_action(mouse_pos)
        if action == "register":
            username = self.ui.get_register_username()
            password = self.ui.get_register_password()
            self.register_user(username, password)
        elif action == "back":
            self.return_to_menu()
    
    def handle_shop_click(self, mouse_pos):
        """处理商城界面的点击"""
        action = self.ui.get_shop_action(mouse_pos)
        
        if action == "buy_delay":
            self.buy_delay_item()
        elif action == "buy_block":
            self.buy_block_item()
        elif action == "buy_reveal":
            self.buy_reveal_item()
        elif action == "back":
            self.return_to_menu()
    
    def handle_history_click(self, mouse_pos):
        """处理历史记录界面的点击"""
        action = self.ui.get_history_action(mouse_pos)
        if action == "back":
            self.return_to_menu()
    
    def handle_game_click(self, mouse_pos):
        """处理游戏中的点击"""
        if self.waiting_to_hide:
            print("正在等待隐藏，忽略点击")
            return  # 正在处理翻牌，忽略点击
        
        # 先检查是否是按钮点击
        action = self.ui.get_game_action(mouse_pos, self.current_game)
        print(f"游戏点击检测 - 鼠标位置: {mouse_pos}, 检测到的动作: {action}")
        print(f"用户道具状态 - 延时: {self.user_items.get('delay', 0)}, 阻挡: {self.user_items.get('block', 0)}, 翻牌: {self.user_items.get('reveal', 0)}")
        
        if action == "delay":
            print("尝试使用延时道具")
            self.use_delay_item()
            return
        elif action == "block":
            print("尝试使用阻挡道具")
            self.use_block_item()
            return
        elif action == "restart":
            self.restart_game()
            return
        elif action == "menu":
            self.return_to_menu()
            return
        
        # 检查是否是卡牌点击
        if hasattr(self.ui, 'get_card_position'):
            card_pos = self.ui.get_card_position(mouse_pos, self.current_game)
            if card_pos:
                print(f"检测到卡牌点击：位置 {card_pos}")
                self.flip_card(*card_pos)
            else:
                print(f"未检测到卡牌点击，鼠标位置：{mouse_pos}")
    
    def handle_victory_click(self, mouse_pos):
        """处理胜利界面的点击"""
        action = self.ui.get_victory_action(mouse_pos)
        
        if action == "restart":
            self.restart_game()
        elif action == "menu":
            self.return_to_menu()
    
    def handle_defeat_click(self, mouse_pos):
        """处理失败界面的点击"""
        action = self.ui.get_defeat_action(mouse_pos)
        
        if action == "restart":
            self.restart_game()
        elif action == "menu":
            self.return_to_menu()
    
    def handle_leaderboard_click(self, mouse_pos):
        """处理排行榜界面的点击"""
        action = self.ui.get_leaderboard_action(mouse_pos)
        if action == "back":  # 修正：原代码是"menu"，UI里是"back"
            self.return_to_menu()
        elif action == "refresh":
            self.show_leaderboard()
    
    def authenticate_user(self, username, password):
        """认证用户（使用本地存储）"""
        try:
            if not username or not username.strip():
                if hasattr(self.ui, 'show_message'):
                    self.ui.show_message("登录失败", "请输入用户名")
                return
            if not password or not password.strip():
                if hasattr(self.ui, 'show_message'):
                    self.ui.show_message("登录失败", "请输入密码")
                return
            
            user_data = self.storage.authenticate_user(username, password)
            if user_data:
                self.user_logged_in = True
                self.username = user_data["username"]
                self.points = user_data["points"]
                self.user_items = user_data.get("items", {"delay": 0, "block": 0, "reveal": 0})
                self.return_to_menu()
                print("登录成功！")
            else:
                if hasattr(self.ui, 'show_message'):
                    self.ui.show_message("登录失败", "用户名或密码错误")
        except Exception as e:
            print(f"登录失败: {e}")
            if hasattr(self.ui, 'show_message'):
                self.ui.show_message("登录失败", str(e))
    
    def register_user(self, username, password):
        """注册用户（使用本地存储）"""
        try:
            if not username or not username.strip():
                if hasattr(self.ui, 'show_message'):
                    self.ui.show_message("注册失败", "请输入用户名")
                return
            if not password or not password.strip():
                if hasattr(self.ui, 'show_message'):
                    self.ui.show_message("注册失败", "请输入密码")
                return
            
            user_data = self.storage.register_user(username, password)
            if user_data:
                if hasattr(self.ui, 'show_message'):
                    self.ui.show_message("注册成功", "请登录")
                self.show_login()
            else:
                if hasattr(self.ui, 'show_message'):
                    self.ui.show_message("注册失败", "注册失败，请重试")
        except Exception as e:
            print(f"注册失败: {e}")
            if hasattr(self.ui, 'show_message'):
                self.ui.show_message("注册失败", str(e))
    
    def buy_delay_item(self):
        """购买延时道具（使用本地存储）"""
        if not self.user_logged_in:
            if hasattr(self.ui, 'show_message'):
                self.ui.show_message("错误", "请先登录")
            return
        
        cost = 10  # 延时道具价格
        if self.points < cost:
            if hasattr(self.ui, 'show_message'):
                self.ui.show_message("购买失败", "积分不足")
            return
        
        if self.storage.buy_item(self.username, "delay", cost):
            self.points -= cost
            self.user_items["delay"] += 1
            # 更新本地存储中的用户信息
            user = self.storage.get_user(self.username)
            if user:
                self.points = user["points"]
                self.user_items = user["items"]
            if hasattr(self.ui, 'show_message'):
                self.ui.show_message("购买成功", "延时道具已购买")
            self.show_shop()
        else:
            if hasattr(self.ui, 'show_message'):
                self.ui.show_message("购买失败", "购买失败")
    
    def buy_block_item(self):
        """购买阻挡道具（使用本地存储）"""
        if not self.user_logged_in:
            if hasattr(self.ui, 'show_message'):
                self.ui.show_message("错误", "请先登录")
            return
        
        cost = 15  # 阻挡道具价格
        if self.points < cost:
            if hasattr(self.ui, 'show_message'):
                self.ui.show_message("购买失败", "积分不足")
            return
        
        if self.storage.buy_item(self.username, "block", cost):
            self.points -= cost
            self.user_items["block"] += 1
            # 更新本地存储中的用户信息
            user = self.storage.get_user(self.username)
            if user:
                self.points = user["points"]
                self.user_items = user["items"]
            if hasattr(self.ui, 'show_message'):
                self.ui.show_message("购买成功", "阻挡道具已购买")
            self.show_shop()
        else:
            if hasattr(self.ui, 'show_message'):
                self.ui.show_message("购买失败", "购买失败")
    
    def buy_reveal_item(self):
        """购买直接翻牌道具（使用本地存储）"""
        if not self.user_logged_in:
            if hasattr(self.ui, 'show_message'):
                self.ui.show_message("错误", "请先登录")
            return
        
        cost = 20  # 直接翻牌道具价格
        if self.points < cost:
            if hasattr(self.ui, 'show_message'):
                self.ui.show_message("购买失败", "积分不足")
            return
        
        if self.storage.buy_item(self.username, "reveal", cost):
            self.points -= cost
            self.user_items["reveal"] += 1
            # 更新本地存储中的用户信息
            user = self.storage.get_user(self.username)
            if user:
                self.points = user["points"]
                self.user_items = user["items"]
            if hasattr(self.ui, 'show_message'):
                self.ui.show_message("购买成功", "直接翻牌道具已购买")
            self.show_shop()
        else:
            if hasattr(self.ui, 'show_message'):
                self.ui.show_message("购买失败", "购买失败")
    
    def show_login(self):
        """显示登录界面"""
        self.game_state = "login"
        # 启用文本输入模式，确保可以输入所有字符
        pygame.key.start_text_input()
        if hasattr(self.ui, 'reset_login_inputs'):
            self.ui.reset_login_inputs()
    
    def show_register(self):
        """显示注册界面"""
        self.game_state = "register"
        # 启用文本输入模式，确保可以输入所有字符
        pygame.key.start_text_input()
        if hasattr(self.ui, 'reset_register_inputs'):
            self.ui.reset_register_inputs()
    
    def show_shop(self):
        """显示商城界面"""
        self.game_state = "shop"
    
    def show_history(self):
        """显示历史记录界面（使用本地存储）"""
        self.game_state = "history"
        if self.user_logged_in:
            history = self.storage.get_user_history(self.username, limit=100)
            if hasattr(self.ui, 'render_history_interface'):
                self.ui.render_history_interface(history)
        else:
            if hasattr(self.ui, 'render_history_interface'):
                self.ui.render_history_interface([])
    
    def show_leaderboard(self):
        """显示排行榜（使用本地存储）"""
        self.game_state = "leaderboard"
        self.load_leaderboard()
    
    def load_leaderboard(self, game_mode: str = "simple", sort_by: str = "time"):
        """加载排行榜数据（使用本地存储）"""
        try:
            results = self.storage.get_leaderboard(game_mode=game_mode, sort_by=sort_by, limit=10)
            leaderboard = []
            for result in results:
                leaderboard.append({
                    "username": result["username"],
                    "time_seconds": result["time_seconds"],
                    "steps": result["steps"],
                    "game_mode": result["game_mode"],
                    "score": result.get("score", 0),
                    "date": result["created_at"]
                })
            self.leaderboard_data = {"leaderboard": leaderboard}
            if hasattr(self.ui, 'render_leaderboard_interface'):
                self.ui.render_leaderboard_interface(self.leaderboard_data)
        except Exception as e:
            print(f"加载排行榜失败: {e}")
            if hasattr(self.ui, 'show_message'):
                self.ui.show_message("排行榜加载失败", str(e))
    
    def start_simple_mode(self):
        """开始简单模式游戏"""
        try:
            self.current_game = SimpleGame(4, 4)
            self.game_state = "game"
            self.waiting_to_hide = False
            self.start_time = time.time()
            self.timer_active = True
            self.step_count = 0
            print("简单模式开始！")
        except Exception as e:
            print(f"开始简单模式失败: {e}")
            if hasattr(self.ui, 'show_message'):
                self.ui.show_message("游戏启动失败", "请稍后再试")
    
    def start_hard_mode(self):
        """开始困难模式游戏"""
        try:
            self.current_game = DynamicMazeGame(7, 7)
            # 同步用户道具数量到游戏中
            if self.user_logged_in and hasattr(self.current_game, 'delay_item_count'):
                print(f"道具同步前 - 用户道具: {self.user_items}")
                print(f"道具同步前 - 游戏道具: 延时={self.current_game.delay_item_count}, 阻挡={self.current_game.block_item_count}")
                
                self.current_game.delay_item_count = self.user_items.get("delay", 0)
                self.current_game.block_item_count = self.user_items.get("block", 0)
                
                print(f"道具同步后 - 游戏道具: 延时={self.current_game.delay_item_count}, 阻挡={self.current_game.block_item_count}")
            self.game_state = "game"
            self.waiting_to_hide = False
            self.start_time = time.time()
            self.timer_active = True
            self.step_count = 0
            print("困难模式开始！")
        except Exception as e:
            print(f"开始困难模式失败: {e}")
            if hasattr(self.ui, 'show_message'):
                self.ui.show_message("游戏启动失败", "请稍后再试")
    
    def restart_game(self):
        """重新开始游戏"""
        if self.current_game:
            if isinstance(self.current_game, DynamicMazeGame):
                self.start_hard_mode()
            else:
                self.start_simple_mode()
    
    def use_delay_item(self):
        """使用延时道具"""
        print(f"使用延时道具 - 登录状态: {self.user_logged_in}, 用户道具数量: {self.user_items.get('delay', 0)}")
        
        if not self.user_logged_in:
            if hasattr(self.ui, 'show_message'):
                self.ui.show_message("错误", "请先登录")
            return
        
        if self.user_items["delay"] <= 0:
            if hasattr(self.ui, 'show_message'):
                self.ui.show_message("错误", "没有延时道具")
            return
        
        if self.current_game and hasattr(self.current_game, 'use_item_delay'):
            # 检查游戏对象中的道具数量
            game_delay_count = getattr(self.current_game, 'delay_item_count', 0)
            print(f"游戏对象中的延时道具数量: {game_delay_count}")
            
            if game_delay_count <= 0:
                if hasattr(self.ui, 'show_message'):
                    self.ui.show_message("错误", "游戏中的延时道具已用完")
                return
                
            if self.storage.use_item(self.username, "delay"):
                self.user_items["delay"] -= 1
                self.current_game.use_item_delay(5)
                self.step_count += 1
                print("延时道具使用成功")
                if hasattr(self.ui, 'show_message'):
                    self.ui.show_message("道具使用成功", "延时5秒")
            else:
                print("道具使用失败 - 存储更新失败")
    
    def use_block_item(self):
        """使用阻挡道具"""
        print(f"使用阻挡道具 - 登录状态: {self.user_logged_in}, 用户道具数量: {self.user_items.get('block', 0)}")
        
        if not self.user_logged_in:
            if hasattr(self.ui, 'show_message'):
                self.ui.show_message("错误", "请先登录")
            return
        
        if self.user_items["block"] <= 0:
            if hasattr(self.ui, 'show_message'):
                self.ui.show_message("错误", "没有阻挡道具")
            return
        
        if self.current_game and hasattr(self.current_game, 'use_item_block_shuffle'):
            # 检查游戏对象中的道具数量
            game_block_count = getattr(self.current_game, 'block_item_count', 0)
            print(f"游戏对象中的阻挡道具数量: {game_block_count}")
            
            if game_block_count <= 0:
                if hasattr(self.ui, 'show_message'):
                    self.ui.show_message("错误", "游戏中的阻挡道具已用完")
                return
                
            if self.storage.use_item(self.username, "block"):
                self.user_items["block"] -= 1
                self.current_game.use_item_block_shuffle(5)
                self.step_count += 1
                print("阻挡道具使用成功")
                if hasattr(self.ui, 'show_message'):
                    self.ui.show_message("道具使用成功", "阻挡重排")
            else:
                print("道具使用失败 - 存储更新失败")
    
    def use_reveal_item(self):
        """使用直接翻牌道具"""
        if not self.user_logged_in:
            if hasattr(self.ui, 'show_message'):
                self.ui.show_message("错误", "请先登录")
            return
        
        if self.user_items["reveal"] <= 0:
            if hasattr(self.ui, 'show_message'):
                self.ui.show_message("错误", "没有直接翻牌道具")
            return
        
        if self.current_game and hasattr(self.current_game, 'reveal_random_card'):
            if self.storage.use_item(self.username, "reveal"):
                self.user_items["reveal"] -= 1
                self.current_game.reveal_random_card()
                self.step_count += 1
                if hasattr(self.ui, 'show_message'):
                    self.ui.show_message("道具使用成功", "已翻开一张卡牌")
    
    def flip_card(self, row, col):
        """翻牌操作"""
        try:
            # flip_card返回True表示配对成功，False表示配对失败或第一次翻牌
            matched = self.current_game.flip_card(row, col)
            self.step_count += 1
            
            if matched:
                # 配对成功 - 也需要等待一段时间让用户看到匹配的卡牌
                print("配对成功！")
                self.handle_pair_matched()
                # 设置等待状态，让匹配成功的卡牌也显示一段时间
                self.waiting_to_hide = True
                self.flip_timer = pygame.time.get_ticks()
                # 检查游戏是否完成
                if self.current_game.is_completed():
                    # 游戏完成，但也要等待显示时间
                    pygame.time.wait(1000)  # 等待1秒让用户看到最后匹配的卡牌
                    self.game_state = "victory"
                    print("游戏完成！")
                    self.upload_game_result("victory")
                    # 刷新用户信息
                    if self.user_logged_in:
                        user = self.storage.get_user(self.username)
                        if user:
                            self.points = user["points"]
            else:
                # 检查是否有两张卡片被翻开但未匹配（配对失败，需要隐藏）
                flipped_count = 0
                if hasattr(self.current_game, 'get_grid_state'):
                    grid_state = self.current_game.get_grid_state()
                    for row in grid_state:
                        for card_id, is_flipped, is_matched in row:
                            if is_flipped and not is_matched:
                                flipped_count += 1
                
                # 如果有两张卡片被翻开但未匹配，说明配对失败，需要隐藏
                if flipped_count == 2:
                    self.waiting_to_hide = True
                    self.flip_timer = pygame.time.get_ticks()
        except Exception as e:
            print(f"翻牌错误: {e}")
            import traceback
            traceback.print_exc()
    
    def is_second_flip(self):
        """检查是否是第二次翻牌（配对失败的情况）"""
        # 如果_first_selected和_second_selected都已设置，说明已经完成配对检查
        # 如果_first_selected已设置但_second_selected为None，说明只翻了一张牌
        # 配对失败后，两者都会被重置为None
        # 所以这里应该检查：是否已经完成配对检查但配对失败
        if not hasattr(self.current_game, '_first_selected'):
            return False
        # 如果_first_selected为None，说明没有翻牌或已重置，不是第二次翻牌
        if self.current_game._first_selected is None:
            return False
        # 如果_second_selected不为None，说明已经完成配对检查
        if self.current_game._second_selected is not None:
            return False
        # 如果_first_selected不为None但_second_selected为None，说明只翻了一张牌
        # 但这不是"第二次翻牌"的情况，因为第二次翻牌会触发配对检查
        # 实际上，配对失败后，两者都会被重置，所以这里应该检查是否有翻开的卡片
        # 更简单的方法：检查是否有两张卡片被翻开但未匹配
        flipped_count = 0
        if hasattr(self.current_game, 'get_grid_state'):
            grid_state = self.current_game.get_grid_state()
            for row in grid_state:
                for card_id, is_flipped, is_matched in row:
                    if is_flipped and not is_matched:
                        flipped_count += 1
        return flipped_count == 2
    
    def handle_pair_matched(self):
        """处理配对成功"""
        # 实现配对成功的缩放反馈动画
        if hasattr(self.current_game, 'score'):
            score = self.current_game.score
            self.points += score
            # 更新本地存储中的积分
            if self.user_logged_in:
                self.storage.update_user_points(self.username, score)
    
    def update_game_state(self):
        """更新游戏状态（如计时器等）"""
        if self.timer_active and self.game_state == "game":
            current_time = time.time()
            self.elapsed_time = int(current_time - self.start_time)
            
            # 检查困难模式的时间限制
            if hasattr(self.current_game, 'is_time_over'):
                if self.current_game.is_time_over():
                    self.game_state = "defeat"
                    print("时间到！你输了。")
                    self.upload_game_result("defeat")
            else:
                # 简单模式：3分钟倒计时
                if self.elapsed_time >= 180:  # 3分钟倒计时
                    self.game_state = "defeat"
                    print("时间到！你输了。")
                    self.upload_game_result("defeat")
                    
            if self.waiting_to_hide:
                reveal_ms = 1000  # 默认1秒
                if hasattr(self.current_game, 'get_reveal_duration_ms'):
                    reveal_ms = self.current_game.get_reveal_duration_ms()
                if pygame.time.get_ticks() - self.flip_timer > reveal_ms:
                    if self.current_game:
                        # 检查是否需要洗牌
                        if hasattr(self.current_game, 'pending_shuffle') and self.current_game.pending_shuffle:
                            if hasattr(self.ui, 'show_message'):
                                self.ui.show_message("洗牌", "连续匹配失败，正在洗牌...")
                            print("触发洗牌！")
                        # 只隐藏未匹配的卡片，已匹配的卡片保持显示
                        self.current_game.hide_all_flipped()
                    self.waiting_to_hide = False
    
    def upload_game_result(self, result):
        """保存游戏结果到本地存储"""
        if not self.user_logged_in:
            return
        
        try:
            game_mode = "simple" if isinstance(self.current_game, SimpleGame) else "hard"
            time_seconds = self.elapsed_time if self.timer_active else 0
            steps = self.step_count
            score = self.current_game.score if hasattr(self.current_game, 'score') else 0
            
            # 保存游戏结果
            self.storage.add_game_result(
                username=self.username,
                game_mode=game_mode,
                time_seconds=time_seconds,
                steps=steps,
                score=score,
                result=result
            )
            
            # 如果胜利，计算并添加积分
            if result == "victory":
                if game_mode == "simple":
                    points = 10 if (time_seconds <= 120 and steps <= 50) else 5
                else:  # hard mode
                    points = 20 if (time_seconds <= 180 and steps <= 100) else 10
                
                self.storage.update_user_points(self.username, points)
                self.points += points
                print(f"游戏完成！获得 {points} 积分")
                # 将积分信息存储到游戏对象中，供UI显示
                if self.current_game:
                    self.current_game.points_earned = points
                # 显示积分获取消息
                if hasattr(self.ui, 'show_message'):
                    self.ui.show_message("🎉 胜利奖励", f"恭喜完成游戏！\n获得 {points} 积分\n当前总积分: {self.points}")
            else:
                print("游戏结束")
        except Exception as e:
            print(f"保存游戏结果失败: {e}")
    
    def return_to_menu(self):
        """返回主菜单"""
        self.game_state = "menu"
        # 停止文本输入模式
        pygame.key.stop_text_input()
        self.current_game = None
        self.waiting_to_hide = False
        self.timer_active = False
        self.start_time = 0
        self.elapsed_time = 0
        self.step_count = 0
        
        # 刷新用户信息（从本地存储）
        if self.user_logged_in:
            user = self.storage.get_user(self.username)
            if user:
                self.points = user["points"]
                self.user_items = user["items"]

def main():
    """程序入口点"""
    try:
        game = MemoryMatchGame()
        game.run()
    except Exception as e:
        print(f"程序错误: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()