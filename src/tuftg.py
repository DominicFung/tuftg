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

platformWin = True
if (os.name != "nt"):
  platformWin = False

START = "M7"
STOP = "M9"

def tool_info():
  print("( Tool info: )")
  print("( Tool type: Tufting Gun )")

def convert(options:dict, img:list[list[float]], max_depth=4.5, px_len=5): # was 0.22 inches
  log.info("convert in progress ..")
  tool_info()
  log.debug(f"options {options}")
  log.debug(f"img {img}")

  g = Gcode(safetyheight=-options.get("safety_height"),
            tolerance=options.get("tolerance"),
            spindle_speed=options.get("spindle_speed"),
            units=options.get("units"))
  g.begin()
  g.continuous(options.get("tolerance"))
  g.safety()

  g.set_feed(options.get("feed_rate"))

  log.info(f"max x: {px_len * len(img[0])}, max y: {px_len * len(img)}")

  max_y = len(img)
  max_x = len(img[0])

  for j, row in enumerate(img):
    log.debug(f"row {row}")
    if min(row) == 0: continue
    
    y = (len(img) - j) * px_len
    g.write("( new row )")

    check_row_start = True
    z = 0

    for i, p in enumerate(row):
      x = i * px_len

      log.debug(f"i: {i}, x: {x}, y: {y}, p: {p}, z: {z}")

      if p < z:   # tuff time!
        if check_row_start:
          z = move_to_row_start(g, x, y)
          check_row_start = False
        else:
          g.rapid(x=x, y=y)
        g.rapid(z=p)        ## 1. plunge
        g.write(START)      ## 2. start tufting
        z = p

      elif p > z: # stop tufting.
        # tuft(g, x, y)

        tuft(g, x=x, y=y/2, z=z_stretch( x, max_y, z, max_depth ))
        tuft(g, x=x, y=y, z=z)

        g.write(STOP)       ## 1. stop tufting
        g.rapid(z=p)        ## 2. move up
        z = p

      elif i == len(row)-1:  # last px
        # tuft(g, x, y)

        tuft(g, x, y/2, z_stretch( x, max_y, z, max_depth ))
        tuft(g, x, y, z)

        g.write(STOP)       ## stop tufting
        g.rapid(z=p)        ## 2. move up

      elif min(row[i::]) >= 0:
         break              # there is nothing left in this row 

      else:
        continue


"""
  Unlike milling, where the wood is always horizontal, 
  monk's cloth stretches! Meaning as you appoach the center of the fabric, 
  you should push your tufting gun lower.
   __________
  | \___4__/ |
  |1| 0    | |
  | |______|2|
  |_/_3____\_|

"""
def z_stretch(y: int, my: int, x: int, mx: int, min_z: float, max_z: float) -> float:
  stretch = 100 # Change this. This is the distance from outer rectangle to inner rectangle in mm.
  if my < stretch or mx < stretch:
     log.error(f"my {my} or mx {mx} is < than stretch {stretch}")
     raise Exception(f"my {my} or mx {mx} is < than stretch {stretch}")

  # section 0
  if y >= stretch and y <= my - stretch and x >= stretch and x <= mx - stretch:
     return max_z
  # section 1
  elif in_trapezoid([(0,0), (stretch, stretch), (stretch, my - stretch), (0, my)], (x, y)):
      return (((stretch - x) / stretch) * (max_z - min_z)) + min_z
  # section 2
  elif in_trapezoid([(mx, 0), (mx-stretch, stretch), (mx-stretch, my-stretch), (mx, my)], (x, y)):
     return (((x - (mx - stretch)) / stretch) * (max_z - min_z)) + min_z
  # section 3
  elif in_trapezoid([(0, 0), (stretch, stretch), (mx-stretch, stretch), (mx, 0)], (x, y)):
     return (((stretch - y) / stretch) * (max_z - min_z)) + min_z
  # section 4
  elif in_trapezoid([(0, my), (stretch, my-stretch), (mx-stretch, my-stretch), (mx, my)], (x, y)):
     return ((y - (my - stretch) / stretch) * (max_z - min_z)) + min_z
  else:
     raise Exception(f"coordinates:({x},{y}) did not fall into any of the sections 0 to 4. Could be an edge case?")

def in_trapezoid(trapezoid, point):
  def cross_product(p1, p2, p):
    return (p2[0] - p1[0]) * (p[1] - p1[1]) - (p2[1] - p1[1]) * (p[0] - p1[0])

    # Unpack trapezoid vertices
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

options = dict(
  safety_height = .012,
  tolerance = .001,
  spindle_speed = 1000,
  units = "G21", # G20 = inches, G21 = mm
  feed_rate = 2540 # 100 inches? # was 12 (inches or mm per min)
)

def tuftg(im_name, depth, max_depth, spacing, feed=100):
  from PIL import Image

  im = Image.open(im_name)
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

  if options.get("normalize"):
      a = nim.min()
      b = nim.max()
      if a != b:
          nim = (nim - a) / (b-a)
  else:
      nim = nim / 255.0
  
  if feed:
     options["feed_rate"] = feed

  nim = nim * -depth
  log.debug("(Image max= {0} min={1})".format(nim.max(),nim.min()))

  if max_depth < depth:
     max_depth = depth

  convert(options, nim, max_depth=max_depth)

  return finalFileName