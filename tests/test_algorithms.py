import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from simulator import simulate  # noqa: E402

TEXTBOOK = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]
BELADY = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]


class TestAlgorithms(unittest.TestCase):
    def test_textbook_3_frames(self):
        # Classic Silberschatz example
        self.assertEqual(simulate("fifo", TEXTBOOK, 3).faults, 15)
        self.assertEqual(simulate("lru", TEXTBOOK, 3).faults, 12)
        self.assertEqual(simulate("optimal", TEXTBOOK, 3).faults, 9)

    def test_belady_anomaly_fifo(self):
        self.assertEqual(simulate("fifo", BELADY, 3).faults, 9)
        self.assertEqual(simulate("fifo", BELADY, 4).faults, 10)

    def test_optimal_is_best(self):
        for n in range(1, 6):
            opt = simulate("optimal", TEXTBOOK, n).faults
            for a in ("fifo", "lru", "mru", "lfu", "clock"):
                self.assertLessEqual(opt, simulate(a, TEXTBOOK, n).faults)

    def test_one_frame_every_change_faults(self):
        self.assertEqual(simulate("lru", [1, 1, 2, 2, 1], 1).faults, 3)

    def test_enough_frames_only_compulsory_faults(self):
        for a in ("fifo", "lru", "optimal", "mru", "lfu", "clock"):
            self.assertEqual(simulate(a, TEXTBOOK, 8).faults, len(set(TEXTBOOK)))

    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            simulate("fifo", [], 3)
        with self.assertRaises(ValueError):
            simulate("fifo", [1], 0)
        with self.assertRaises(ValueError):
            simulate("nope", [1], 1)


if __name__ == "__main__":
    unittest.main()
