##
"""
  This is a new version, written by Dom.
  Algorithm:

  Decide on x -> each px moves right / down by that amount. This is a constant
  
    1. for each row, is there any tufting? If so, add to gcode list. If not, move onto next row.
    2. for each px in row with tufting. 
        - If there is no tuft (ie, px is black), z = 0
        - If there IS tuft (ie, px is white), z = (max depth)
    3. add to gcode list
    4. only write gcode IF z delta is not zero - ie there is movement need to start/stop tufting.
"""

import datetime
from math import *
import numpy as np
import sys, os

from src.author import Gcode

from loguru import logger as log
import numpy as np
from matplotlib import pyplot as plt

from typing import Dict

platformWin = True
if (os.name != "nt"):
  platformWin = False

START = "M7"
STOP = "M9"

def tool_info():
  print("( Tool info: )")
  print("( Tool type: Tufting Gun )")

class TuftG():
  def __init__(self, im_name:str, pxs:float, feed:float, 
          bed_width:float, bed_height:float, tuft_x_offset:float, tuft_y_offset:float,
          depth:float, max_depth:float, spacing:float):
      self.im_name:str          = im_name
      self.pxs:float            = pxs
      self.feed:float           = feed
      self.bed_width:float      = bed_width
      self.bed_height:float     = bed_height
      self.uft_x_offset:float   = tuft_x_offset
      self.tuft_y_offset:float  = tuft_y_offset
      self.depth:float          = depth
      self.max_depth:float      = max_depth
      self.spacing:float        = spacing

      self.img:list[list[float]] = None
      self.options:dict = dict(
        safety_height = .012,
        tolerance = .001,
        spindle_speed = 1000,
        units = "G21",    # G20 = inches, G21 = mm
        feed_rate = feed  # 2540 # 100 inches? # was 12 (inches or mm per min)
      )

  def __str__(self):
     pass

  def convert_img(self) -> str:
    from PIL import Image

    im = Image.open(self.im_name)
    im = im.convert("L") #grayscale
    w, h = im.size
    try:
      nim = np.frombuffer(im.tobytes(), dtype=np.uint8)
    except AttributeError:
      nim = np.frombuffer(im.tobytes(), dtype=np.uint8)
    nim = nim.reshape(w,h)

    newDir = "nc_output"
    fileExtention = ".nc"
    fileName = "gcodeout"
    if not os.path.isdir(newDir):
        os.makedirs(newDir)      
    finalFileName = fileName+str(datetime.datetime.now().strftime("_%d%m%Y_%H.%M.%S.%f")[:-3])+fileExtention
    if platformWin:
        sys.stdout = open(newDir+"\\"+finalFileName, 'w')
    else:
        sys.stdout = open(newDir+"/"+finalFileName, 'w')

    if self.options.get("normalize"):
        a = nim.min()
        b = nim.max()
        if a != b:
            nim = (nim - a) / (b-a)
    else:
        nim = nim / 255.0
    
    if self.feed:
      self.options["feed_rate"] = self.feed

    nim = nim * - self.depth
    log.debug("(Image max= {0} min={1})".format(nim.max(),nim.min()))

    if self.max_depth < self.depth:
      self.max_depth = self.depth

    self.img = nim
    return finalFileName

  def write_gcode(self):
    if self.img is None: 
      raise "self.img is Null, please run convert_img()."
    
    tool_info()
    log.debug(f"options {self.options}")
    log.debug(f"img {self.img}")

    g = Gcode(safetyheight=-self.options.get("safety_height"),
              tolerance=self.options.get("tolerance"),
              spindle_speed=self.options.get("spindle_speed"),
              units=self.options.get("units"))
    g.begin()
    g.continuous(self.options.get("tolerance"))
    g.safety()

    g.set_feed(self.options.get("feed_rate"))

    log.info(f"max x: {self.pxs * len(self.img[0])}, max y: {self.pxs * len(self.img)}")
    g.flush()

    max_y = len(self.img) * self.pxs
    max_x = len(self.img[0]) * self.pxs

    for j, row in enumerate(self.img):
      log.debug(f"row {row}")
      if min(row) == 0: continue
      
      y = (len(self.img) - j) * self.pxs
      g.write("( new row )")

      is_tufting = False

      for i, p in enumerate(row):
        x = i * self.pxs

        if not is_tufting and p < 0:
          g.rapid(x=x, y=y)
          g.rapid(z=-z_stretch( x=x, mx=max_x, y=y, my=max_y, min_z=self.depth, max_z=self.max_depth ))         ## 1. plunge
          g.write(START)        ## 2. start tufting
          is_tufting = True
        elif is_tufting and p < 0:
          tuft(g, x=x, y=y, z=-z_stretch( x=x, mx=max_x, y=y, my=max_y, min_z=self.depth, max_z=self.max_depth))
        elif is_tufting and p == 0:
          tuft(g, x=x, y=y, z=-z_stretch( x=x, mx=max_x, y=y, my=max_y, min_z=self.depth, max_z=self.max_depth))
          g.write(STOP)
          g.rapid(z=0)
          is_tufting = False
        else:
          continue

  def write_gcode_bak(self):
    if self.img is None: 
      raise "self.img is Null, please run convert_img()."
    
    tool_info()
    log.debug(f"options {self.options}")
    log.debug(f"img {self.img}")

    g = Gcode(safetyheight=-self.options.get("safety_height"),
              tolerance=self.options.get("tolerance"),
              spindle_speed=self.options.get("spindle_speed"),
              units=self.options.get("units"))
    g.begin()
    g.continuous(self.options.get("tolerance"))
    g.safety()

    g.set_feed(self.options.get("feed_rate"))

    log.info(f"max x: {self.pxs * len(self.img[0])}, max y: {self.pxs * len(self.img)}")

    max_y = len(self.img) * self.pxs
    max_x = len(self.img[0]) * self.pxs

    for j, row in enumerate(self.img):
      log.debug(f"row {row}")
      if min(row) == 0: continue
      
      y = (len(self.img) - j) * self.pxs
      g.write("( new row )")

      check_row_start = True
      z = 0

      for i, p in enumerate(row):
        x = i * self.pxs

        log.debug(f"i: {i}, x: {x}, y: {y}, p: {p}, z: {z}")

        if p < z:   # tuff time!
          # if check_row_start:
          #   z = move_to_row_start(g, x, y)
          #   check_row_start = False
          # else:
          #   g.rapid(x=x, y=y)
          g.rapid(x=x, y=y)
          g.rapid(z=p)          ## 1. plunge
          g.write(START)        ## 2. start tufting
          z = p

        elif p > z: # stop tufting.
          # tuft(g, x, y)

          tuft(g, x=x, y=y/2, z=-z_stretch( x=x, mx=max_x, y=y, my=max_y, min_z=self.depth, max_z=self.max_depth ))

          tuft(g, x=x, y=y, z=z)

          g.write(STOP)       ## 1. stop tufting
          g.rapid(z=p)        ## 2. move up
          z = p

        elif i == len(row)-1:  # last px
          # tuft(g, x, y)

          tuft(g, x=x, y=y/2, z=-z_stretch( x=x, mx=max_x, y=y, my=max_y, min_z=self.depth, max_z=self.max_depth ))
          tuft(g, x=x, y=y, z=z)

          g.write(STOP)       ## stop tufting
          g.rapid(z=p)        ## 2. move up

        elif min(row[i::]) >= 0:
          break              # there is nothing left in this row 

        else:
          continue

"""
  Utilities
"""

def move_to_row_start(g: Gcode, x:float, y: float) -> float:
  g.rapid(x, y)
  g.rapid(z=0)
  g.flush()

  g.lastgcode = None

  g.lastx = x
  g.lasty = y
  g.lastz = 0

  return 0

def tuft(g: Gcode, x:float|None, y: float|None, z: float|None):
  g.cut(x=x, y=y, z=z)
  g.flush()
  g.write(f"( cut {x} {y} {z})")

"""
  Unlike milling, where the wood is always horizontal, 
  monk's cloth stretches! Meaning as you appoach the center of the fabric, 
  you should push your tufting gun lower.
   __________
  | \___4__/ |
  |1| 0    | |
  | |______|2|
  |_/_3____\_|

  This algorithm ONLY works for right to left.
  { z: current depth, m: next milestone { z, x, y } }
"""
def z_stretch(y: int, my: int, x: int, mx: int, min_z: float, max_z: float) -> float:
  stretch = 100 # Change this. This is the distance from outer rectangle to inner rectangle in mm.

  log.debug(f"x: {x} mx: {mx} y: {y} my: {my} min_z: {min_z} max_z: {max_z}")

  if my < stretch or mx < stretch:
     log.error(f"my {my} or mx {mx} is < than stretch {stretch}")
     raise Exception(f"my {my} or mx {mx} is < than stretch {stretch}")

  # section 0
  if y >= stretch and y <= my - stretch and x >= stretch and x <= mx - stretch:
    log.debug(f"z_stretch section 0 = {max_z}")
    return max_z
  # section 1
  elif in_trapezoid([(0,0), (stretch, stretch), (stretch, my - stretch), (0, my)], (x, y)):
    log.debug(f"z_stretch section 1 = {(((stretch - x) / stretch) * (max_z - min_z)) + min_z}")
    return (x / stretch) * (max_z - min_z) + min_z
  # section 2: order matters!
  elif in_trapezoid([(mx, 0), (mx, my), (mx-stretch, my-stretch), (mx-stretch, stretch)], (x, y)):
    log.debug(f"z_stretch section 2 = {(((x - (mx - stretch)) / stretch) * (max_z - min_z)) + min_z}")
    return ((mx - x) / stretch) * (max_z - min_z) + min_z
  # section 3: order matters!
  elif in_trapezoid([(0, 0), (mx, 0), (mx-stretch, stretch), (stretch, stretch)], (x, y)):
    log.debug(f"z_stretch section 3 = {(((stretch - y) / stretch) * (max_z - min_z)) + min_z}")
    return (y / stretch) * (max_z - min_z) + min_z
  # section 4
  elif in_trapezoid([(0, my), (stretch, my-stretch), (mx-stretch, my-stretch), (mx, my)], (x, y)):
    log.debug(f"z_stretch section 4 = {((y - (my - stretch) / stretch) * (max_z - min_z)) + min_z}")
    log.debug(f"y: {y}, my: {my}, stretch: {stretch}, max_z: {max_z}, min_z: {min_z}")
    return ((my - y) / stretch) * (max_z - min_z) + min_z
  # ((y - 6.5) * 22.8) + min_z
  else:
    log.error(f"coordinates:({x},{y}) did not fall into any of the sections 0 to 4. Could be an edge case?")

    show_trapizoid_and_point(point=(x,y), traps=[
      [(0,0), (0, my), (stretch, my - stretch), (stretch, stretch)],
      [(mx, 0), (mx-stretch, stretch), (mx-stretch, my-stretch), (mx, my)],
      [(0, 0), (stretch, stretch), (mx-stretch, stretch), (mx, 0)],
      [(0, my), (stretch, my-stretch), (mx-stretch, my-stretch), (mx, my)]
    ])

    raise Exception(f"coordinates:({x},{y}) did not fall into any of the sections 0 to 4. Could be an edge case?")

def in_trapezoid(trapezoid, point):
  def cross_product(p1, p2, p):
    return (p2[0] - p1[0]) * (p[1] - p1[1]) - (p2[1] - p1[1]) * (p[0] - p1[0])

  # Unpack trapezoid vertices
  if len(trapezoid) != 4: 
    print(f"trapezoid: {trapezoid}")
    raise Exception(f"trapezoid: {trapezoid}")

  (x1, y1), (x2, y2), (x3, y3), (x4, y4) = trapezoid
  x, y = point
    
  # Check if the point is on the left side of each edge
  if (cross_product((x1, y1), (x2, y2), (x, y)) >= 0 and
      cross_product((x2, y2), (x3, y3), (x, y)) >= 0 and
      cross_product((x3, y3), (x4, y4), (x, y)) >= 0 and
      cross_product((x4, y4), (x1, y1), (x, y)) >= 0):
    return True
  else:
    return False
  
def show_trapizoid_and_point(point, traps):
  # there should only be 4 trapizoids
  trapezoids = []
  for i in range(4):
    if (i < len(traps)):
      trapezoids.append(np.array(traps[i-1]))

  # Create a figure and axis
  plt.figure(figsize=(10, 8))
  plt.gca().set_aspect('equal', adjustable='box')

  # Loop through the trapezoids and plot each one
  colors = ['blue', 'green', 'purple', 'orange']
  for i, vertices in enumerate(trapezoids):
      x_trap, y_trap = vertices[:, 0], vertices[:, 1]
      plt.fill(x_trap, y_trap, edgecolor=colors[i], fill=False, label=f'Trapezoid {i+1}')

  # Plot the point
  plt.plot(point[0], point[1], 'ro', label='Point')

  # Add labels, legend, and grid
  plt.title("Multiple Trapezoids and Point Visualization")
  plt.xlabel("X-axis")
  plt.ylabel("Y-axis")
  plt.axhline(0, color='black', linewidth=0.5, linestyle='--')
  plt.axvline(0, color='black', linewidth=0.5, linestyle='--')
  plt.grid(color='gray', linestyle='--', linewidth=0.5)
  plt.legend()
  plt.show()