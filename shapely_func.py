import shapely
import random
from shapely.affinity import affine_transform
from shapely.geometry import Point, Polygon, LineString
from shapely.ops import triangulate
import matplotlib.pyplot as plt

def random_points_in_polygon_triangulate(polygon, k):
    """Return list of k points chosen uniformly at random inside the polygon."""
    areas = []
    transforms = []
    for t in triangulate(polygon):
        areas.append(t.area)
        (x0, y0), (x1, y1), (x2, y2), _ = t.exterior.coords
        transforms.append([x1 - x0, x2 - x0, y2 - y0, y1 - y0, x0, y0])
    points = []
    for transform in random.choices(transforms, weights=areas, k=k):
        x, y = [random.random() for _ in range(2)]
        if x + y > 1:
            p = Point(1 - x, 1 - y)
        else:
            p = Point(x, y)
        points.append(affine_transform(p, transform))
    return points


# TRY THIS ONE FIRST AND CHECK THE AVERAGE EXECUTION TIME
def random_points_in_polygon_rejection(poly, k):
    """Return list of k points inside the polygon, implemented with uniform rejection sampling"""
    min_x, min_y, max_x, max_y = poly.bounds

    points = []
    # choose random points inside the bounding box until a point inside the polygon is found
    while len(points) < k:
        rand_x = random.uniform(min_x, max_x)
        rand_y = random.uniform(min_y, max_y)
        random_point = Point([rand_x, rand_y])
        if random_point.within(poly):
            points.append([rand_x, rand_y])
    return points


def random_point_in_polygon(poly):
    """Return a point chosen randomly inside the polygon, distribution is less random than the other implementations"""
    min_x, min_y, max_x, max_y = poly.bounds

    # first select a random x coordinate inside the area
    x = random.uniform(min_x, max_x)

    # then build a line parallel to y axis passing through that point
    x_line = LineString([(x, min_y), (x, max_y)])
    # finally choose a random point between the set of points in that line that are inside the polygon
    x_line_intercept_min, x_line_intercept_max = x_line.intersection(poly).xy[1].tolist()
    y = random.uniform(x_line_intercept_min, x_line_intercept_max)
    return x, y


def random_rectangle(x_min, y_min, x_max, y_max, base_l, height_l):
    x1 = random.uniform(x_min + base_l, x_max - base_l)
    y1 = random.uniform(y_min + height_l, y_max - height_l)
    # TODO: improve so that they are not always parallel to x and y axis
    # p1-p2 is the base
    if random.uniform(0, 1) > 0.5:
        x2 = x1 + base_l
        y2 = y1
    else:
        x2 = x1 - base_l
        y2 = y1
    if random.uniform(0, 1) > 0.5:
        # height goes up
        x3 = x1
        y3 = y1 + height_l
        x4 = x2
        y4 = y2 + height_l
    else:
        # height goes down
        x3 = x1
        y3 = y1 - height_l
        x4 = x2
        y4 = y2 - height_l

    return Polygon([(x1, y1), (x2, y2), (x4, y4), (x3, y3)])


# DRAW FUNCTIONS
def draw_multipolygon(multipolygon):
    for p in multipolygon:
        x, y = p.exterior.xy
        plt.plot(x, y)
    plt.show()

