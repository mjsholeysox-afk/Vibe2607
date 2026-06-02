import tkinter as tk
from tkinter import messagebox
from random import choice

COLS = 10
ROWS = 20
CELL_SIZE = 30

SHAPES = {
    'i': [
        [(0, 1), (1, 1), (2, 1), (3, 1)],
        [(2, 0), (2, 1), (2, 2), (2, 3)],
    ],
    'j': [
        [(0, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (2, 2)],
        [(1, 0), (1, 1), (0, 2), (1, 2)],
    ],
    'l': [
        [(2, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (2, 2)],
        [(0, 1), (1, 1), (2, 1), (0, 2)],
        [(0, 0), (1, 0), (1, 1), (1, 2)],
    ],
    'o': [
        [(1, 0), (2, 0), (1, 1), (2, 1)],
    ],
    's': [
        [(1, 0), (2, 0), (0, 1), (1, 1)],
        [(1, 0), (1, 1), (2, 1), (2, 2)],
    ],
    't': [
        [(1, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (1, 2)],
        [(1, 0), (0, 1), (1, 1), (1, 2)],
    ],
    'z': [
        [(0, 0), (1, 0), (1, 1), (2, 1)],
        [(2, 0), (1, 1), (2, 1), (1, 2)],
    ],
}

COLORS = {
    'i': '#06b6d4',
    'j': '#2563eb',
    'l': '#f97316',
    'o': '#eab308',
    's': '#22c55e',
    't': '#a855f7',
    'z': '#ef4444',
}

LINE_SCORE = [0, 100, 300, 500, 800]


class Tetris:
    def __init__(self, root):
        self.root = root
        root.title('파이썬 테트리스')
        root.configure(bg='#0f172a')
        root.resizable(False, False)

        self.board = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.score = 0
        self.lines = 0
        self.level = 1
        self.drop_interval = 800
        self.timer_id = None
        self.current_piece = None
        self.next_piece = None
        self.is_paused = False
        self.game_over = False
        self.level_up_active = False
        self.level_up_ticks = 0
        self.level_up_animation_id = None
        self.clown_x = 40
        self.clown_dx = 6

        self.create_widgets()
        self.draw_board()
        self.root.bind('<Key>', self.on_key_press)

    def create_widgets(self):
        container = tk.Frame(self.root, bg='#0f172a', padx=20, pady=20)
        container.pack()

        board_frame = tk.Frame(container, bg='#0f172a')
        board_frame.grid(row=0, column=0)

        status_frame = tk.Frame(container, bg='#0f172a')
        status_frame.grid(row=0, column=1, sticky='n', padx=(20, 0))

        self.canvas = tk.Canvas(
            board_frame,
            width=COLS * CELL_SIZE,
            height=ROWS * CELL_SIZE,
            bg='#111827',
            bd=0,
            highlightthickness=0,
        )
        self.canvas.pack()

        self.overlay_canvas = tk.Canvas(
            board_frame,
            width=COLS * CELL_SIZE,
            height=ROWS * CELL_SIZE,
            bg='#111827',
            bd=0,
            highlightthickness=0,
        )
        self.overlay_canvas.place(x=0, y=0)

        title = tk.Label(status_frame, text='테트리스', fg='#e2e8f0', bg='#0f172a', font=('Segoe UI', 18, 'bold'))
        title.pack(pady=(0, 12))

        self.score_label = self.create_status_label(status_frame, '점수', self.score)
        self.lines_label = self.create_status_label(status_frame, '줄', self.lines)
        self.level_label = self.create_status_label(status_frame, '레벨', self.level)

        preview_frame = tk.Frame(status_frame, bg='#111827', bd=2, relief='solid')
        preview_frame.pack(pady=(12, 0), fill='x')

        preview_title = tk.Label(preview_frame, text='다음 블럭', fg='#38bdf8', bg='#111827', font=('Segoe UI', 11, 'bold'))
        preview_title.pack(anchor='w', padx=10, pady=(8, 4))

        self.preview_canvas = tk.Canvas(
            preview_frame,
            width=4 * CELL_SIZE,
            height=4 * CELL_SIZE,
            bg='#0f172a',
            bd=0,
            highlightthickness=0,
        )
        self.preview_canvas.pack(padx=10, pady=(0, 10))

        button_frame = tk.Frame(status_frame, bg='#0f172a')
        button_frame.pack(pady=(12, 0), fill='x')

        start_button = tk.Button(
            button_frame,
            text='게임 시작',
            command=self.start_game,
            bg='#1e293b',
            fg='#e2e8f0',
            activebackground='#334155',
            padx=12,
            pady=10,
            bd=0,
            relief='raised',
            cursor='hand2',
        )
        start_button.pack(fill='x', pady=(0, 8))

        self.pause_button = tk.Button(
            button_frame,
            text='일시정지',
            command=self.toggle_pause,
            bg='#1e293b',
            fg='#e2e8f0',
            activebackground='#334155',
            padx=12,
            pady=10,
            bd=0,
            relief='raised',
            cursor='hand2',
            state='disabled',
        )
        self.pause_button.pack(fill='x')

        instruction_frame = tk.Frame(status_frame, bg='#111827', bd=2, relief='solid')
        instruction_frame.pack(pady=(16, 0), fill='x')

        instr_title = tk.Label(instruction_frame, text='조작법', fg='#38bdf8', bg='#111827', font=('Segoe UI', 11, 'bold'))
        instr_title.pack(anchor='w', padx=10, pady=(8, 0))

        for text in ['← / → : 이동', '↑ : 회전', '↓ : 하강 가속', '스페이스 : 즉시 떨어뜨리기']:
            label = tk.Label(instruction_frame, text=text, fg='#e2e8f0', bg='#111827', anchor='w', font=('Segoe UI', 10))
            label.pack(fill='x', padx=10)

    def create_status_label(self, parent, title, value):
        frame = tk.Frame(parent, bg='#111827', bd=2, relief='solid')
        frame.pack(fill='x', pady=4)
        title_label = tk.Label(frame, text=title, fg='#94a3b8', bg='#111827', font=('Segoe UI', 10))
        title_label.pack(side='left', padx=10, pady=10)
        value_label = tk.Label(frame, text=str(value), fg='#e2e8f0', bg='#111827', font=('Segoe UI', 10, 'bold'))
        value_label.pack(side='right', padx=10, pady=10)
        return value_label

    def start_game(self):
        self.board = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.score = 0
        self.lines = 0
        self.level = 1
        self.drop_interval = 800
        self.is_paused = False
        self.game_over = False
        self.pause_button.config(text='일시정지', state='normal')
        self.next_piece = self.generate_piece()
        self.current_piece = self.next_piece
        self.next_piece = self.generate_piece()
        if self.collide(self.current_piece):
            self.end_game()
            return
        self.update_status()
        self.draw_board()
        self.schedule_drop()

    def toggle_pause(self):
        if self.game_over:
            return
        self.is_paused = not self.is_paused
        self.pause_button.config(text='재개' if self.is_paused else '일시정지')

    def on_key_press(self, event):
        if self.game_over or self.current_piece is None:
            return

        key = event.keysym
        if key == 'Left':
            self.move_piece(-1, 0)
        elif key == 'Right':
            self.move_piece(1, 0)
        elif key == 'Down':
            self.move_piece(0, 1)
        elif key == 'Up':
            self.rotate_piece()
        elif key == 'space':
            self.hard_drop()

    def new_piece(self):
        self.current_piece = self.next_piece
        self.next_piece = self.generate_piece()
        if self.collide(self.current_piece):
            self.end_game()

    def generate_piece(self):
        shape_type = choice(list(SHAPES.keys()))
        return {
            'type': shape_type,
            'shape': SHAPES[shape_type],
            'rotation': 0,
            'x': 3,
            'y': -1,
        }

    def get_cells(self, piece):
        return [
            (piece['x'] + x, piece['y'] + y)
            for x, y in piece['shape'][piece['rotation']]
        ]

    def collide(self, piece, dx=0, dy=0, rotation=None):
        rotation_index = piece['rotation'] if rotation is None else rotation
        shape = piece['shape'][rotation_index]
        for x, y in shape:
            new_x = piece['x'] + x + dx
            new_y = piece['y'] + y + dy
            if new_x < 0 or new_x >= COLS or new_y >= ROWS:
                return True
            if new_y >= 0 and self.board[new_y][new_x] is not None:
                return True
        return False

    def move_piece(self, dx, dy):
        if self.current_piece is None or self.game_over:
            return
        if not self.collide(self.current_piece, dx, dy):
            self.current_piece['x'] += dx
            self.current_piece['y'] += dy
            self.draw_board()

    def rotate_piece(self):
        if self.current_piece is None or self.game_over:
            return
        next_rotation = (self.current_piece['rotation'] + 1) % len(self.current_piece['shape'])
        if not self.collide(self.current_piece, 0, 0, next_rotation):
            self.current_piece['rotation'] = next_rotation
        else:
            for dx in (-1, 1, -2, 2):
                if not self.collide(self.current_piece, dx, 0, next_rotation):
                    self.current_piece['x'] += dx
                    self.current_piece['rotation'] = next_rotation
                    break
        self.draw_board()

    def merge_piece(self):
        for x, y in self.get_cells(self.current_piece):
            if 0 <= y < ROWS and 0 <= x < COLS:
                self.board[y][x] = self.current_piece['type']

    def clear_lines(self):
        cleared = 0
        row = ROWS - 1
        while row >= 0:
            if all(cell is not None for cell in self.board[row]):
                del self.board[row]
                self.board.insert(0, [None for _ in range(COLS)])
                cleared += 1
            else:
                row -= 1

        if cleared > 0:
            old_level = self.level
            self.score += LINE_SCORE[cleared]
            self.lines += cleared
            self.level = min(20, 1 + self.lines // 10)
            self.drop_interval = max(100, 800 - (self.level - 1) * 60)
            if self.level > old_level:
                self.show_level_up()

    def drop_step(self):
        if self.game_over or self.is_paused or self.current_piece is None:
            return

        if not self.collide(self.current_piece, 0, 1):
            self.current_piece['y'] += 1
        else:
            self.merge_piece()
            self.clear_lines()
            self.new_piece()

        self.update_status()
        self.draw_board()

    def hard_drop(self):
        if self.current_piece is None or self.game_over:
            return
        while not self.collide(self.current_piece, 0, 1):
            self.current_piece['y'] += 1
        self.drop_step()

    def end_game(self):
        self.game_over = True
        self.pause_button.config(state='disabled')
        messagebox.showinfo('게임 오버', f'게임 오버! 점수: {self.score}')

    def schedule_drop(self):
        if self.timer_id is not None:
            self.root.after_cancel(self.timer_id)
        self.timer_id = self.root.after(self.drop_interval, self.tick)

    def tick(self):
        if not self.game_over and not self.is_paused:
            self.drop_step()
        self.schedule_drop()

    def update_status(self):
        self.score_label.config(text=str(self.score))
        self.lines_label.config(text=str(self.lines))
        self.level_label.config(text=str(self.level))

    def draw_board(self):
        self.canvas.delete('all')
        for row in range(ROWS):
            for col in range(COLS):
                cell_color = '#0f172a'
                if self.board[row][col] is not None:
                    cell_color = COLORS[self.board[row][col]]
                self.draw_cell(col, row, cell_color)

        if self.current_piece is not None:
            for x, y in self.get_cells(self.current_piece):
                if 0 <= y < ROWS and 0 <= x < COLS:
                    self.draw_cell(x, y, COLORS[self.current_piece['type']])
        self.draw_preview()

    def draw_cell(self, col, row, color):
        x1 = col * CELL_SIZE + 2
        y1 = row * CELL_SIZE + 2
        x2 = x1 + CELL_SIZE - 4
        y2 = y1 + CELL_SIZE - 4
        self.canvas.create_rectangle(
            x1,
            y1,
            x2,
            y2,
            fill=color,
            outline='#334155',
            width=1,
        )

    def draw_preview(self):
        if not hasattr(self, 'preview_canvas') or self.preview_canvas is None:
            return
        self.preview_canvas.delete('all')
        if self.next_piece is None:
            return

        preview_size = 4
        preview_cell = CELL_SIZE - 8
        cells = self.next_piece['shape'][0]
        min_x = min(x for x, y in cells)
        min_y = min(y for x, y in cells)
        for x, y in cells:
            px = x - min_x
            py = y - min_y
            x1 = px * preview_cell + 8
            y1 = py * preview_cell + 8
            x2 = x1 + preview_cell - 4
            y2 = y1 + preview_cell - 4
            self.preview_canvas.create_rectangle(
                x1,
                y1,
                x2,
                y2,
                fill=COLORS[self.next_piece['type']],
                outline='#334155',
                width=1,
            )

    def show_level_up(self):
        if self.level_up_active or self.game_over:
            return
        self.level_up_active = True
        self.level_up_ticks = 0
        self.is_paused = True
        self.clown_x = 40
        self.clown_dx = 6
        self.overlay_canvas.lift(self.canvas)
        self.animate_clown()

    def hide_level_up(self):
        self.level_up_active = False
        self.overlay_canvas.delete('all')
        self.is_paused = False
        self.update_status()

    def animate_clown(self):
        if not self.level_up_active:
            return

        self.overlay_canvas.delete('all')
        width = COLS * CELL_SIZE
        height = ROWS * CELL_SIZE
        self.overlay_canvas.create_rectangle(0, 0, width, height, fill='#000000', stipple='gray25', outline='')
        self.overlay_canvas.create_text(width // 2, 40, text='레벨 업!', fill='#f8b195', font=('Segoe UI', 24, 'bold'))
        self.overlay_canvas.create_text(width // 2, 75, text=f'레벨 {self.level}', fill='#ffffff', font=('Segoe UI', 14, 'bold'))

        face_radius = 24
        face_y = height // 2
        self.overlay_canvas.create_oval(self.clown_x - face_radius, face_y - face_radius, self.clown_x + face_radius, face_y + face_radius, fill='#ffffff', outline='#000000')
        self.overlay_canvas.create_oval(self.clown_x - 10, face_y - 10, self.clown_x - 2, face_y - 2, fill='#000000')
        self.overlay_canvas.create_oval(self.clown_x + 2, face_y - 10, self.clown_x + 10, face_y - 2, fill='#000000')
        self.overlay_canvas.create_arc(self.clown_x - 12, face_y + 4, self.clown_x + 12, face_y + 22, start=180, extent=180, style='arc', outline='#e63946', width=3)
        self.overlay_canvas.create_oval(self.clown_x - 34, face_y - 34, self.clown_x - 14, face_y - 14, fill='#f94144', outline='')
        self.overlay_canvas.create_oval(self.clown_x + 14, face_y - 34, self.clown_x + 34, face_y - 14, fill='#f94144', outline='')
        self.overlay_canvas.create_rectangle(self.clown_x - 20, face_y + 28, self.clown_x + 20, face_y + 42, fill='#f0f0f0', outline='')

        self.clown_x += self.clown_dx
        if self.clown_x < 40 or self.clown_x > width - 40:
            self.clown_dx *= -1
        self.level_up_ticks += 1
        if self.level_up_ticks >= 10:
            self.hide_level_up()
        else:
            self.level_up_animation_id = self.root.after(120, self.animate_clown)


if __name__ == '__main__':
    root = tk.Tk()
    game = Tetris(root)
    root.mainloop()
  




