import pygame
import sys
import requests
import json
import subprocess
import time
import threading
import os
from ui import GameUI
from modes.simple_mode import SimpleGame
from modes.dynamic_maze import DynamicMazeGame

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
        
        # 后端服务
        self.backend_process = None
        self.backend_url = "http://localhost:8000"
        self.backend_ready = False
        
        # 用户信息
        self.user_logged_in = False
        self.username = ""
        self.points = 0
        
        # 排行榜数据
        self.leaderboard_data = {"leaderboard": []}
        
        # 自动启动后端服务
        self.start_backend_service()
    
    def start_backend_service(self):
        """启动后端服务"""
        def start_backend():
            try:
                # 动态获取后端目录路径（相对于当前文件）
                current_dir = os.path.dirname(os.path.abspath(__file__))
                backend_dir = os.path.join(current_dir, "backend")
                
                # 检查后端目录是否存在
                if not os.path.exists(backend_dir):
                    print(f"错误：后端目录不存在: {backend_dir}")
                    return
                
                # 检查启动脚本是否存在
                start_server_path = os.path.join(backend_dir, "start_server.py")
                if not os.path.exists(start_server_path):
                    print(f"错误：启动脚本不存在: {start_server_path}")
                    return
                
                print(f"正在启动后端服务，目录: {backend_dir}")
                
                # 启动后端服务
                self.backend_process = subprocess.Popen(
                    [sys.executable, "start_server.py"],
                    cwd=backend_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,  # 将stderr重定向到stdout
                    text=True,
                    bufsize=1  # 行缓冲
                )
                
                # 等待后端服务启动
                max_attempts = 30
                startup_success = False
                output_lines = []
                
                for i in range(max_attempts):
                    # 检查进程是否已退出
                    if self.backend_process.poll() is not None:
                        # 进程已退出，读取所有输出
                        time.sleep(0.5)  # 等待输出缓冲
                        try:
                            remaining_output = self.backend_process.stdout.read()
                            if remaining_output:
                                output_lines.extend(remaining_output.splitlines())
                        except:
                            pass
                        
                        if output_lines:
                            print("后端服务启动失败，错误信息:")
                            for line in output_lines[-20:]:  # 显示最后20行
                                if line.strip():
                                    print(f"  {line}")
                        else:
                            print(f"后端服务进程意外退出，返回码: {self.backend_process.returncode}")
                            print("可能的原因:")
                            print("  1. 缺少依赖包")
                            print("  2. Python版本不兼容")
                            print("  3. 数据库文件权限问题")
                        break
                    
                    # 尝试连接健康检查端点
                    try:
                        response = requests.get(f"{self.backend_url}/health", timeout=1)
                        if response.status_code == 200:
                            self.backend_ready = True
                            startup_success = True
                            print("后端服务启动成功！")
                            break
                    except requests.exceptions.ConnectionError:
                        # 连接被拒绝，继续等待
                        if i % 5 == 0 and i > 0:  # 每5秒显示一次进度
                            print(f"等待后端服务启动... ({i}/{max_attempts})")
                        time.sleep(1)
                    except Exception as e:
                        print(f"检查后端服务时出错: {e}")
                        time.sleep(1)
                        if i == max_attempts - 1:
                            print("后端服务启动超时")
                
                if not startup_success:
                    if self.backend_process.poll() is None:
                        # 进程还在运行但无法连接
                        print("后端服务启动超时，请检查:")
                        print("  1. 端口8000是否被占用")
                        print("  2. 防火墙是否阻止了连接")
                        print("  3. 查看上面的错误信息")
                        # 显示部分输出
                        if output_lines:
                            print("\n后端服务输出（最后10行）:")
                            for line in output_lines[-10:]:
                                if line.strip():
                                    print(f"  {line}")
                    else:
                        # 进程已退出
                        if not output_lines:
                            print("后端服务进程已退出，但未捕获到错误信息")
                            print("建议手动运行后端服务查看错误:")
                            print(f"  cd {backend_dir}")
                            print(f"  python start_server.py")
                
            except Exception as e:
                print(f"启动后端服务失败: {e}")
                import traceback
                traceback.print_exc()
        
        # 在后台线程启动后端服务
        backend_thread = threading.Thread(target=start_backend)
        backend_thread.daemon = True
        backend_thread.start()
        
        # 定期检查后端状态
        pygame.time.set_timer(pygame.USEREVENT + 1, 2000)  # 每2秒检查一次
    
    def run(self):
        """主游戏循环"""
        while self.running:
            # 处理事件
            self.handle_events()
            
            # 更新游戏状态
            self.update_game_state()
            
            # 渲染界面
            self.ui.render(self.game_state, self.current_game, self.waiting_to_hide, self.elapsed_time, self.step_count, self.points, self.user_logged_in, self.username)
            
            # 控制帧率
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.USEREVENT + 1:  # 后端检查
                if self.backend_process:
                    self.check_backend_status()
            
            elif event.type == pygame.KEYDOWN:
                self.handle_keyboard(event.key)
                # 关键：将键盘输入传递给UI处理
                if self.game_state in ["login", "register"]:
                    # 假设UI有处理键盘输入的方法
                    if hasattr(self.ui, 'handle_key_input'):
                        self.ui.handle_key_input(event)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键点击
                    mouse_pos = pygame.mouse.get_pos()
                    # 关键：先处理输入框点击激活（在按钮点击之前）
                    # 这样如果点击了输入框，可以激活它；如果点击了按钮，按钮处理会覆盖
                    if self.game_state in ["login", "register"]:
                        if hasattr(self.ui, 'handle_input_click'):
                            self.ui.handle_input_click(mouse_pos, self.game_state)
                    # 然后处理按钮点击
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
            email = self.ui.get_register_email()
            password = self.ui.get_register_password()
            self.register_user(username, email, password)
        elif action == "back":
            self.return_to_menu()
    
    def handle_shop_click(self, mouse_pos):
        """处理商城界面的点击"""
        action = self.ui.get_shop_action(mouse_pos)
        if action == "buy_delay":
            self.buy_delay_item()
        elif action == "buy_block":
            self.buy_block_item()
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
            return  # 正在处理翻牌，忽略点击
        action = self.ui.get_game_action(mouse_pos, self.current_game)
        if action == "delay":
            self.use_delay_item()
            return
        elif action == "block":
            self.use_block_item()
            return
        elif action == "restart":
            self.restart_game()
            return
        elif action == "menu":
            self.return_to_menu()
            return
        # 检查UI是否有获取卡牌位置的方法
        if hasattr(self.ui, 'get_card_position'):
            card_pos = self.ui.get_card_position(mouse_pos, self.current_game)
            if card_pos:
                self.flip_card(*card_pos)
    
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
    
    def check_backend_status(self):
        """检查后端服务状态"""
        if self.backend_process.poll() is not None:
            print("后端服务已停止，尝试重启...")
            self.start_backend_service()
    
    def authenticate_user(self, username, password):
        """认证用户"""
        try:
            # 先登录获取token
            response = requests.post(
                f"{self.backend_url}/auth/login",
                json={"username": username, "password": password},
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                access_token = data.get("access_token")
                if access_token:
                    # 使用token获取用户信息
                    headers = {"Authorization": f"Bearer {access_token}"}
                    user_response = requests.get(
                        f"{self.backend_url}/auth/me",
                        headers=headers,
                        timeout=5
                    )
                    if user_response.status_code == 200:
                        user_data = user_response.json()
                        self.user_logged_in = True
                        self.username = user_data.get("username", username)
                        self.points = user_data.get("points", 0)
                        self.return_to_menu()
                        print("登录成功！")
                    else:
                        # 如果获取用户信息失败，至少保存token和用户名
                        self.user_logged_in = True
                        self.username = username
                        self.points = 0
                        self.return_to_menu()
                        print("登录成功！")
                else:
                    if hasattr(self.ui, 'show_message'):
                        self.ui.show_message("登录失败", "服务器响应异常")
            else:
                error_detail = "用户名或密码错误"
                try:
                    error_data = response.json()
                    if "detail" in error_data:
                        error_detail = error_data["detail"]
                except:
                    pass
                if hasattr(self.ui, 'show_message'):
                    self.ui.show_message("登录失败", error_detail)
        except Exception as e:
            print(f"登录请求失败: {e}")
            if hasattr(self.ui, 'show_message'):
                self.ui.show_message("登录失败", "网络错误")
    
    def register_user(self, username, email, password):
        """注册用户"""
        try:
            if not email or not email.strip():
                if hasattr(self.ui, 'show_message'):
                    self.ui.show_message("注册失败", "请输入邮箱")
                return
            response = requests.post(
                f"{self.backend_url}/auth/register",
                json={"username": username, "email": email, "password": password},
                timeout=5
            )
            if response.status_code == 200 or response.status_code == 201:
                if hasattr(self.ui, 'show_message'):
                    self.ui.show_message("注册成功", "请登录")
                self.show_login()
            else:
                error_detail = "注册失败"
                try:
                    error_data = response.json()
                    if "detail" in error_data:
                        error_detail = error_data["detail"]
                except:
                    pass
                if hasattr(self.ui, 'show_message'):
                    self.ui.show_message("注册失败", error_detail)
        except Exception as e:
            print(f"注册请求失败: {e}")
            if hasattr(self.ui, 'show_message'):
                self.ui.show_message("注册失败", "网络错误")
    
    def buy_delay_item(self):
        """购买延时道具"""
        if not self.user_logged_in:
            if hasattr(self.ui, 'show_message'):
                self.ui.show_message("错误", "请先登录")
            return
        try:
            response = requests.post(
                f"{self.backend_url}/game/buy_item",
                json={"username": self.username, "item": "delay"},
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                self.points = data.get("points", self.points)
                if hasattr(self.ui, 'show_message'):
                    self.ui.show_message("购买成功", "延时道具已购买")
                self.show_shop()
            else:
                if hasattr(self.ui, 'show_message'):
                    self.ui.show_message("购买失败", "积分不足或网络错误")
        except Exception as e:
            print(f"购买延时道具失败: {e}")
            if hasattr(self.ui, 'show_message'):
                self.ui.show_message("购买失败", "网络错误")
    
    def buy_block_item(self):
        """购买阻挡道具"""
        if not self.user_logged_in:
            if hasattr(self.ui, 'show_message'):
                self.ui.show_message("错误", "请先登录")
            return
        try:
            response = requests.post(
                f"{self.backend_url}/game/buy_item",
                json={"username": self.username, "item": "block"},
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                self.points = data.get("points", self.points)
                if hasattr(self.ui, 'show_message'):
                    self.ui.show_message("购买成功", "阻挡道具已购买")
                self.show_shop()
            else:
                if hasattr(self.ui, 'show_message'):
                    self.ui.show_message("购买失败", "积分不足或网络错误")
        except Exception as e:
            print(f"购买阻挡道具失败: {e}")
            if hasattr(self.ui, 'show_message'):
                self.ui.show_message("购买失败", "网络错误")
    
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
        """显示历史记录界面"""
        self.game_state = "history"
        # 实现获取和渲染历史记录
        if hasattr(self.ui, 'render_history_interface'):
            self.ui.render_history_interface([])
    
    def show_leaderboard(self):
        """显示排行榜"""
        self.game_state = "leaderboard"
        if self.backend_ready:
            self.load_leaderboard()
    
    def load_leaderboard(self):
        """从后端加载排行榜数据"""
        try:
            response = requests.get(f"{self.backend_url}/game/leaderboard?game_mode=simple&limit=10", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.leaderboard_data = data
                if hasattr(self.ui, 'render_leaderboard_interface'):
                    self.ui.render_leaderboard_interface(self.leaderboard_data)
            else:
                if hasattr(self.ui, 'show_message'):
                    self.ui.show_message("排行榜加载失败", "请稍后再试")
        except Exception as e:
            print(f"加载排行榜失败: {e}")
            if hasattr(self.ui, 'show_message'):
                self.ui.show_message("排行榜加载失败", "网络错误")
    
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
        if self.current_game and hasattr(self.current_game, 'use_item_delay'):
            self.current_game.use_item_delay(5)
            self.step_count += 1
            if self.backend_ready:
                self.upload_game_step()
    
    def use_block_item(self):
        if self.current_game and hasattr(self.current_game, 'use_item_block_shuffle'):
            self.current_game.use_item_block_shuffle(5)
            self.step_count += 1
            if self.backend_ready:
                self.upload_game_step()
    
    def flip_card(self, row, col):
        """翻牌操作"""
        try:
            need_hide = self.current_game.flip_card(row, col)
            self.step_count += 1
            if self.backend_ready:
                self.upload_game_step()
            
            if need_hide:
                # 配对成功
                print("配对成功！")
                self.handle_pair_matched()
            else:
                # 检查是否需要设置计时器
                if self.is_second_flip():
                    self.waiting_to_hide = True
                    self.flip_timer = pygame.time.get_ticks()
            
            # 检查游戏是否完成
            if self.current_game.is_completed():
                self.game_state = "victory"
                print("游戏完成！")
                self.upload_game_result("victory")
        except Exception as e:
            print(f"翻牌错误: {e}")
    
    def is_second_flip(self):
        """检查是否是第二次翻牌"""
        return (hasattr(self.current_game, '_first_selected') and 
                self.current_game._first_selected is not None and
                self.current_game._second_selected is None)
    
    def handle_pair_matched(self):
        """处理配对成功"""
        # 实现配对成功的缩放反馈动画
        if hasattr(self.current_game, 'score'):
            self.points += self.current_game.score  # 假设游戏有分数属性
    
    def update_game_state(self):
        """更新游戏状态（如计时器等）"""
        if self.timer_active and self.game_state == "game":
            current_time = time.time()
            self.elapsed_time = int(current_time - self.start_time)
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
                        self.current_game.hide_all_flipped()
                    self.waiting_to_hide = False
    
    def upload_game_step(self):
        """上传游戏步骤到后端"""
        if not self.backend_ready or not self.user_logged_in:
            return
        try:
            result_data = {
                "username": self.username,
                "game_mode": "simple" if isinstance(self.current_game, SimpleGame) else "hard",
                "step": self.step_count,
                "timestamp": int(time.time())
            }
            response = requests.post(
                f"{self.backend_url}/game/upload_step",
                json=result_data,
                timeout=5
            )
            if response.status_code != 200:
                print(f"上传步骤失败: {response.status_code}")
        except Exception as e:
            print(f"上传步骤失败: {e}")
    
    def upload_game_result(self, result):
        """上传游戏结果到后端"""
        if not self.backend_ready or not self.user_logged_in:
            return
        try:
            game_mode = "simple" if isinstance(self.current_game, SimpleGame) else "hard"
            time_seconds = self.elapsed_time if self.timer_active else 0
            steps = self.step_count
            score = self.current_game.score if hasattr(self.current_game, 'score') else 0
            result_data = {
                "username": self.username,
                "game_mode": game_mode,
                "time_seconds": time_seconds,
                "steps": steps,
                "score": score,
                "result": result,
                "timestamp": int(time.time())
            }
            response = requests.post(
                f"{self.backend_url}/game/upload_result",
                json=result_data,
                timeout=5
            )
            if response.status_code == 200:
                print("游戏结果上传成功！")
            else:
                print(f"游戏结果上传失败: {response.status_code}")
        except Exception as e:
            print(f"上传游戏结果失败: {e}")
    
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