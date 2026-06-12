import lib.stddraw as stddraw
from lib.picture import Picture
from lib.color import Color
import os
from game_grid import GameGrid
from tetromino import Tetromino
import random
import pygame

def load_high_score():
   try:
      with open('high_score.txt', 'r') as f:
         return int(f.read())
   except:
      return 0

def save_high_score(score):
   try:
      with open('high_score.txt', 'w') as f:
         f.write(str(score))
   except:
      pass

def main():
   pygame.mixer.init()
   pygame.mixer.music.load('sounds/background.wav')
   pygame.mixer.music.set_volume(0.05)  # 0.0 ile 1.0 arası, 0.05 = %5 ses seviyesi
   pygame.mixer.music.play(-1)  # -1 = sonsuz döngü.  
   # --- Game grid dimensions ---
   grid_height, grid_width = 20, 12
   panel_width = 5  # right panel for score & next piece

   # --- Canvas setup ---
   cell_size = 40
   canvas_height = cell_size * grid_height
   canvas_width = cell_size * (grid_width + panel_width)
   stddraw.setCanvasSize(canvas_width, canvas_height)
   stddraw.setXscale(-0.5, grid_width + panel_width - 0.5)
   stddraw.setYscale(-0.5, grid_height - 0.5)

   # Pass grid dimensions to Tetromino class
   Tetromino.grid_height = grid_height
   Tetromino.grid_width = grid_width

   # Show menu and wait for start
   display_game_menu(grid_height, grid_width, panel_width)

   # --- Game loop ---
   while True:
      high_score = load_high_score()
      # Create grid and first two tetrominoes
      grid = GameGrid(grid_height, grid_width)
      # Temayı yükle ve uygula
      theme_name = load_theme()
      theme = THEMES[theme_name]
      grid.empty_cell_color = theme['empty']
      grid.line_color = theme['line']
      grid.boundary_color = theme['boundary']
      grid.panel_color = theme['panel']
      grid.high_score = high_score
      current_tetromino = create_tetromino()
      next_tetromino = create_tetromino()
      grid.current_tetromino = current_tetromino
      game_over = False
      paused = False
      speed_counter = 0
      fall_speed = 5  # auto-fall every N frames (lower = faster)
      level=1

      while not game_over:
         # --- Input handling ---
         if stddraw.hasNextKeyTyped():
            key = stddraw.nextKeyTyped()
            if not paused:
               if key == 'left':
                  current_tetromino.move('left', grid)
               elif key == 'right':
                  current_tetromino.move('right', grid)
               elif key == 'down':
                  current_tetromino.move('down', grid)
               elif key == 'up':
                  current_tetromino.rotate(grid)
               elif key == 'space':
                  current_tetromino.hard_drop(grid)
                  # Force land immediately
                  tiles, pos = current_tetromino.get_min_bounded_tile_matrix(True)
                  game_over = grid.update_grid(tiles, pos)
                  if not game_over:
                     current_tetromino = next_tetromino
                     next_tetromino = create_tetromino()
                     grid.current_tetromino = current_tetromino
                     grid.can_hold = True
                  speed_counter = 0
                  stddraw.clearKeysTyped()
                  grid.display(next_tetromino)
                  continue

            if key == 'p' or key == 'P':
               paused = not paused
            elif key == 'c' or key == 'C':
               if grid.can_hold:
                  if grid.held_tetromino is None:
                     grid.held_tetromino = current_tetromino
                     current_tetromino = next_tetromino
                     next_tetromino = create_tetromino()
                  else:
                     grid.held_tetromino, current_tetromino = current_tetromino, grid.held_tetromino
                     current_tetromino.bottom_left_cell.y = Tetromino.grid_height - 1
                     current_tetromino.bottom_left_cell.x = random.randint(0, Tetromino.grid_width - len(current_tetromino.tile_matrix))
                  grid.current_tetromino = current_tetromino
                  grid.can_hold = False
            elif key == 'r' or key == 'R':
               game_over = True   
            stddraw.clearKeysTyped()

         if paused:
            draw_pause_screen(grid_height, grid_width, panel_width)
            stddraw.show(100)
            continue

         # --- Auto fall ---
         speed_counter += 1
         level = 1 + grid.score // 200
         fall_speed = max(1, 6 - level)
         if speed_counter >= fall_speed:
            speed_counter = 0
            success = current_tetromino.move('down', grid)
            if not success:
               # Land the tetromino
               tiles, pos = current_tetromino.get_min_bounded_tile_matrix(True)
               game_over = grid.update_grid(tiles, pos)
               if not game_over:
                  current_tetromino = next_tetromino
                  next_tetromino = create_tetromino()
                  grid.current_tetromino = current_tetromino
                  grid.can_hold = True

         # --- Win check ---
         if grid.win:
            grid.display(next_tetromino)
            display_end_screen(grid_height, grid_width, panel_width, grid.score, won=True)
            break

         # --- Draw ---
         grid.display(next_tetromino)
      if grid.score > high_score:
        high_score = grid.score
        save_high_score(high_score)
      if game_over:
         display_end_screen(grid_height, grid_width, panel_width, grid.score, won=False)

      # Ask to play again (display_end_screen returns True = restart)
      # After end screen, loop back to start a new game
      display_game_menu(grid_height, grid_width, panel_width)


def create_tetromino():
   """Create a random tetromino from all 7 types."""
   types = ['I', 'O', 'Z', 'S', 'J', 'L', 'T']
   return Tetromino(types[3])


def draw_pause_screen(grid_height, grid_width, panel_width):
   """Draw a semi-transparent pause overlay."""
   stddraw.setPenColor(Color(255, 255, 255,))
   stddraw.setFontFamily('Arial')
   stddraw.setFontSize(36)
   cx = (grid_width - 1) / 2
   cy = grid_height / 2
   stddraw.boldText(cx, cy, 'PAUSED')
   stddraw.setFontSize(16)
   stddraw.text(cx, cy - 1.5, 'Press P to continue')


def display_end_screen(grid_height, grid_width, panel_width, score, won=False):
   bg = Color(119, 110, 101)
   stddraw.clear(bg)
   
   # Ekranın ortasına yerleştirmek için
   cx = (grid_width + panel_width) / 2 - 1
   cy = grid_height / 2

   stddraw.setPenColor(Color(237, 194, 46) if won else Color(246, 94, 59))
   stddraw.setFontFamily('Arial')
   stddraw.setFontSize(36)
   msg = 'YOU WIN!' if won else 'GAME OVER'
   stddraw.boldText(cx, cy + 3, msg)

   stddraw.setPenColor(Color(249, 246, 242))
   stddraw.setFontSize(20)
   stddraw.boldText(cx, cy + 1, f'Score: {score}')

   # Play again butonu
   button_color = Color(143, 122, 102)
   bw, bh = grid_width + panel_width - 4, 2
   bx, by = cx - bw / 2, cy - 2
   stddraw.setPenColor(button_color)
   stddraw.filledRectangle(bx, by, bw, bh)
   stddraw.setPenColor(Color(249, 246, 242))
   stddraw.setFontSize(18)
   stddraw.boldText(cx, by + bh / 2, 'Click to Play Again')

   stddraw.show(100)
   while True:
      stddraw.show(50)
      if stddraw.mousePressed():
         mx, my = stddraw.mouseX(), stddraw.mouseY()
         if bx <= mx <= bx + bw and by <= my <= by + bh:
            return

# Tema renkleri
THEMES = {
   'Classic': {
      'empty': Color(187, 173, 160),
      'line': Color(205, 193, 180),
      'boundary': Color(120, 110, 100),
      'panel': Color(150, 138, 126),
   },
   'Dark': {
      'empty': Color(30, 30, 30),
      'line': Color(60, 60, 60),
      'boundary': Color(80, 80, 80),
      'panel': Color(45, 45, 45),
   },
   'Ocean': {
      'empty': Color(0, 80, 120),
      'line': Color(0, 100, 150),
      'boundary': Color(0, 60, 100),
      'panel': Color(0, 60, 100),
   },
   'Forest': {
      'empty': Color(34, 85, 34),
      'line': Color(50, 110, 50),
      'boundary': Color(20, 60, 20),
      'panel': Color(27, 70, 27),
   },
}

def load_theme():
   try:
      with open('theme.txt', 'r') as f:
         return f.read().strip()
   except:
      return 'Classic'

def save_theme(theme_name):
   try:
      with open('theme.txt', 'w') as f:
         f.write(theme_name)
   except:
      pass

def display_theme(grid_height, grid_width, panel_width):
   cx = (grid_width + panel_width) / 2 - 1
   current_theme = load_theme()

   while True:
      stddraw.clear(Color(100, 90, 80))
      stddraw.setPenColor(Color(249, 246, 242))
      stddraw.setFontFamily('Arial')
      stddraw.setFontSize(30)
      stddraw.boldText(cx, grid_height - 2, 'THEME SELECTION')
      stddraw.setFontSize(14)
      stddraw.text(cx, grid_height - 3.5, 'Choose a theme for the game:')

      # Tema butonları
      theme_names = list(THEMES.keys())
      for i, name in enumerate(theme_names):
         bw, bh = grid_width + panel_width - 4, 1.8
         bx = cx - bw / 2
         by = grid_height - 6 - i * 2.5
         theme = THEMES[name]
         # Seçili tema altın renkli
         if name == current_theme:
            stddraw.setPenColor(Color(237, 194, 46))
         else:
            stddraw.setPenColor(theme['panel'])
         stddraw.filledRectangle(bx, by, bw, bh)
         stddraw.setPenColor(Color(255, 255, 255))
         stddraw.setFontSize(16)
         stddraw.boldText(cx, by + bh / 2, name)

      # Geri butonu
      bbw, bbh = grid_width + panel_width - 4, 1.5
      bbx, bby = cx - bbw / 2, 1.2
      stddraw.setPenColor(Color(143, 122, 102))
      stddraw.filledRectangle(bbx, bby, bbw, bbh)
      stddraw.setPenColor(Color(255, 255, 255))
      stddraw.setFontSize(16)
      stddraw.boldText(cx, bby + bbh / 2, 'Back')

      stddraw.show(50)

      if stddraw.mousePressed():
         mx, my = stddraw.mouseX(), stddraw.mouseY()
         # Tema butonları kontrolü
         for i, name in enumerate(theme_names):
            bw, bh = grid_width + panel_width - 4, 1.8
            bx = cx - bw / 2
            by = grid_height - 6 - i * 2.5
            if bx <= mx <= bx + bw and by <= my <= by + bh:
               current_theme = name
               save_theme(name)
         # Geri butonu kontrolü
         if bbx <= mx <= bbx + bbw and bby <= my <= bby + bbh:
            return
            
def display_game_menu(grid_height, grid_width, panel_width):
   background_color = Color(187, 173, 160)
   button_color = Color(143, 122, 102)
   text_color = Color(249, 246, 242)
   title_color = Color(255, 255, 255)

   stddraw.clear(background_color)

   cx = (grid_width + panel_width) / 2 - 1

   # Başlık
   stddraw.setPenColor(title_color)
   stddraw.setFontFamily('Arial')
   stddraw.setFontSize(48)
   stddraw.boldText(cx, grid_height - 3, 'TETRIS')
   stddraw.setPenColor(title_color)
   stddraw.boldText(cx, grid_height - 5, '2048')

   # Menü resmi
   current_dir = os.path.dirname(os.path.realpath(__file__))
   img_file = os.path.join(current_dir, 'images/menu_image.png')
   if os.path.exists(img_file):
      try:
         image_to_display = Picture(img_file)
         stddraw.picture(image_to_display, cx, grid_height - 9)
      except:
         pass

   # Kontroller
   stddraw.setPenColor(title_color)
   stddraw.setFontSize(11)
   stddraw.text(cx, 6.8, '←→: Move  |  ↑: Rotate  |  ↓: Soft Drop')
   stddraw.text(cx, 6.1, 'Space: Hard Drop  |  P: Pause  |  R: Restart  |  C: Hold')

   # Start butonu
   bw, bh = grid_width + panel_width - 4, 2
   bx, by = cx - bw / 2, 3.5
   stddraw.setPenColor(button_color)
   stddraw.filledRectangle(bx, by, bw, bh)
   stddraw.setPenColor(text_color)
   stddraw.setFontSize(22)
   stddraw.boldText(cx, by + bh / 2, 'Click Here to Start')

   # Themes button
   sw, sh = grid_width + panel_width - 4, 1.5
   sx, sy = cx - sw / 2, 1.2
   stddraw.setPenColor(Color(237, 194, 46))
   stddraw.filledRectangle(sx, sy, sw, sh)
   stddraw.setPenColor(title_color)
   stddraw.setFontSize(18)
   stddraw.boldText(cx, sy + sh / 2, 'Thems')

   stddraw.show(50)
   while True:
      stddraw.show(50)
      if stddraw.mousePressed():
         mx, my = stddraw.mouseX(), stddraw.mouseY()
         if bx <= mx <= bx + bw and by <= my <= by + bh:
            return  # Oyunu başlat
         if sx <= mx <= sx + sw and sy <= my <= sy + sh:
            display_theme(grid_height, grid_width, panel_width)
            # Tema seçiminden önce menüyü göstermek için
            display_game_menu(grid_height, grid_width, panel_width)
            return


# Start the program
main()
