import lib.stddraw as stddraw  # used for drawing the tiles to display them
from lib.color import Color  # used for coloring the tiles
import random  # used for generating random tile numbers

# A class for modeling numbered tiles as in 2048
class Tile:
   # Class variables shared among all Tile objects
   boundary_thickness = 0.004
   font_family, font_size = 'Arial', 14

   # Color map: tile number -> (background_color, foreground_color)
   COLORS = {
      2:    (Color(238, 228, 218), Color(119, 110, 101)),
      4:    (Color(237, 224, 200), Color(119, 110, 101)),
      8:    (Color(242, 177, 121), Color(249, 246, 242)),
      16:   (Color(245, 149, 99),  Color(249, 246, 242)),
      32:   (Color(246, 124, 95),  Color(249, 246, 242)),
      64:   (Color(246, 94,  59),  Color(249, 246, 242)),
      128:  (Color(237, 207, 114), Color(249, 246, 242)),
      256:  (Color(237, 204, 97),  Color(249, 246, 242)),
      512:  (Color(237, 200, 80),  Color(249, 246, 242)),
      1024: (Color(237, 197, 63),  Color(249, 246, 242)),
      2048: (Color(237, 194, 46),  Color(249, 246, 242)),
   }
   DEFAULT_BG = Color(60, 58, 50)
   DEFAULT_FG = Color(249, 246, 242)

   def __init__(self, number=None):
      # randomly assign 2 or 4 if number not given (75% chance of 2)
      if number is None:
         self.number = random.choice([2, 2, 2, 4])
      else:
         self.number = number
      self._update_colors()

   def _update_colors(self):
      """Update tile colors based on the current number."""
      if self.number in Tile.COLORS:
         self.background_color, self.foreground_color = Tile.COLORS[self.number]
      else:
         self.background_color = Tile.DEFAULT_BG
         self.foreground_color = Tile.DEFAULT_FG
      self.box_color = Color(187, 173, 160)

   def merge_with(self, other):
      """Merge this tile with another tile (same number). Returns new value."""
      self.number *= 2
      self._update_colors()
      return self.number

   def draw(self, position, length=1):
      # draw the tile as a filled square
      stddraw.setPenColor(self.background_color)
      stddraw.filledSquare(position.x, position.y, length / 2)
      # draw the bounding box
      stddraw.setPenColor(self.box_color)
      stddraw.setPenRadius(Tile.boundary_thickness)
      stddraw.square(position.x, position.y, length / 2)
      stddraw.setPenRadius()
      # draw the number
      stddraw.setPenColor(self.foreground_color)
      stddraw.setFontFamily(Tile.font_family)
      if self.number >= 1000:
         stddraw.setFontSize(10)
      elif self.number >= 100:
         stddraw.setFontSize(12)
      else:
         stddraw.setFontSize(Tile.font_size)
      stddraw.boldText(position.x, position.y, str(self.number))
