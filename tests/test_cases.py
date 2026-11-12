import io
import json
import os
import shutil
import tempfile
import unittest
import numpy as np
import pycocotools.mask as mask_util
from pycocotools.coco import COCO

def _encode(x):
    return mask_util.encode(np.asfortranarray(x, np.uint8))

class TestToBBox(unittest.TestCase):
    def testToBboxFullImage(self):
        mask = np.array([[0, 1], [1, 1]])
        bbox = mask_util.toBbox(_encode(mask))
        self.assertTrue(
            (bbox == np.array([0, 0, 2, 2], dtype="float32")).all(),
            bbox)

    # bugfix by piotr in ff4a47150bf66
    def testToBboxNonFullImage(self):
        mask = np.zeros((10, 10), dtype=np.uint8)
        mask[2:4, 3:6] = 1
        bbox = mask_util.toBbox(_encode(mask))
        self.assertTrue(
            (bbox == np.array([3, 2, 3, 2], dtype="float32")).all(),
            bbox)


class TestMaskUtil(unittest.TestCase):
    def testInvalidRLECounts(self):
        rle = {'size': [1024, 1024], 'counts': 'jd`0=`o06J5L4M3L3N2N2N2N2N1O2N2N101N1O2O0O1O2N100O1O2N100O1O1O1O1O101N1O1O1O1O1O1O101N1O100O101O0O100000000000000001O00001O1O0O2O1N3N1N3N3L5Kh0XO6J4K5L5Id[o5N]dPJ7K4K4M3N2M3N2N1O2N100O2O0O1000O01000O101N1O1O2N2N2M3M3M4J7Inml5H[RSJ6L2N2N2N2O000000000000O2O1N2N2Mkm81SRG6L3L3N2O1N2N2O0O2O00001O0000000000O2O001N2O0O2N2N3M3L5JRjf6MPVYI8J4L3N3M2N1O2O1N101N1000000O10000001O000O101N101N1O2N2N2N3L4L7FWZ_50ne`J0000001O000000001O0000001O1O0N3M3N1O2N2N2O1N2O001N2`RO^O`k0c0[TOEak0;\\\\TOJbk07\\\\TOLck03[TO0dk01ZTO2dk0OYTO4gk0KXTO7gk0IXTO8ik0HUTO:kk0ETTO=lk0CRTO>Pl0@oSOb0Rl0\\\\OmSOe0Tl0[OjSOg0Ul0YOiSOi0Wl0XOgSOi0Yl0WOeSOk0[l0VOaSOn0kh0cNmYO'}
        with self.assertRaises(ValueError):
            mask_util.decode(rle)

    def testZeroLeadingRLE(self):
        # A foreground segment of length 0 was not previously handled correctly.
        # This input rle has 3 leading zeros.
        rle = {'size': [1350, 1080], 'counts': '000lg0Zb01O00001O00001O001O00001O00001O001O00001O01O2N3M3M3M2N3M3N2M3M2N1O1O1O1O2N1O1O1O2N1O1O101N1O1O1O2N1O1O1O2N3M2N1O2N1O2O0O2N1O1O2N1O2N1O2N1O2N1O2N1O2O0O2N1O3M2N1O2N2N2N2N2N1O2N2N2N2N1O2N2N2N2N2N1N3N2N00O1O1O1O100000000000000O100000000000000001O0000001O00001O0O5L7I5K4L4L3M2N2N2N1O2m]OoXOm`0Sg0j^OVYOTa0lf0c^O]YO[a0ef0\\^OdYOba0bg0N2N2N2N2N2N2N2N2N2N2N2N2N2N2N2N2N3M2M4M2N3M2N3M2N3M2N3M2N3M2N3M2N3M2N3M2M4M2N2N3M2M4M2N2N3M2M3N3M2N3M2M3N3M2N2N3L3N2N3M2N3L3N2N3M5J4M3M4L3M3L5L3M3M4L3L4\\EXTOd6jo0K6J5K6I4M1O1O1O1N2O1O1O001N2O00001O0O101O000O2O00001N101N101N2N101N101N101N2O0O2O0O2O0O2O1N101N2N2O1N2O1N2O1N101N2O1N2O1N2O0O2O1N2N2O1N2O0O2O1N2O1N2N2N1N4M2N2M4M2N3L3N2N3L3N3L3N2N3L3N2N3L3M4L3M3M4L3M5K5K5K6J5K5K6J7I7I7Ibijn0'}
        orig_bbox = mask_util.toBbox(rle)
        mask = mask_util.decode(rle)
        rle_new = mask_util.encode(mask)
        new_bbox = mask_util.toBbox(rle_new)
        self.assertTrue(np.equal(orig_bbox, new_bbox).all())

class TestCOCO(unittest.TestCase):
    def testNonAsciiNames(self):
        # annotation files are UTF-8, whatever the platform's default encoding
        name = u"собака"
        dataset = {
            "images": [{"id": 1, "file_name": name + ".jpg", "width": 10, "height": 10}],
            "categories": [{"id": 1, "name": name}],
            "annotations": [{"id": 1, "image_id": 1, "category_id": 1, "bbox": [1, 1, 5, 5], "area": 25, "iscrowd": 0}],
        }
        results = [{"image_id": 1, "category_id": 1, "bbox": [1, 1, 5, 5], "score": 0.9, "note": name}]
        tmp_dir = tempfile.mkdtemp()
        try:
            ann_file = os.path.join(tmp_dir, "annotations.json")
            res_file = os.path.join(tmp_dir, "results.json")
            for path, obj in ((ann_file, dataset), (res_file, results)):
                with io.open(path, "w", encoding="utf-8") as f:
                    f.write(json.dumps(obj, ensure_ascii=False))

            coco = COCO(ann_file)
            self.assertEqual(coco.loadCats(1)[0]["name"], name)
            self.assertEqual(coco.loadImgs(1)[0]["file_name"], name + ".jpg")

            res = coco.loadRes(res_file)
            self.assertEqual(res.loadAnns(res.getAnnIds())[0]["note"], name)
        finally:
            shutil.rmtree(tmp_dir)

if __name__ == "__main__":
    unittest.main()
