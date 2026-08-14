from tile import Tile  # used for modeling each tile on the tetrominoes
from point import Point  # used for tile positions
import copy as cp  # the copy module is used for copying tiles and positions
import random  # the random module is used for generating random values
import numpy as np  # the fundamental Python module for scientific computing

# A class for modeling all 7 tetrominoes with rotation support
class Tetromino:
   # Shapes defined as (col, row) pairs for the tile matrix
   # Each shape uses a square tile matrix of size n x n
   # n=4 for I, n=2 for O, n=3 for all others
   SHAPES = {
      'I': [(1,0), (1,1), (1,2), (1,3)],
      'O': [(0,0), (0,1), (1,0), (1,1)],
      'Z': [(0,1), (1,1), (1,2), (2,2)],  # row 1 left-center, row 2 center-right
      'S': [(1,1), (2,1), (0,2), (1,2)],
      'J': [(0,0), (1,0), (1,1), (1,2)],
      'L': [(1,0), (1,1), (1,2), (2,0)],
      'T': [(0,1), (1,1), (1,2), (2,1)],
   }
   # Matrix sizes per type
   SIZES = {'I': 4, 'O': 2, 'Z': 3, 'S': 3, 'J': 3, 'L': 3, 'T': 3}

   # Class variables: game grid dimensions (set before creating tetrominoes)
   grid_height, grid_width = None, None

   def __init__(self, type):
      self.type = type
      n = Tetromino.SIZES[type]
      # create n x n tile matrix (None = empty cell)
      self.tile_matrix = np.full((n, n), None)
      # place tiles at the shape positions
      for col_index, row_index in self.SHAPES[type]:
         self.tile_matrix[row_index][col_index] = Tile()
      # starting position: bottom-left cell of the matrix
      self.bottom_left_cell = Point()
      self.bottom_left_cell.y = Tetromino.grid_height - 1
      self.bottom_left_cell.x = random.randint(0, Tetromino.grid_width - n)

   def get_cell_position(self, row, col):
      """Returns the grid position of the tile at (row, col) in the matrix."""
      n = len(self.tile_matrix)
      position = Point()
      position.x = self.bottom_left_cell.x + col
      position.y = self.bottom_left_cell.y + (n - 1) - row
      return position

   def get_min_bounded_tile_matrix(self, return_position=False):
      """Returns a copy of the tile matrix without empty rows/columns."""
      n = len(self.tile_matrix)
      min_row, max_row, min_col, max_col = n - 1, 0, n - 1, 0
      for row in range(n):
         for col in range(n):
            if self.tile_matrix[row][col] is not None:
               min_row = min(min_row, row)
               max_row = max(max_row, row)
               min_col = min(min_col, col)
               max_col = max(max_col, col)
      copy = np.full((max_row - min_row + 1, max_col - min_col + 1), None)
      for row in range(min_row, max_row + 1):
         for col in range(min_col, max_col + 1):
            if self.tile_matrix[row][col] is not None:
               copy[row - min_row][col - min_col] = cp.deepcopy(self.tile_matrix[row][col])
      if not return_position:
         return copy
      blc_position = cp.copy(self.bottom_left_cell)
      blc_position.translate(min_col, (n - 1) - max_row)
      return copy, blc_position

   def rotate(self, game_grid):
      """Rotate tetromino 90 degrees clockwise (if possible)."""
      n = len(self.tile_matrix)
      # build rotated matrix: new[col][n-1-row] = old[row][col]
      rotated = np.full((n, n), None)
      for row in range(n):
         for col in range(n):
            if self.tile_matrix[row][col] is not None:
               rotated[col][n - 1 - row] = self.tile_matrix[row][col]
      # check if rotated position is valid
      old_matrix = self.tile_matrix
      self.tile_matrix = rotated
      if not self._is_valid_position(game_grid):
         # try wall kicks: shift left/right to fit
         for dx in [1, -1, 2, -2]:
            self.bottom_left_cell.x += dx
            if self._is_valid_position(game_grid):
               return  # kick succeeded
            self.bottom_left_cell.x -= dx
         # revert rotation
         self.tile_matrix = old_matrix

   def _is_valid_position(self, game_grid):
      """Check if all tiles in the current position are inside & not colliding."""
      n = len(self.tile_matrix)
      for row in range(n):
         for col in range(n):
            if self.tile_matrix[row][col] is not None:
               pos = self.get_cell_position(row, col)
               if pos.x < 0 or pos.x >= Tetromino.grid_width:
                  return False
               if pos.y < 0:
                  return False
               if game_grid.is_occupied(pos.y, pos.x):
                  return False
      return True

   def hard_drop(self, game_grid):
      """Drop the tetromino all the way down instantly."""
      while self.move('down', game_grid):
         pass

   def draw(self):
      """Draw the tetromino on the game grid."""
      n = len(self.tile_matrix)
      for row in range(n):
         for col in range(n):
            if self.tile_matrix[row][col] is not None:
               position = self.get_cell_position(row, col)
               if position.y < Tetromino.grid_height:
                  self.tile_matrix[row][col].draw(position)

   def draw_at(self, center_x, center_y, cell_size=0.9):
      """Draw tetromino centered at (center_x, center_y) for next-piece display."""
      n = len(self.tile_matrix)
      # find bounding box of actual tiles
      min_row, max_row, min_col, max_col = n, -1, n, -1
      for row in range(n):
         for col in range(n):
            if self.tile_matrix[row][col] is not None:
               min_row = min(min_row, row)
               max_row = max(max_row, row)
               min_col = min(min_col, col)
               max_col = max(max_col, col)
      if max_row < 0:
         return
      piece_h = max_row - min_row + 1
      piece_w = max_col - min_col + 1
      # draw each tile offset from center
      for row in range(min_row, max_row + 1):
         for col in range(min_col, max_col + 1):
            if self.tile_matrix[row][col] is not None:
               dx = (col - min_col) - (piece_w - 1) / 2
               dy = (max_row - row) - (piece_h - 1) / 2
               p = Point(center_x + dx * cell_size, center_y + dy * cell_size)
               self.tile_matrix[row][col].draw(p, cell_size)

   def move(self, direction, game_grid):
      """Move this tetromino in the given direction by 1 cell."""
      if not self.can_be_moved(direction, game_grid):
         return False
      if direction == 'left':
         self.bottom_left_cell.x -= 1
      elif direction == 'right':
         self.bottom_left_cell.x += 1
      else:  # 'down'
         self.bottom_left_cell.y -= 1
      return True

   def can_be_moved(self, direction, game_grid):
      """Check if this tetromino can be moved in the given direction."""
      n = len(self.tile_matrix)
      if direction == 'left' or direction == 'right':
         for row_index in range(n):
            for col_index in range(n):
               row, col = row_index, col_index
               if direction == 'left' and self.tile_matrix[row][col] is not None:
                  leftmost = self.get_cell_position(row, col)
                  if leftmost.x == 0:
                     return False
                  if game_grid.is_occupied(leftmost.y, leftmost.x - 1):
                     return False
                  break
               row, col = row_index, n - 1 - col_index
               if direction == 'right' and self.tile_matrix[row][col] is not None:
                  rightmost = self.get_cell_position(row, col)
                  if rightmost.x == Tetromino.grid_width - 1:
                     return False
                  if game_grid.is_occupied(rightmost.y, rightmost.x + 1):
                     return False
                  break
      else:  # 'down'
         for col in range(n):
            for row in range(n - 1, -1, -1):
               if self.tile_matrix[row][col] is not None:
                  bottommost = self.get_cell_position(row, col)
                  if bottommost.y == 0:
                     return False
                  if game_grid.is_occupied(bottommost.y - 1, bottommost.x):
                     return False
                  break
      return True
