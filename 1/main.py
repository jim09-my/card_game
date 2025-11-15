"""
main.py - 记忆迷宫游戏主程序
"""
import pygame
import sys
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
        self.game_state = "menu"  # menu, game, victory
        self.running = True
        self.clock = pygame.time.Clock()
        
        # 游戏计时
        self.flip_timer = 0
        self.waiting_to_hide = False
    
    def run(self):
        """主游戏循环"""
        while self.running:
            # 处理事件
            self.handle_events()
            
            # 更新游戏状态
            self.update_game_state()
            
            # 渲染界面
            self.ui.render(self.game_state, self.current_game, self.waiting_to_hide)
            
            # 控制帧率
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

    def handle_events(self):
        """处理所有事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                self.handle_keyboard(event.key)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键点击
                    self.handle_mouse_click(pygame.mouse.get_pos())
    
    def handle_keyboard(self, key):
        """处理键盘事件"""
        if key == pygame.K_ESCAPE:
            if self.game_state in ["game", "victory", "defeat"]:
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
        elif self.game_state == "game":
            self.handle_game_click(mouse_pos)
        elif self.game_state == "victory":
            self.handle_victory_click(mouse_pos)
        elif self.game_state == "defeat":
            self.handle_victory_click(mouse_pos)
    
    def handle_menu_click(self, mouse_pos):
        """处理菜单界面的点击"""
        action = self.ui.get_menu_action(mouse_pos)
        
        if action == "start_game":
            self.start_simple_mode()
        elif action == "hard_game":
            self.start_hard_mode()
        elif action == "exit":
            self.running = False
    
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
    
    def flip_card(self, row, col):
        """翻牌操作"""
        try:
            need_hide = self.current_game.flip_card(row, col)
            
            if need_hide:
                # 配对成功
                print("Pair matched!")
            else:
                # 检查是否需要设置计时器
                if self.is_second_flip():
                    self.waiting_to_hide = True
                    self.flip_timer = pygame.time.get_ticks()
            
            # 检查游戏是否完成
            if self.current_game.is_completed():
                self.game_state = "victory"
                print("Game completed!")
                
        except Exception as e:
            print(f"Flip card error: {e}")
    
    def is_second_flip(self):
        """检查是否是第二次翻牌"""
        return (hasattr(self.current_game, '_first_selected') and 
                self.current_game._first_selected is None)
    
    def update_game_state(self):
        """更新游戏状态（如计时器等）"""
        reveal_ms = 1000
        if self.current_game and hasattr(self.current_game, 'get_reveal_duration_ms'):
            reveal_ms = self.current_game.get_reveal_duration_ms()
        if self.waiting_to_hide and pygame.time.get_ticks() - self.flip_timer > reveal_ms:
            if self.current_game:
                self.current_game.hide_all_flipped()
            self.waiting_to_hide = False
        if self.current_game and hasattr(self.current_game, 'is_time_over') and self.current_game.is_time_over():
            self.game_state = "defeat"
            print("Time over! You lost.")
    
    def start_simple_mode(self):
        """开始简单模式游戏"""
        try:
            self.current_game = SimpleGame(4, 4)
            self.game_state = "game"
            self.waiting_to_hide = False
            print("Simple mode started!")
        except Exception as e:
            print(f"Start game failed: {e}")
    
    def start_hard_mode(self):
        """开始困难模式游戏"""
        try:
            # 使用动态迷宫困难模式（图结构约束翻牌）
            self.current_game = DynamicMazeGame(7, 7)
            self.game_state = "game"
            self.waiting_to_hide = False
            print("Hard mode started! (Dynamic Maze)")
        except Exception as e:
            print(f"Start hard mode failed: {e}")
    
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

    def use_block_item(self):
        if self.current_game and hasattr(self.current_game, 'use_item_block_shuffle'):
            self.current_game.use_item_block_shuffle(5)
    
    def return_to_menu(self):
        """返回主菜单"""
        self.game_state = "menu"
        self.current_game = None
        self.waiting_to_hide = False

def main():
    """程序入口点"""
    try:
        game = MemoryMatchGame()
        game.run()
    except Exception as e:
        print(f"Program error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()