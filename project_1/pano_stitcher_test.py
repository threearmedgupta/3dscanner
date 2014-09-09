"""Unit tests for the pano_stitcher module.

Implement your pano_stitcher module so that all tests pass.
An example of how to run these tests is given in run_tests.sh.

The tests below will be used to test the correctness of your
implementation.

You should  add additional detailed tests as you add more
of your own functions to your implementation!
"""

import cv2
import pano_stitcher
import numpy
import unittest


class TestPanoStitcher(unittest.TestCase):
    """Tests the functionality of the pano_stitcher module."""

    def setUp(self):
        """Initializes shared state for unit tests."""
        pass

    def _known_homography(self, rows, cols):
        """Returns an arbitrary homography for testing."""
        orig_points = numpy.array([[0, 0],
                                   [0, rows - 1],
                                   [cols - 1, 0],
                                   [cols - 1, rows - 1]],
                                  numpy.float32)
        warp_points = numpy.array([[10, 10],
                                   [-10, rows - 1 - 10],
                                   [cols - 1 - 30, 50],
                                   [cols - 1 - 60, rows - 1 - 30]],
                                  numpy.float32)
        return cv2.getPerspectiveTransform(orig_points, warp_points)

    def _scale_homography(self, scale):
        """Return a homography that scales by 'scale'"""
        return numpy.array([[scale, 0.0, 0.0],
                            [0.0, scale, 0.0],
                            [0.0, 0.0, 1.0]])

    def _translate_homography(self, x, y):
        """Return a homography that translates by (x, y)"""
        return numpy.array([[1.0, 0.0, x],
                            [0.0, 1.0, y],
                            [0.0, 0.0, 1.0]])

    def test_homography(self):
        """Checks that a known homography is recovered accurately."""
        # Load the left_houses image.
        houses_left = cv2.imread("test_data/houses_left.png",
                                 cv2.CV_LOAD_IMAGE_GRAYSCALE)
        rows, cols = houses_left.shape

        # Warp with a known homography.
        H_expected = self._known_homography(rows, cols)
        houses_left_warped = cv2.warpPerspective(houses_left, H_expected,
                                                 (rows, cols))

        # Compute the homography with the library.
        H_actual = pano_stitcher.homography(houses_left_warped, houses_left)

        # The two should be nearly equal.
        H_difference = numpy.absolute(H_expected - H_actual)
        H_difference_magnitude = numpy.linalg.norm(H_difference)

        print "Expected homography:"
        print H_expected
        print "Actual homography:"
        print H_actual
        print "Difference:"
        print H_difference
        print "Magnitude of difference:", H_difference_magnitude

        max_difference_magnitude = 0.5
        self.assertLessEqual(H_difference_magnitude, max_difference_magnitude)

    def test_warp_image_scale(self):
        """Tests warping an image by a scale-only homography."""
        image = cv2.imread("test_data/houses_left.png")
        rows, cols, _ = image.shape

        # A homography that scales the image by 2x returns an image with
        # correct shape.
        scale = 2.0
        H_scale = self._scale_homography(scale)
        image_scaled, origin = pano_stitcher.warp_image(image, H_scale)
        scaled_rows, scaled_cols, _ = image_scaled.shape
        self.assertEqual(rows * scale, scaled_rows)
        self.assertEqual(cols * scale, scaled_cols)

    def test_warp_image_translate(self):
        """Tests warping an image by a translation-only homography."""
        image = cv2.imread("test_data/houses_left.png")
        rows, cols, _ = image.shape

        # A homography that only translates the image should not change shape.
        H_translate = self._translate_homography(101, 42)
        image_translated, origin = pano_stitcher.warp_image(image, H_translate)
        translated_rows, translated_cols, _ = image_translated.shape
        self.assertEqual(rows, translated_rows)
        self.assertEqual(cols, translated_cols)

    def _read_origins(self):
        """Returns book images origins from data file."""
        with open("test_data/book_origins.txt") as f:
            lines = [line.split(",") for line in f.readlines()]
            origins = [(int(line[0]), int(line[1])) for line in lines]
        return origins

    def test_create_mosaic_pano(self):
        """Tests creation of a mosaic from warped input images."""
        # Read the origins in the shared warped space.
        books_1_origin, books_2_origin, books_3_origin = self._read_origins()
        read_alpha = -1

        # Read the component images.
        books_1_warped = cv2.imread("test_data/books_1_warped.png", read_alpha)
        books_2 = cv2.imread("test_data/books_2.png")
        books_2 = cv2.cvtColor(books_2, cv2.COLOR_BGR2BGRA)
        books_3_warped = cv2.imread("test_data/books_3_warped.png", read_alpha)

        # Create the panorama mosaic.
        images = (books_1_warped, books_3_warped, books_2)
        origins = (books_1_origin, books_3_origin, books_2_origin)
        pano = pano_stitcher.create_mosaic(images, origins)

        cv2.imwrite("test_data/books_pano.png", pano)

if __name__ == '__main__':
    unittest.main()
