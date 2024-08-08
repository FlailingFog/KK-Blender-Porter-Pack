"""Core functions"""

# Built-in
import collections
import math
from typing import Tuple

# Cython
import cython
from libc.stdlib cimport malloc, free, qsort
from libc.limits cimport LONG_MAX
from cpython.mem cimport PyMem_Malloc, PyMem_Free


DEF NO_POSITION = -1
DEF CASE_0 = 0
DEF CASE_1 = 1
DEF CASE_2 = 2
DEF CASE_3 = 3
DEF CASE_4 = 4


class PackingImpossibleError(Exception):
    """Packing rectangles is impossible with imposed restrictions.

    This can happen, for example, if `max_width` is strictly less than
    the widest rectangle given to :py:func:`rpack.pack`.

    If possible, a partial result will be given in the second
    argument, with the positions of packed rectangles up till the
    point of failure.
    """

# The following four functions are used as compare-functions for
# sorting `Rectangle` structs by index, width, height and area.

cdef int rectangle_index_cmp(const void *a, const void *b) noexcept nogil:
    cdef int index_a, index_b
    index_a = (<Rectangle*>a)[0].index
    index_b = (<Rectangle*>b)[0].index
    if index_a < index_b:
        return -1
    elif index_a == index_b:
        return 0
    else:
        return 1


cdef int rectangle_width_cmp(const void *a, const void *b) noexcept nogil:
    cdef int width_a, width_b
    width_a = (<Rectangle*>a)[0].width
    width_b = (<Rectangle*>b)[0].width
    if width_a < width_b:
        return 1
    elif width_a == width_b:
        return rectangle_area_cmp(a, b)
    else:
        return -1


cdef int rectangle_height_cmp(const void *a, const void *b) noexcept nogil:
    cdef int height_a, height_b
    height_a = (<Rectangle*>a)[0].height
    height_b = (<Rectangle*>b)[0].height
    if height_a < height_b:
        return 1
    elif height_a == height_b:
        return rectangle_area_cmp(a, b)
    else:
        return -1


cdef int rectangle_area_cmp(const void *a, const void *b) noexcept nogil:
    cdef int area_a, area_b
    area_a = (<Rectangle*>a)[0].area
    area_b = (<Rectangle*>b)[0].area
    if area_a < area_b:
        return 1
    elif area_a == area_b:
        return 0
    else:
        return -1


cdef class RectangleSet:
    """Container for a set of rectangles to be packed."""

    cdef:
        Rectangle *rectangles
        Py_ssize_t length
        long sum_width
        long sum_height

        long min_width
        long min_height

        long max_width
        long max_height

        long area


    def __cinit__(self, sizes):
        cdef:
            size_t i
            long w, h

        if len(sizes) == 0:
            raise ValueError('Empty sizes')
        self.length = len(sizes)
        self.min_height = LONG_MAX
        self.min_width = LONG_MAX

        # Prepare input
        self.rectangles = NULL
        self.rectangles = <Rectangle *> PyMem_Malloc(<size_t>self.length * sizeof(Rectangle))
        if not self.rectangles:
            raise MemoryError('Rectangles')
        i = 0
        for width, height in sizes:
            if not isinstance(width, int):
                raise TypeError("Rectangle width must be an integer")
            if not isinstance(height, int):
                raise TypeError("Rectangle height must be an integer")
            w = <long>width
            h = <long>height
            if w <= 0:
                raise ValueError("Rectangle width must be positive integer")
            elif h <= 0:
                raise ValueError("Rectangle height must be positive integer")

            self.sum_width += w
            self.sum_height += h

            if self.max_width < w:
                self.max_width = w
            if self.max_height < h:
                self.max_height = h

            if w < self.min_width:
                self.min_width = w
            if h < self.min_height:
                self.min_height = h

            self.area += w*h

            self.rectangles[i].width = w
            self.rectangles[i].height = h
            self.rectangles[i].x = NO_POSITION
            self.rectangles[i].y = NO_POSITION
            self.rectangles[i].index = i
            self.rectangles[i].area = w*h
            self.rectangles[i].wide = (w >= h)
            self.rectangles[i].rotated = False
            i += 1

    def __dealloc__(self):
        # Note: this is called if Exceptions are raised in __cinit__
        if self.rectangles != NULL:
            PyMem_Free(self.rectangles)

    def __iter__(self):
        cdef size_t i
        for i in range(self.length):
            yield self.rectangles[i]

    cdef list positions(self):
        cdef size_t i = 0, end_i = 0
        for i in range(self.length):
            if self.rectangles[i].x == NO_POSITION or \
                   self.rectangles[i].y == NO_POSITION:
                break
            end_i = i + 1
        self.sort_by_index(end_i)
        output = [(self.rectangles[i].x, self.rectangles[i].y)
                  for i in range(end_i)]
        if end_i != self.length:
            raise PackingImpossibleError(f"Partial result", output)
        return output

    cdef bbox_size(self):
        cdef:
            long max_width = 0, max_height = 0
            Rectangle *r
            size_t i
        for i in range(self.length):
            r = &self.rectangles[i]
            if r.x == NO_POSITION or r.y == NO_POSITION:
                break
            if r.width + r.x > max_width:
                max_width = r.width + r.x
            if r.height + r.y > max_height:
                max_height = r.height + r.y
        return max_width, max_height

    cdef void rotate_all(self) nogil:
        cdef size_t i
        cdef Rectangle *r
        for i in range(self.length):
            r = &self.rectangles[i]
            r.width, r.height = r.height, r.width
            r.rotated = not r.rotated
            r.wide = r.width >= r.height
        self.sum_width, self.sum_height = self.sum_height, self.sum_width
        self.min_width, self.min_height = self.min_height, self.min_width
        self.max_width, self.max_height = self.max_height, self.max_width

    cdef void sort_by_index(self, size_t length) nogil:
        qsort(<void*>(self.rectangles), length, sizeof(Rectangle), rectangle_index_cmp)

    cdef void sort_by_width(self) nogil:
        qsort(<void*>(self.rectangles), self.length, sizeof(Rectangle), rectangle_width_cmp)

    cdef void sort_by_height(self) nogil:
        qsort(<void*>(self.rectangles), self.length, sizeof(Rectangle), rectangle_height_cmp)

    cdef void sort_by_area(self) nogil:
        qsort(<void*>(self.rectangles), self.length, sizeof(Rectangle), rectangle_area_cmp)

    cdef void translate(self, long x, long y) nogil:
        cdef size_t i
        cdef Rectangle *r
        for i in range(self.length):
            r = &self.rectangles[i]
            r.x += x
            r.y += y

    cdef void transpose(self) nogil:
        cdef size_t i
        cdef Rectangle *r
        for i in range(self.length):
            r = &self.rectangles[i]
            r.x, r.y = r.y, r.x


cdef class Grid:

    cdef:
        Py_ssize_t length
        CGrid *cgrid

    def __cinit__(self, size_t size, long width=0, long height=0):
        self.cgrid = grid_alloc(size, width, height)
        if not self.cgrid:
            raise MemoryError('Grid')

    def __dealloc__(self):
        if self.cgrid != NULL:
            grid_free(self.cgrid)

    cdef (long, long) search_bbox(
            self, RectangleSet rset, BBoxRestrictions *bbr):
        cdef long status
        if self.cgrid.size + 1 < rset.length:
            raise PackingImpossibleError(
                "Too many rectangles for allocated grid size.", [])
        assert bbr.min_width == rset.max_width
        assert bbr.min_height == rset.max_height
        with nogil:
            status = grid_search_bbox(self.cgrid, rset.rectangles, bbr)
        if status >= 0:
            return self.cgrid.width, self.cgrid.height
        return self.cgrid.width, -self.cgrid.height

    cdef int pack(self, RectangleSet rset, long width, long height) except -1:
        cdef size_t i = 0
        cdef Region reg
        if self.cgrid.size + 1 < rset.length:
            raise PackingImpossibleError(
                "Too many rectangles for allocated grid size.", [])
        with nogil:
            self.cgrid.width = width
            self.cgrid.height = height
            grid_clear(self.cgrid)
            for i in range(rset.length):
                r = &rset.rectangles[i]
                grid_find_region(self.cgrid, r, &reg)
                if reg.col_cell == NULL:
                    r.x = NO_POSITION
                    r.y = NO_POSITION
                    return 1
                r.x = start_pos(reg.col_cell_start)
                r.y = start_pos(reg.row_cell_start)
                grid_split(self.cgrid, &reg)
        return 0


def pack(sizes, long max_width, long max_height):
    """Pack rectangles by testing four different strategies.

    Strategies:

        - Sort by height.

        - Sort by width.

        - Rotate and sort by height.

        - Rotate and sort by width.

    The result of the best one will be returned.

    If ``max_width`` is negative, it will be ignored.  Same for
    ``max_height``.

    If ``max_width`` or ``max_height`` is too restrictive, a
    ``PackingImpossibleError`` exception might be issued.
    """
    cdef:
        long area = LONG_MAX
        long w = 0, h = 0, best_w = 0, best_h = 0
        int case = CASE_0
        BBoxRestrictions bbr

    # Abort early
    n = len(sizes)
    if n == 0:
        return list()

    cdef RectangleSet rset = RectangleSet(sizes)

    if max_width < 0:
        max_width = rset.sum_width
    elif max_width == 0:
        raise PackingImpossibleError("max_width zero", list())
    elif max_width < rset.max_width:
        raise PackingImpossibleError("max_width less than widest rectangle", list())

    if max_height < 0:
        max_height = rset.sum_height
    elif max_height == 0:
        raise PackingImpossibleError("max_height zero", list())
    elif max_height < rset.max_height:
        raise PackingImpossibleError("max_height less than highest rectangle", list())

    grid = Grid(rset.length + 1, 0, 0)
    bbr = BBoxRestrictions(
        min_width=rset.max_width,
        max_width=max_width,
        min_height=rset.max_height,
        max_height=max_height,
        max_area=area
    )
    best_w = max_width
    best_h = max_height

    rset.sort_by_height()
    w, h = grid.search_bbox(rset, &bbr)
    area = w*h
    if 0 < area < bbr.max_area:
        bbr.max_area = area
        best_w = w
        best_h = h
        case = CASE_1

    rset.sort_by_width()
    w, h = grid.search_bbox(rset, &bbr)
    area = w*h
    if 0 < area < bbr.max_area:
        bbr.max_area = area
        best_w = w
        best_h = h
        case = CASE_2

    # Rotated

    rset.rotate_all()
    bbr.min_width = rset.max_width
    bbr.max_width = max_height
    bbr.min_height = rset.max_height
    bbr.max_height = max_width

    w, h = grid.search_bbox(rset, &bbr)
    area = w*h
    if 0 < area < bbr.max_area:
        bbr.max_area = area
        best_w = w
        best_h = h
        case = CASE_3

    rset.sort_by_width()
    w, h = grid.search_bbox(rset, &bbr)
    area = w*h
    if 0 < area < bbr.max_area:
        bbr.max_area = area
        best_w = w
        best_h = h
        case = CASE_4

    # Restore rset to best case
    if case == CASE_0:
        best_w = bbr.max_width
        best_h = bbr.max_height
    elif case == CASE_1:
        rset.rotate_all()
    elif case == CASE_2:
        rset.rotate_all()
        rset.sort_by_width()
    elif case == CASE_3:
        rset.sort_by_height()
    elif case == CASE_4:
        pass

    grid.pack(rset, best_w, best_h)

    # Restore rectangles if rotated
    if case == CASE_0 or case == CASE_3 or case == CASE_4:
        rset.transpose()

    return rset.positions()


def bbox_size(sizes, positions) -> Tuple[int, int]:
    """Return bounding box size (width, height) of packed rectangles.

    Useful for evaluating the result of :py:func:`rpack.pack`.

    Example::

        >>> import rpack

        >>> sizes = [(58, 206), (231, 176), (35, 113), (46, 109)]
        >>> positions = rpack.pack(sizes)

        >>> bbox_size(sizes, positions)
        (335, 222)

    :param sizes: List of rectangle sizes (width, height).
    :type sizes: List[Tuple[int, int]]

    :param positions: List of rectangle positions (x, y).
    :type positions: List[Tuple[int, int]]

    :return: Size (width, height) of bounding box covering rectangles
             having `sizes` and `positions`.
    :rtype: Tuple[int, int]
    """
    cdef long max_width = 0, max_height = 0, w, h, x, y
    for i in range(len(sizes)):
        w, h = sizes[i]
        x, y = positions[i]
        if w + x > max_width:
            max_width = w + x
        if h + y > max_height:
            max_height = h + y
    return max_width, max_height


def packing_density(sizes, positions) -> float:
    """Return packing density of packed rectangles.

    Useful for evaluating the result of :py:func:`rpack.pack`.

    Example::

        >>> import rpack

        >>> sizes = [(58, 206), (231, 176), (35, 113), (46, 109)]
        >>> positions = rpack.pack(sizes)

        >>> packing_density(sizes, positions)
        0.8279279279279279

    :param sizes: List of rectangle sizes (width, height).
    :type sizes: List[Tuple[int, int]]

    :param positions: List of rectangle positions (x, y).
    :type positions: List[Tuple[int, int]]

    :return: Packing density as a fraction in the interval [0, 1],
             where 1 means that the bounding box area equals the sum
             of the areas of the rectangles packed, i.e. perfect
             packing.
    :rtype: float
    """
    w, h = bbox_size(sizes, positions)
    area_bounding_box = w*h
    area_rectangles = sum(w*h for w, h in sizes)
    return area_rectangles/area_bounding_box


def overlapping(sizes, positions):
    """Return indices of overlapping rectangles, else ``None``.

    Mainly used for test cases.

    Example::

        >>> sizes = [(10, 10), (10, 10)]

        >>> positions = [(0, 0), (10, 10)]
        >>> overlapping(sizes, positions) is None
        True

        >>> positions = [(0, 0), (5, 5)]
        >>> overlapping(sizes, positions)
        (0, 1)

    :param sizes: List of rectangle sizes (width, height).
    :type sizes: List[Tuple[int, int]]

    :param positions: List of rectangle positions (x, y).
    :type positions: List[Tuple[int, int]]

    :return: Return indices (i, j) if i-th and j-th rectangle overlap
             (first case found).  Return ``None`` if no rectangles
             overlap.
    :rtype: Union[None, Tuple[int, int]]
    """
    cdef:
        long w1, h1, x1, y1
        long w2, h2, x2, y2
        bint disjoint_in_x, disjoint_in_y
        Py_ssize_t n = len(sizes)
    for i in range(n):
        w1, h1 = sizes[i]
        x1, y1 = positions[i]
        for j in range(n):
            if j == i:
                continue
            w2, h2 = sizes[j]
            x2, y2 = positions[j]
            disjoint_in_x = (x1 + w1 <= x2 or x2 + w2 <= x1)
            disjoint_in_y = (y1 + h1 <= y2 or y2 + h2 <= y1)
            if not (disjoint_in_x or disjoint_in_y):
                return (i, j)
    return None
