

cdef extern from "rpackcore.h":

    ctypedef struct Rectangle:
        long width
        long height
        long x
        long y
        size_t index
        long area
        bint wide
        bint rotated

    ctypedef struct Cell

    cdef long start_pos(Cell *cell) nogil

    ctypedef struct Region:
        Cell *row_cell_start
        Cell *col_cell_start
        Cell *col_cell

    ctypedef struct BBoxRestrictions:
        long min_width
        long max_width
        long min_height
        long max_height
        long max_area

    ctypedef struct CGrid "Grid":
        size_t size
        long width
        long height

    cdef:
        CGrid *grid_alloc(size_t size, long width, long height) nogil
        void grid_free(CGrid *grid) nogil
        void grid_clear(CGrid *self) nogil
        int grid_find_region(CGrid *grid, Rectangle *rectangle, Region *reg) nogil
        void grid_split(CGrid *self, Region *reg) nogil
        long grid_search_bbox(CGrid *grid, Rectangle *sizes, BBoxRestrictions *bbr) nogil
