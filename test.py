import unittest
from src.tuftg import in_trapezoid, show_trapizoid_and_point

import numpy as np
from matplotlib import pyplot as plt

class Testing(unittest.TestCase):
  def test_in_trapezoid(self):
    trapezoid_vertices = [(1, 1), (4, 1), (3, 3), (2, 3)]
    point = (2.5, 2)
    is_inside = in_trapezoid(trapezoid_vertices, point)

    print("Point is inside the trapezoid" if is_inside else "Point is outside the trapezoid")

    self.assertEqual(is_inside, True)

  def test_in_trapezoid_negative(self):
    trapezoid_vertices = [(-4, -3), (-1, -3), (1, -1), (-6, -1)]
    point = (-2, -2)  # A point within the trapezoid

    is_inside = in_trapezoid(trapezoid_vertices, point)
    print("Point is inside the trapezoid" if is_inside else "Point is outside the trapezoid")

    self.assertEqual(is_inside, True)

  def test_in_trapizoid_same_vertex(self):
    trapezoid_vertices = [(1, 1), (4, 1), (3, 3), (2, 3)]
    point = (1, 1)
    is_inside = in_trapezoid(trapezoid_vertices, point)

    print("Point is inside the trapezoid" if is_inside else "Point is outside the trapezoid")

    self.assertEqual(is_inside, True)

  def test_in_trapizoid_mixed_vertices(self):
    trapezoid_vertices = [(-3, -2), (2, -2), (3, 2), (-4, 2)]
    point = (-1, 0)  # A point inside the trapezoid

    is_inside = in_trapezoid(trapezoid_vertices, point)
    print("Point is inside the trapezoid" if is_inside else "Point is outside the trapezoid")

    self.assertEqual(is_inside, True)

  def test__trapixzoid_edgecase_1(self):
    stretch = 100
    mx = 750
    trapezoid_vertices = [(0, 0), (mx, 0), (mx-stretch, stretch), (stretch, stretch)]
    point = (315, 95)

    is_inside = in_trapezoid(trapezoid_vertices, point)
    print("Point is inside the trapezoid" if is_inside else "Point is outside the trapezoid")

    self.assertEqual(is_inside, True)

  def test__trapixzoid_edgecase_1dot1(self):
    stretch = 100
    mx = 750
    trapezoid_vertices = [(0, 0), (mx, 0), (mx-stretch, stretch), (stretch, stretch)]
    point = (315, 95)

    # show_trapizoid_and_point(point=point, traps=[trapezoid_vertices])

    def cross_product(p1, p2, p):
      return (p2[0] - p1[0]) * (p[1] - p1[1]) - (p2[1] - p1[1]) * (p[0] - p1[0])
    
    (x1, y1), (x2, y2), (x3, y3), (x4, y4) = trapezoid_vertices
    x, y = point

    print(cross_product((x1, y1), (x2, y2), (x, y)))
    print(cross_product((x2, y2), (x3, y3), (x, y)))
    print(cross_product((x3, y3), (x4, y4), (x, y)))
    print(cross_product((x4, y4), (x1, y1), (x, y)))

    if (cross_product((x1, y1), (x2, y2), (x, y)) >= 0 and
        cross_product((x2, y2), (x3, y3), (x, y)) >= 0 and
        cross_product((x3, y3), (x4, y4), (x, y)) >= 0 and
        cross_product((x4, y4), (x1, y1), (x, y)) >= 0):
      is_inside = True
    else:
      is_inside = False

    print("Point is inside the trapezoid" if is_inside else "Point is outside the trapezoid")
    self.assertEqual(is_inside, True)

if __name__ == '__main__':
  unittest.main()