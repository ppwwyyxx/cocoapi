#!/usr/bin/env python
"""Tests for numpy 2.0+ compatibility."""

import unittest
import sys
import numpy as np
import pycocotools.mask as mask_util
import pycocotools._mask as _mask


class TestNumpy2Compatibility(unittest.TestCase):
    """Test that pycocotools works with numpy 2.0+"""

    def setUp(self):
        """Set up test data."""
        self.numpy_version = tuple(map(int, np.__version__.split('.')[:2]))
        print(f"Testing with NumPy {np.__version__}")

    def test_numpy_version(self):
        """Verify we're testing with appropriate numpy version."""
        # This test suite is designed for numpy 2.0+
        # but should also pass with numpy 1.x
        self.assertGreaterEqual(self.numpy_version[0], 1)

    def test_mask_encode_decode(self):
        """Test basic mask encoding and decoding."""
        # Create a test mask
        mask = np.zeros((100, 100, 1), dtype=np.uint8, order='F')
        mask[20:80, 30:70, 0] = 1

        # Encode the mask
        rle = mask_util.encode(mask)
        self.assertIsNotNone(rle)

        # Decode back
        decoded = mask_util.decode(rle)

        # Verify shapes match
        self.assertEqual(mask.shape, decoded.shape)

        # Verify content matches
        np.testing.assert_array_equal(mask, decoded)

    def test_mask_area(self):
        """Test area computation."""
        # Create a mask with known area
        mask = np.zeros((50, 50, 1), dtype=np.uint8, order='F')
        mask[10:40, 15:35, 0] = 1  # 30x20 = 600 pixels

        rle = mask_util.encode(mask)
        area = mask_util.area(rle)

        self.assertEqual(area[0], 600)

    def test_mask_bbox(self):
        """Test bounding box extraction."""
        # Create a mask with known bbox
        mask = np.zeros((100, 100, 1), dtype=np.uint8, order='F')
        mask[20:50, 30:70, 0] = 1  # bbox: [30, 20, 40, 30]

        rle = mask_util.encode(mask)
        bbox = mask_util.toBbox(rle)

        expected = np.array([[30, 20, 40, 30]], dtype=np.float32)
        np.testing.assert_array_equal(bbox, expected)

    def test_mask_iou(self):
        """Test IoU computation."""
        # Create two overlapping masks
        mask1 = np.zeros((100, 100), dtype=np.uint8, order='F')
        mask1[20:60, 30:70] = 1

        mask2 = np.zeros((100, 100), dtype=np.uint8, order='F')
        mask2[40:80, 50:90] = 1

        # Encode masks
        rle1 = mask_util.encode(mask1.reshape(100, 100, 1))
        rle2 = mask_util.encode(mask2.reshape(100, 100, 1))

        # Compute IoU
        iou = mask_util.iou(rle1, rle2, [0])

        # Verify IoU is computed without errors
        self.assertIsNotNone(iou)
        self.assertEqual(iou.shape, (1, 1))

        # IoU should be between 0 and 1
        self.assertGreaterEqual(iou[0, 0], 0)
        self.assertLessEqual(iou[0, 0], 1)

    def test_mask_merge(self):
        """Test mask merging operations."""
        # Create two masks to merge
        mask1 = np.zeros((50, 50), dtype=np.uint8, order='F')
        mask1[10:30, 10:30] = 1

        mask2 = np.zeros((50, 50), dtype=np.uint8, order='F')
        mask2[20:40, 20:40] = 1

        # Encode masks
        rle1 = mask_util.encode(mask1.reshape(50, 50, 1))[0]
        rle2 = mask_util.encode(mask2.reshape(50, 50, 1))[0]

        # Test union (intersect=0)
        merged_union = mask_util.merge([rle1, rle2], intersect=0)
        self.assertIsNotNone(merged_union)

        # Test intersection (intersect=1)
        merged_intersect = mask_util.merge([rle1, rle2], intersect=1)
        self.assertIsNotNone(merged_intersect)

        # Verify areas are correct
        area_union = mask_util.area([merged_union])
        area_intersect = mask_util.area([merged_intersect])

        # Union should be larger than intersection
        self.assertGreater(area_union[0], area_intersect[0])

    def test_bbox_iou(self):
        """Test IoU computation for bounding boxes."""
        # Create bounding boxes [x, y, w, h]
        dt = np.array([[10, 10, 20, 20], [30, 30, 15, 15]], dtype=np.float64)
        gt = np.array([[15, 15, 20, 20], [35, 35, 10, 10]], dtype=np.float64)

        # Compute IoU
        iou = mask_util.iou(dt, gt, [0, 0])

        # Verify shape
        self.assertEqual(iou.shape, (2, 2))

        # IoU values should be between 0 and 1
        self.assertTrue(np.all(iou >= 0))
        self.assertTrue(np.all(iou <= 1))

    def test_frPyObjects(self):
        """Test conversion from Python objects to RLE."""
        h, w = 100, 100

        # Test with bbox (needs to be numpy array or nested list)
        bbox = np.array([[10, 10, 20, 20]], dtype=np.float64)
        rle_bbox = mask_util.frPyObjects(bbox, h, w)
        self.assertIsNotNone(rle_bbox)

        # Test with polygon
        polygon = [10, 10, 30, 10, 30, 30, 10, 30]
        rle_poly = mask_util.frPyObjects([polygon], h, w)
        self.assertIsNotNone(rle_poly)

    def test_memory_ownership(self):
        """Test that memory ownership is correctly handled."""
        # This is the core of the numpy 2.0 compatibility fix
        # Create a mask and verify it can be properly freed
        for _ in range(10):
            mask = np.random.randint(0, 2, (50, 50, 1), dtype=np.uint8)
            mask = np.asfortranarray(mask)

            # Encode and decode multiple times
            rle = mask_util.encode(mask)
            decoded = mask_util.decode(rle)

            # Compute operations that allocate memory
            area = mask_util.area(rle)
            bbox = mask_util.toBbox(rle)

            # If memory ownership is not handled correctly,
            # this would cause memory leaks or segfaults
            del decoded, area, bbox


class TestBackwardCompatibility(unittest.TestCase):
    """Ensure the fix doesn't break numpy 1.x compatibility."""

    def test_import_works(self):
        """Test that imports work without errors."""
        # These imports should work regardless of numpy version
        import pycocotools
        import pycocotools.coco
        import pycocotools.cocoeval
        import pycocotools.mask

        # Verify module attributes exist
        self.assertTrue(hasattr(pycocotools.mask, 'encode'))
        self.assertTrue(hasattr(pycocotools.mask, 'decode'))
        self.assertTrue(hasattr(pycocotools.mask, 'area'))
        self.assertTrue(hasattr(pycocotools.mask, 'toBbox'))
        self.assertTrue(hasattr(pycocotools.mask, 'iou'))


if __name__ == '__main__':
    # Print system info
    print(f"Python {sys.version}")
    print(f"NumPy {np.__version__}")

    # Run tests
    unittest.main(verbosity=2)