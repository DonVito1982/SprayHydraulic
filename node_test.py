import unittest
from Nodes import *


class NodeTests(unittest.TestCase):
    def test_pressure(self):
        sys_node = Node()
        sys_node.set_pressure(8, "psi")
        self.assertEqual(sys_node.get_pressure("psi"), 8)
        self.assertAlmostEqual(sys_node.get_pressure("Pascal"), 8*6894.757)
        self.assertAlmostEqual(sys_node.get_pressure('KPa'), 8*6.894757)

    def test_elevation(self):
        sys_node = Node()
        sys_node.set_elevation(8, 'm')
        self.assertEqual(sys_node.get_elevation('m'), 8)
        self.assertAlmostEqual(sys_node.get_elevation('ft'), 8*3.2808)


if __name__ == '__main__':
    unittest.main()
