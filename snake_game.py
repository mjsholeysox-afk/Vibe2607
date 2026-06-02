#cmd
#pip install pygame 
import pygame
import random
import sys

# 게임 설정
CELL_SIZE = 20
GRID_WIDTH = 32  # 640 / 20
GRID_HEIGHT = 24  # 480 / 20
WIDTH = CELL_SIZE * GRID_WIDTH
HEIGHT = CELL_SIZE * GRID_HEIGHT
FPS = 10

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PLAYER_COLOR = (50, 205, 50)
AI_COLOR = (65, 105, 225)
RED = (255, 69, 0)

# 생성할 사과(음식) 개수
NUM_FOODS = 3


class Snake:
    def __init__(self, body=None, direction=(1, 0), color=PLAYER_COLOR):
        if body is None:
            self.body = [(GRID_WIDTH // 2, GRID_HEIGHT // 2),
                         (GRID_WIDTH // 2 - 1, GRID_HEIGHT // 2),
                         (GRID_WIDTH // 2 - 2, GRID_HEIGHT // 2)]
        else:
            self.body = list(body)
        self.direction = direction
        self.grow_pending = 0
        self.alive = True
        self.color = color

    def change_direction(self, new_dir):
        # 역방향 이동 금지
        if (new_dir[0] == -self.direction[0] and new_dir[1] == -self.direction[1]):
            return
        self.direction = new_dir

    def move(self):
        if not self.alive:
            return
        head_x, head_y = self.body[0]
        dx, dy = self.direction
        new_head = ((head_x + dx) % GRID_WIDTH, (head_y + dy) % GRID_HEIGHT)
        self.body.insert(0, new_head)
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()

    def grow(self):
        self.grow_pending += 1

    def collides_with_self(self):
        return self.body[0] in self.body[1:]

    def draw(self, surface):
        for segment in self.body:
            x, y = segment
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(surface, self.color, rect)


class AISnake(Snake):
    def __init__(self, body=None, direction=(-1, 0), color=AI_COLOR):
        super().__init__(body=body, direction=direction, color=color)

    def decide_direction(self, food_pos, occupied):
        # 단순한 휴리스틱: 먹이에 대한 맨해튼 거리 최소화, 안전한 칸 우선
        if not self.alive:
            return
        possible_dirs = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        # 금지: 역방향
        possible_dirs = [d for d in possible_dirs if not (d[0] == -self.direction[0] and d[1] == -self.direction[1])]

        best = None
        best_dist = None
        head_x, head_y = self.body[0]
        for d in possible_dirs:
            nx = (head_x + d[0]) % GRID_WIDTH
            ny = (head_y + d[1]) % GRID_HEIGHT
            if (nx, ny) in occupied:
                continue
            dist = abs(nx - food_pos[0]) + abs(ny - food_pos[1])
            if best is None or dist < best_dist:
                best = d
                best_dist = dist

        if best is not None:
            self.direction = best
        else:
            # 안전한 칸이 없으면 역방향만 피して 임의 선택
            if possible_dirs:
                self.direction = possible_dirs[0]


class Food:
    def __init__(self, snakes, occupied_extra=None):
        self.position = (0, 0)
        self.spawn(snakes, occupied_extra)

    def spawn(self, snakes, occupied_extra=None):
        occupied = set()
        for s in snakes:
            occupied.update(s.body)
        if occupied_extra:
            occupied.update(occupied_extra)
        attempts = 0
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            attempts += 1
            if (x, y) not in occupied:
                self.position = (x, y)
                return
            if attempts > GRID_WIDTH * GRID_HEIGHT:
                # 전체 그리드가 차면 그냥 반환
                self.position = (0, 0)
                return

    def draw(self, surface):
        x, y = self.position
        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, RED, rect)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Snake - Player vs AI")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 28)
        self.reset()

    def reset(self):
        # 플레이어 왼쪽, AI 오른쪽에서 시작
        player_body = [(GRID_WIDTH // 4, GRID_HEIGHT // 2), (GRID_WIDTH // 4 - 1, GRID_HEIGHT // 2), (GRID_WIDTH // 4 - 2, GRID_HEIGHT // 2)]
        ai_body = [(GRID_WIDTH * 3 // 4, GRID_HEIGHT // 2), (GRID_WIDTH * 3 // 4 + 1, GRID_HEIGHT // 2), (GRID_WIDTH * 3 // 4 + 2, GRID_HEIGHT // 2)]
        self.player = Snake(body=player_body, direction=(1, 0), color=PLAYER_COLOR)
        self.ai = AISnake(body=ai_body, direction=(-1, 0), color=AI_COLOR)
        # 여러 개의 음식 생성, 겹치지 않도록 순차적으로 생성
        self.foods = []
        occupied_extra = set()
        for _ in range(NUM_FOODS):
            f = Food([self.player, self.ai], occupied_extra=occupied_extra)
            self.foods.append(f)
            occupied_extra.add(f.position)
        self.score_player = 0
        self.score_ai = 0
        self.game_over = False

    def draw_grid(self):
        for x in range(0, WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, (40, 40, 40), (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, (40, 40, 40), (0, y), (WIDTH, y))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.player.change_direction((0, -1))
                elif event.key == pygame.K_DOWN:
                    self.player.change_direction((0, 1))
                elif event.key == pygame.K_LEFT:
                    self.player.change_direction((-1, 0))
                elif event.key == pygame.K_RIGHT:
                    self.player.change_direction((1, 0))
                elif event.key == pygame.K_r and self.game_over:
                    self.reset()

    def update(self):
        if self.game_over:
            return

        # AI 결정: 현재 점유 셀(두 뱀의 몸 및 음식 위치)을 고려
        occupied = set(self.player.body + self.ai.body)
        occupied.update([f.position for f in self.foods])
        # AI는 가장 가까운 음식을 목표로 삼음
        head = self.ai.body[0]
        nearest = min(self.foods, key=lambda f: abs(f.position[0]-head[0]) + abs(f.position[1]-head[1]))
        self.ai.decide_direction(nearest.position, occupied)

        # 이동
        self.player.move()
        self.ai.move()

        # 음식 섭취 처리 (여러 음식 체크)
        for f in self.foods:
            if self.player.alive and self.player.body[0] == f.position:
                self.player.grow()
                self.score_player += 1
                # 재생성: 다른 음식 위치와 뱀 위치를 고려
                other_food_positions = {of.position for of in self.foods if of is not f}
                f.spawn([self.player, self.ai], occupied_extra=other_food_positions)

            if self.ai.alive and self.ai.body[0] == f.position:
                self.ai.grow()
                self.score_ai += 1
                other_food_positions = {of.position for of in self.foods if of is not f}
                f.spawn([self.player, self.ai], occupied_extra=other_food_positions)

        # 충돌 검사
        # 자기 충돌
        if self.player.alive and self.player.collides_with_self():
            self.player.alive = False

        if self.ai.alive and self.ai.collides_with_self():
            self.ai.alive = False

        # 서로 충돌: 머리가 상대 몸에 닿음
        if self.player.alive and self.player.body[0] in self.ai.body[1:]:
            self.player.alive = False

        if self.ai.alive and self.ai.body[0] in self.player.body[1:]:
            self.ai.alive = False

        # 머리끼리 충돌
        if self.player.body[0] == self.ai.body[0]:
            self.player.alive = False
            self.ai.alive = False

        # 게임 오버 조건: 둘 다 죽으면 종료
        if not self.player.alive and not self.ai.alive:
            self.game_over = True

    def draw(self):
        self.screen.fill(BLACK)
        self.draw_grid()
        for f in self.foods:
            f.draw(self.screen)
        self.player.draw(self.screen)
        self.ai.draw(self.screen)

        score_surf = self.font.render(f"Player: {self.score_player}", True, WHITE)
        self.screen.blit(score_surf, (10, 10))
        score_surf2 = self.font.render(f"AI: {self.score_ai}", True, WHITE)
        rect = score_surf2.get_rect(topright=(WIDTH - 10, 10))
        self.screen.blit(score_surf2, rect)

        if self.game_over:
            over_surf = self.font.render("Game Over - Press R to Restart", True, WHITE)
            rect = over_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            self.screen.blit(over_surf, rect)
        pygame.display.flip()

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)


if __name__ == "__main__":
    Game().run()
