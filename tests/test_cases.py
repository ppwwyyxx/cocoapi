import unittest
import numpy as np
import pycocotools.mask as mask_util

def _encode(x):
    return mask_util.encode(np.asfortranarray(x, np.uint8))

class TestToBBox(unittest.TestCase):
    def testToBboxFullImage(self):
        mask = np.array([[0, 1], [1, 1]])
        bbox = mask_util.toBbox(_encode(mask))
        self.assertTrue(
            (bbox == np.array([0, 0, 2, 2], dtype="float32")).all(),
            bbox)

    def testToBboxNonFullImage(self):
        mask = np.zeros((10, 10), dtype=np.uint8)
        mask[2:4, 3:6] = 1
        bbox = mask_util.toBbox(_encode(mask))
        self.assertTrue(
            (bbox == np.array([3, 2, 3, 2], dtype="float32")).all(),
            bbox)

if __name__ == "__main__":
    unittest.main()
