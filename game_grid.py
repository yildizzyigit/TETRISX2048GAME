import lib.stddraw as stddraw  # used for displaying the game grid
from lib.color import Color  # used for coloring the game grid
from point import Point  # used for tile positions
import numpy as np  # fundamental Python module for scientific computing
import pygame
import copy as cp
# A class for modeling the game grid with all Tetris 2048 mechanics
class GameGrid:
   def __init__(self, grid_h, grid_w):
      self.grid_height = grid_h
      self.grid_width = grid_w
      # tile matrix: stores Tile objects (None = empty)
      self.tile_matrix = np.full((grid_h, grid_w), None)
      self.current_tetromino = None
      self.game_over = False
      self.high_score = 0
      self.level = 1
      self.lines_cleared = 0
      self.held_tetromino = None
      self.can_hold = True  # her tetromino için sadece bir kez hold yapılabilecek
      pygame.mixer.init()
      self.merge_sound = pygame.mixer.Sound('sounds/merge.wav')
      self.clear_sound = pygame.mixer.Sound('sounds/clear.wav')
      self.game_over_sound = pygame.mixer.Sound('sounds/lose.mp3')
      self.win_sound = pygame.mixer.Sound('sounds/win.wav')
      self.score = 0
      self.win = False  # True when a 2048 tile is reached

      # Panel dimensions (right side info panel)
      self.panel_width = 5  # extra columns for score/next panel

      # Colors
      self.empty_cell_color = Color(187, 173, 160)
      self.line_color = Color(205, 193, 180)
      self.boundary_color = Color(120, 110, 100)
      self.panel_color = Color(150, 138, 126)
      self.line_thickness = 0.002
      self.box_thickness = 5 * self.line_thickness

   def display(self, next_tetromino=None):
      """Display the game grid, current tetromino, score, and next piece."""
      stddraw.clear(self.panel_color)
      self.draw_grid()
      if self.current_tetromino is not None:
          self.draw_ghost(self.current_tetromino)
          self.current_tetromino.draw()
      self.draw_boundaries()
      self.draw_panel(next_tetromino)
      stddraw.show(250)  # 250ms per frame for smooth gameplay

   def draw_grid(self):
      """Draw all locked tiles and grid lines."""
      # draw empty cells as background
      stddraw.setPenColor(self.empty_cell_color)
      for row in range(self.grid_height):
         for col in range(self.grid_width):
            stddraw.filledSquare(col, row, 0.5)
      # draw locked tiles
      for row in range(self.grid_height):
         for col in range(self.grid_width):
            if self.tile_matrix[row][col] is not None:
               self.tile_matrix[row][col].draw(Point(col, row))
      # draw grid lines
      stddraw.setPenColor(self.line_color)
      stddraw.setPenRadius(self.line_thickness)
      start_x, end_x = -0.5, self.grid_width - 0.5
      start_y, end_y = -0.5, self.grid_height - 0.5
      for x in np.arange(start_x + 1, end_x, 1):
         stddraw.line(x, start_y, x, end_y)
      for y in np.arange(start_y + 1, end_y, 1):
         stddraw.line(start_x, y, end_x, y)
      stddraw.setPenRadius()

   def draw_boundaries(self):
      """Draw the border around the game grid."""
      stddraw.setPenColor(self.boundary_color)
      stddraw.setPenRadius(self.box_thickness)
      stddraw.rectangle(-0.5, -0.5, self.grid_width, self.grid_height)
      stddraw.setPenRadius()
   
   def draw_ghost(self, tetromino):
      """Tetrominonun düşeceği yeri gösteren ghost piece."""
   
      ghost = cp.deepcopy(tetromino)
      # Ghost'u en aşağıya indir
      while ghost.can_be_moved('down', self):
         ghost.bottom_left_cell.y -= 1
      # Ghost tile'larını şeffaf renkte çiz
      n = len(ghost.tile_matrix)
      for row in range(n):
         for col in range(n):
            if ghost.tile_matrix[row][col] is not None:
               pos = ghost.get_cell_position(row, col)
               if 0 <= pos.y < self.grid_height:
                  stddraw.setPenColor(Color(200, 200, 200))
                  stddraw.filledSquare(pos.x, pos.y, 0.5)
                  stddraw.setPenColor(Color(150, 150, 150))
                  stddraw.setPenRadius(0.004)
                  stddraw.square(pos.x, pos.y, 0.5)
                  stddraw.setPenRadius()


   def draw_panel(self, next_tetromino=None):
      """Draw the score and next piece panel on the right side."""
      panel_x = self.grid_width
      panel_center_x = panel_x + self.panel_width / 2 - 0.5

      # panel background
      stddraw.setPenColor(self.panel_color)
      stddraw.filledRectangle(panel_x - 0.5, -0.5, self.panel_width, self.grid_height)

      # SCORE
      stddraw.setPenColor(Color(255, 255, 255))
      stddraw.setFontFamily('Arial')
      stddraw.setFontSize(13)
      stddraw.boldText(panel_center_x, self.grid_height - 1.2, 'SCORE')
      stddraw.setFontSize(18)
      stddraw.boldText(panel_center_x, self.grid_height - 2.2, str(self.score))

      # BEST
      stddraw.setPenColor(Color(255, 255, 255))
      stddraw.setFontSize(13)
      stddraw.boldText(panel_center_x, self.grid_height - 3.2, 'BEST')
      stddraw.setFontSize(18)
      stddraw.boldText(panel_center_x, self.grid_height - 4.2, str(self.high_score))

      # NEXT
      stddraw.setPenColor(Color(255, 255, 255))
      stddraw.setFontSize(13)
      stddraw.boldText(panel_center_x, self.grid_height - 5.2, 'NEXT')
      if next_tetromino is not None:
         next_tetromino.draw_at(panel_center_x, self.grid_height - 7.5, cell_size=0.8)

      # LEVEL
      stddraw.setPenColor(Color(255, 255, 255))
      stddraw.setFontSize(13)
      stddraw.boldText(panel_center_x, self.grid_height - 10, 'LEVEL')
      stddraw.setFontSize(18)
      stddraw.boldText(panel_center_x, self.grid_height - 11, str(self.level))

      # HOLD
      stddraw.setPenColor(Color(255, 255, 255))
      stddraw.setFontSize(13)
      stddraw.boldText(panel_center_x, self.grid_height - 12.2, 'HOLD')
      if self.held_tetromino is not None:
         self.held_tetromino.draw_at(panel_center_x, self.grid_height - 14.5, cell_size=0.8)

      # Controls hint
      stddraw.setPenColor(Color(255, 255, 255))
      stddraw.setFontSize(8)
      hints = [
         ('←→', 'Move'),
         ('↑', 'Rotate'),
         ('↓', 'Soft Drop'),
         ('Space', 'Hard Drop'),
         ('P', 'Pause'),
         ('R', 'Restart'),
         ('C', 'Hold'),
      ]
      for i, (key, action) in enumerate(hints):
         y = 3.5 - i * 0.7
         stddraw.boldText(panel_center_x, y, f'{key}: {action}')

   def is_occupied(self, row, col):
      """Check if a grid cell is occupied."""
      if not self.is_inside(row, col):
         return False
      return self.tile_matrix[row][col] is not None

   def is_inside(self, row, col):
      """Check if a row/col is inside the grid."""
      return 0 <= row < self.grid_height and 0 <= col < self.grid_width

   def update_grid(self, tiles_to_lock, blc_position):
      """
      Lock the landed tetromino onto the grid, then:
      1. Merge tiles column-wise (bottom to top, chain merging)
      2. Handle free (unconnected) tiles
      3. Clear full rows
      Returns True if game is over.
      """
      self.current_tetromino = None
      # --- Lock tiles ---
      n_rows, n_cols = len(tiles_to_lock), len(tiles_to_lock[0])
      for col in range(n_cols):
         for row in range(n_rows):
            if tiles_to_lock[row][col] is not None:
               pos = Point()
               pos.x = blc_position.x + col
               pos.y = blc_position.y + (n_rows - 1) - row
               if self.is_inside(pos.y, pos.x):
                  self.tile_matrix[pos.y][pos.x] = tiles_to_lock[row][col]
               else:
                  self.game_over = True  # tile above grid → game over
                  self.game_over_sound.play()
      if self.game_over:
         return True

      # --- 1. Chain merge column-wise bottom-to-top ---
      self._merge_tiles()

      # --- 2. Handle free tiles ---
      self._handle_free_tiles()

      # --- 3. Clear full lines ---
      self._clear_full_lines()

      # --- Check win condition (2048 tile) ---
      for row in range(self.grid_height):
         for col in range(self.grid_width):
            if self.tile_matrix[row][col] is not None:
               if self.tile_matrix[row][col].number >= 16:
               #if self.tile_matrix[row][col].number >= 16:  win ekranınını testi için
                  self.win = True
                  self.win_sound.play()
      return self.game_over

   def _merge_tiles(self):
      """
      Merge vertically adjacent tiles with the same number in each column.
      Processes bottom to top, chains until no more merges in a pass.
      """
      merged = True
      while merged:
         merged = False
         for col in range(self.grid_width):
            for row in range(1, self.grid_height):  # bottom to top (row 0 is bottom)
               if (self.tile_matrix[row][col] is not None and
                     self.tile_matrix[row - 1][col] is not None):
                  if self.tile_matrix[row][col].number == self.tile_matrix[row - 1][col].number:
                     # merge: lower tile gets doubled, upper tile is removed
                     new_val = self.tile_matrix[row - 1][col].merge_with(self.tile_matrix[row][col])
                     self.score += new_val
                     self.tile_matrix[row][col] = None
                     self.merge_sound.play()
                     # tiles above the removed tile fall down
                     for r in range(row, self.grid_height - 1):
                        self.tile_matrix[r][col] = self.tile_matrix[r + 1][col]
                     self.tile_matrix[self.grid_height - 1][col] = None
                     merged = True
                     break  # restart scan for this column from bottom

   def _handle_free_tiles(self):
      """
      Remove tiles not connected (4-connectivity) to the bottom row or to a
      tile connected to the bottom. Add their numbers to score (easier approach).
      """
      connected = self._find_connected_tiles()
      for row in range(self.grid_height):
         for col in range(self.grid_width):
            if self.tile_matrix[row][col] is not None and not connected[row][col]:
               self.score += self.tile_matrix[row][col].number
               self.tile_matrix[row][col] = None

   def _find_connected_tiles(self):
      """BFS/flood fill from the bottom row to find all 4-connected tiles."""
      connected = [[False] * self.grid_width for _ in range(self.grid_height)]
      # seed: tiles in row 0 (bottom)
      queue = []
      for col in range(self.grid_width):
         if self.tile_matrix[0][col] is not None:
            connected[0][col] = True
            queue.append((0, col))
      # BFS
      while queue:
         r, c = queue.pop(0)
         for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nr, nc = r + dr, c + dc
            if self.is_inside(nr, nc) and not connected[nr][nc]:
               if self.tile_matrix[nr][nc] is not None:
                  connected[nr][nc] = True
                  queue.append((nr, nc))
      return connected

   def _clear_full_lines(self):
      """Clear fully-occupied rows and add sum of tiles to score."""
      rows_to_clear = []
      for row in range(self.grid_height):
         if all(self.tile_matrix[row][col] is not None for col in range(self.grid_width)):
            rows_to_clear.append(row)

      rainbow_colors = [
         Color(255, 0, 0),
         Color(255, 127, 0),
         Color(255, 255, 0),
         Color(0, 255, 0),
         Color(0, 0, 255),
         Color(148, 0, 211),
      ]

      for row in rows_to_clear:
         # Gökkuşağı animasyonu
         for color in rainbow_colors:
            for col in range(self.grid_width):
               stddraw.setPenColor(color)
               stddraw.filledSquare(col, row, 0.5)
            stddraw.show(50)
         # Ses çal
         self.clear_sound.play()
         # Skoru güncelle
         for col in range(self.grid_width):
            self.score += self.tile_matrix[row][col].number
         # Satırı sil
         for r in range(row, self.grid_height - 1):
            for col in range(self.grid_width):
               self.tile_matrix[r][col] = self.tile_matrix[r + 1][col]
         for col in range(self.grid_width):
            self.tile_matrix[self.grid_height - 1][col] = None
         rows_to_clear = [r - 1 if r > row else r for r in rows_to_clear]
         self.lines_cleared += 1
         self.level = 1 + self.lines_cleared // 5 # her 5 satır temizlendikten sonra level atla
