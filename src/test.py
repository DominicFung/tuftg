from tuftg import fabric_stretch
import matplotlib.pyplot as plt
from loguru import logger as log

def run():
  """
    make max_y arbitrarily big = 1000, y = 500, such that y will never be min distance
    max_x = 500, x => [0 ... 499]
  """

  z = []
  y = 500
  max_y = y*2
  max_x = 300
  x = range(max_x)
  
  for i in x:
    ans = fabric_stretch(max_x, max_y, i, y)
    log.debug(f"{i} {ans}")
    z.append(ans)
    
  plt.plot(x, z)
  plt.show()
  plt.close()

if __name__ == "__main__":
    run()