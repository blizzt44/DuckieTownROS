import numpy as np
from scipy.spatial import ConvexHull

from typing import List, Tuple, Union


class BlobBounding:
    def __init__(self, bounding_degree=4) -> None:
        """
        Args:
            bounding_degree: The number of vertices that a bounding polygon should have.
        """
        raise NotImplementedError("Disabled on Duckiebot")

    @staticmethod
    def get_edge_map(binary_image: np.ndarray, dilation_size:int=3):
        """Get the edge map of a binary image.
        Args:
            binary_image: An image with 0s and 1s. Edge detection is applied on pixels of 1s.
            dilation_size: Dilate the image before finding the edge.
        Returns:
            edge_map: An image of the same size as the input, but all 1s are at the edges.
        """
        raise NotImplementedError("Disabled on Duckiebot")
    @staticmethod
    def get_bounding_rectangle(hull_points: np.ndarray):
        """Find the smallest bounding rectangle for a convex hull.
        
        Ref:
            https://stackoverflow.com/questions/13542855/algorithm-to-find-the-minimum-area-rectangle-for-given-points-in-order-to-comput
        Args:
            hull_points: an n*2 matrix of coordinates.
        Returns:
            rval: An n*2 matrix of coordinates of rectangle vertices.
        """
        raise NotImplementedError("Disabled on Duckiebot")
    def get_bounding_polygon(self, hull_points: np.ndarray):
        raise NotImplementedError("Disabled on Duckiebot")

    def get_bounding_polygons(self, grayscale_image: np.ndarray) -> List[np.ndarray]:
        raise NotImplementedError("Disabled on Duckiebot")