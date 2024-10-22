import unittest
from src.tuftg import in_trapezoid

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

if __name__ == '__main__':
  unittest.main()