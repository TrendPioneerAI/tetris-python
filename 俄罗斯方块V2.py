import pygame
import random

# 初始化
pygame.init()

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
MAGENTA = (255, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)

# 游戏设置
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SCREEN_WIDTH = BLOCK_SIZE * (GRID_WIDTH + 6)
SCREEN_HEIGHT = BLOCK_SIZE * GRID_HEIGHT

# 方块形状
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]]   # Z
]

COLORS = [CYAN, YELLOW, MAGENTA, ORANGE, BLUE, GREEN, RED]

class Tetris:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("俄罗斯方块")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('simsun', 24)
        
        # 游戏状态
        self.state = "menu"  # menu, playing, paused, game_over
        self.fade_alpha = 255  # 渐入效���
        self.animation_lines = []  # 消除行动画
        
        self.reset_game()
        self.load_high_score()

    def reset_game(self):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.game_over = False
        self.paused = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fade_alpha = 255

    def load_high_score(self):
        try:
            with open('highscore.txt', 'r') as f:
                self.high_score = int(f.read())
        except:
            self.high_score = 0

    def save_high_score(self):
        with open('highscore.txt', 'w') as f:
            f.write(str(self.high_score))

    def new_piece(self):
        shape = random.choice(SHAPES)
        color = COLORS[SHAPES.index(shape)]
        x = GRID_WIDTH // 2 - len(shape[0]) // 2
        y = 0
        return {'shape': shape, 'x': x, 'y': y, 'color': color}

    def valid_move(self, piece, x, y):
        for i, row in enumerate(piece['shape']):
            for j, cell in enumerate(row):
                if cell:
                    if (y + i >= GRID_HEIGHT or 
                        x + j < 0 or 
                        x + j >= GRID_WIDTH or 
                        y + i >= 0 and self.grid[y + i][x + j]):
                        return False
        return True

    def merge_piece(self):
        for i, row in enumerate(self.current_piece['shape']):
            for j, cell in enumerate(row):
                if cell:
                    self.grid[self.current_piece['y'] + i][self.current_piece['x'] + j] = self.current_piece['color']

    def remove_lines(self):
        lines = []
        for i in range(GRID_HEIGHT):
            if all(self.grid[i]):
                lines.append(i)
                
        if lines:
            # 添加消除行动画
            for line in lines:
                self.animation_lines.append({
                    'y': line,
                    'alpha': 255,
                    'width': GRID_WIDTH * BLOCK_SIZE
                })
            
            self.lines_cleared += len(lines)
            self.score += len(lines) * 100 * self.level
            self.level = self.lines_cleared // 10 + 1
            
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
            
            pygame.time.delay(100)
            
            for line in sorted(lines, reverse=True):
                del self.grid[line]
                self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])

    def rotate_piece(self):
        shape = self.current_piece['shape']
        rotated = list(zip(*shape[::-1]))
        if self.valid_move({'shape': rotated, 'x': self.current_piece['x'], 'y': self.current_piece['y']},
                          self.current_piece['x'], self.current_piece['y']):
            self.current_piece['shape'] = rotated

    def draw_menu(self):
        self.screen.fill(BLACK)
        
        # 标题
        title = self.font.render("俄罗斯方块", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3))
        self.screen.blit(title, title_rect)
        
        # 菜单选项
        menu_items = ["按空格键开始游戏", "按ESC键退出"]
        for i, item in enumerate(menu_items):
            text = self.font.render(item, True, WHITE)
            rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + i * 40))
            self.screen.blit(text, rect)
        
        pygame.display.flip()

    def draw_game(self):
        self.screen.fill(BLACK)
        
        # 绘制网格中的方块
        for i in range(GRID_HEIGHT):
            for j in range(GRID_WIDTH):
                if self.grid[i][j]:
                    pygame.draw.rect(self.screen, self.grid[i][j],
                                   (j * BLOCK_SIZE, i * BLOCK_SIZE, 
                                    BLOCK_SIZE - 1, BLOCK_SIZE - 1))

        # 绘制当前方块
        if self.current_piece:
            for i, row in enumerate(self.current_piece['shape']):
                for j, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(self.screen, self.current_piece['color'],
                                       ((self.current_piece['x'] + j) * BLOCK_SIZE,
                                        (self.current_piece['y'] + i) * BLOCK_SIZE,
                                        BLOCK_SIZE - 1, BLOCK_SIZE - 1))

        # 绘制信息
        info_x = GRID_WIDTH * BLOCK_SIZE + 20
        texts = [
            f'分数: {self.score}',
            f'等级: {self.level}',
            f'最高分: {self.high_score}',
            f'已消除: {self.lines_cleared}行',
            '下一个:'
        ]
        
        for i, text in enumerate(texts):
            surface = self.font.render(text, True, WHITE)
            self.screen.blit(surface, (info_x, 30 + i * 40))

        # 绘制下一个方块预览
        next_x = GRID_WIDTH * BLOCK_SIZE + 20
        next_y = 240
        for i, row in enumerate(self.next_piece['shape']):
            for j, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, self.next_piece['color'],
                                   (next_x + j * BLOCK_SIZE,
                                    next_y + i * BLOCK_SIZE,
                                    BLOCK_SIZE - 1, BLOCK_SIZE - 1))

        # 绘制消除行动画
        for anim in self.animation_lines[:]:
            s = pygame.Surface((anim['width'], BLOCK_SIZE))
            s.fill(WHITE)
            s.set_alpha(anim['alpha'])
            self.screen.blit(s, (0, anim['y'] * BLOCK_SIZE))
            
            anim['alpha'] -= 15
            anim['width'] = max(0, anim['width'] - 20)
            
            if anim['alpha'] <= 0 or anim['width'] <= 0:
                self.animation_lines.remove(anim)

        # 渐入效果
        if self.fade_alpha > 0:
            fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            fade_surface.fill(BLACK)
            fade_surface.set_alpha(self.fade_alpha)
            self.screen.blit(fade_surface, (0, 0))
            self.fade_alpha = max(0, self.fade_alpha - 5)

        # 绘制暂停/游戏结束状态
        if self.paused or self.game_over:
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            s.set_alpha(128)
            s.fill(BLACK)
            self.screen.blit(s, (0, 0))
            
            text = '已暂停' if self.paused else '游戏结束'
            text_surface = self.font.render(text, True, WHITE)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(text_surface, text_rect)
            
            if self.game_over:
                restart_text = self.font.render('按R键重新开始', True, WHITE)
                restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40))
                self.screen.blit(restart_text, restart_rect)

        pygame.display.flip()

    def run(self):
        while True:
            if self.state == "menu":
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            self.state = "playing"
                            self.reset_game()
                        elif event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            return
                self.draw_menu()
                
            elif self.state == "playing":
                fall_time = 0
                while not self.game_over:
                    fall_speed = max(50 - (self.level * 5), 10)
                    fall_time += 1
                    
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            return
                            
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_r and self.game_over:
                                self.reset_game()
                                continue
                            if event.key == pygame.K_ESCAPE:
                                self.state = "menu"
                                break
                                
                            if not self.paused and not self.game_over:
                                if event.key == pygame.K_LEFT:
                                    if self.valid_move(self.current_piece, self.current_piece['x'] - 1, self.current_piece['y']):
                                        self.current_piece['x'] -= 1
                                if event.key == pygame.K_RIGHT:
                                    if self.valid_move(self.current_piece, self.current_piece['x'] + 1, self.current_piece['y']):
                                        self.current_piece['x'] += 1
                                if event.key == pygame.K_DOWN:
                                    if self.valid_move(self.current_piece, self.current_piece['x'], self.current_piece['y'] + 1):
                                        self.current_piece['y'] += 1
                                if event.key == pygame.K_UP:
                                    self.rotate_piece()
                            if event.key == pygame.K_SPACE:
                                self.paused = not self.paused

                    if not self.paused and not self.game_over:
                        if fall_time >= fall_speed:
                            fall_time = 0
                            if self.valid_move(self.current_piece, self.current_piece['x'], self.current_piece['y'] + 1):
                                self.current_piece['y'] += 1
                            else:
                                self.merge_piece()
                                self.remove_lines()
                                self.current_piece = self.next_piece
                                self.next_piece = self.new_piece()
                                if not self.valid_move(self.current_piece, self.current_piece['x'], self.current_piece['y']):
                                    self.game_over = True

                    self.draw_game()
                    self.clock.tick(60)

if __name__ == '__main__':
    game = Tetris()
    game.run()
