"""Pack a set of rectangles into a bounding box with minimum area

===========================
Welcome to rectangle-packer
===========================

|PyPI-Versions| |PyPI-Wheel| |Build-Status| |Read-the-Docs| |GitHub-License|

|PyPI-Downloads|

**Primary use:** Given a set of rectangles with fixed orientations,
find a bounding box of minimum area that contains them all with no
overlap.

This project is inspired by Matt Perdeck's blog post `Fast Optimizing
Rectangle Packing Algorithm for Building CSS Sprites`_.

* The latest documentation is available on `Read the Docs`_.
* The source code is available on `GitHub`_.


Installation
============

Install latest version from `PyPI`_:

.. code:: sh

    $ python3 -m pip install rectangle-packer

Or `clone the repository`_ and install with:

.. code:: sh

    $ python3 setup.py install


Basic usage
===========

.. code:: python

    # Import the module
    >>> import rpack

    # Create a bunch of rectangles (width, height)
    >>> sizes = [(58, 206), (231, 176), (35, 113), (46, 109)]

    # Pack
    >>> positions = rpack.pack(sizes)

    # The result will be a list of (x, y) positions:
    >>> positions
    [(0, 0), (58, 0), (289, 0), (289, 113)]

The output positions are the lower left corner coordinates of each
rectangle in the input.

These positions will yield a packing with no overlaps and enclosing
area as small as possible (best effort).

.. note::

    * You must use **positive integers** as rectangle width and height.

    * The module name is **rpack** which is an abbreviation of the package
      name at PyPI (rectangle-packer).

    * The computational time required by ``rpack.pack()`` increases by
      the number *and* size of input rectangles.  If this becomes a problem,
      you might need to implement your own `divide-and-conquer algorithm`_.


Examples
========

**Example A:**

.. image:: https://penlect.com/rpack/2.0.1/img/packing_best_10.png
   :alt: pack10
   :align: center

**Example B:**

.. image:: https://penlect.com/rpack/2.0.1/img/packing_phi.png
   :alt: packphi
   :align: center

**Example C:** Sometimes the input rectangles simply cannot be packed in
a good way. Here is an example of low packing density:

.. image:: https://penlect.com/rpack/2.0.1/img/packing_worst_10.png
   :alt: pack10bad
   :align: center

**Example D:** The image below is contributed by Paul Brodersen, and
illustrates a solution to a problem discussed at stackoverflow_.

.. image:: https://i.stack.imgur.com/kLat8.png
    :alt: PaulBrodersenExampleImage
    :align: center
    :width: 450px


.. _Read the Docs: https://rectangle-packer.readthedocs.io/en/latest/
.. _GitHub: https://github.com/Penlect/rectangle-packer
.. _`Fast Optimizing Rectangle Packing Algorithm for Building CSS Sprites`: http://www.codeproject.com/Articles/210979/Fast-optimizing-rectangle-packing-algorithm-for-bu
.. _`clone the repository`: https://github.com/Penlect/rectangle-packer
.. _stackoverflow: https://stackoverflow.com/a/53156709/2912349
.. _PyPI: https://pypi.org/project/rectangle-packer/
..  _`divide-and-conquer algorithm`: https://en.wikipedia.org/wiki/Divide-and-conquer_algorithm

.. |PyPI-Versions| image:: https://img.shields.io/pypi/pyversions/rectangle-packer.svg
   :target: https://pypi.org/project/rectangle-packer

.. |PyPI-Wheel| image:: https://img.shields.io/pypi/wheel/rectangle-packer.svg
   :target: https://pypi.org/project/rectangle-packer

.. |Build-Status| image:: https://travis-ci.com/Penlect/rectangle-packer.svg?branch=master
   :target: https://travis-ci.com/Penlect/rectangle-packer

.. |Read-the-Docs| image:: https://img.shields.io/readthedocs/rectangle-packer.svg
   :target: https://rectangle-packer.readthedocs.io/en/latest

.. |GitHub-License| image:: https://img.shields.io/github/license/Penlect/rectangle-packer.svg
   :target: https://raw.githubusercontent.com/Penlect/rectangle-packer/travis/LICENSE.md

.. |PyPI-Downloads| image:: https://img.shields.io/pypi/dm/rectangle-packer.svg
   :target: https://pypi.org/project/rectangle-packer
"""

# Module metadata
__author__ = 'Daniel Andersson'
__maintainer__ = __author__
__email__ = 'daniel.4ndersson@gmail.com'
__contact__ = __email__
__copyright__ = 'Copyright (c) 2017 Daniel Andersson'
__license__ = 'MIT'
__url__ = 'https://github.com/Penlect/rectangle-packer'
__version__ = '2.0.2'

# Built-in
from typing import Iterable, Tuple, List

# Extension modules
from ._core import (
    pack as _pack,
    PackingImpossibleError,
    bbox_size,
    packing_density,
    overlapping
)

enclosing_size = bbox_size


def pack(sizes: Iterable[Tuple[int, int]],
         max_width=None, max_height=None) -> List[Tuple[int, int]]:
    """Pack rectangles into a bounding box with minimal area.

    The result is returned as a list of coordinates "(x, y)", which
    specifices the location of each corresponding input rectangle's
    lower left corner.

    The helper function :py:func:`bbox_size` can be used to compute
    the width and height of the resulting bounding box.  And
    :py:func:`packing_density` can be used to evaluate the packing
    quality.

    The algorithm will sort the input in different ways internally so
    there is no need to sort ``sizes`` in advance.

    The GIL is released when C-intensive code is running.  Execution
    time increases by the number *and* size of input rectangles.  If
    this becomes a problem, you might need to implement your own
    `divide-and-conquer algorithm`_.

    **Example**::

        # Import the module
        >>> import rpack

        # Create a bunch of rectangles (width, height)
        >>> sizes = [(58, 206), (231, 176), (35, 113), (46, 109)]

        # Pack
        >>> positions = rpack.pack(sizes)

        # The result will be a list of (x, y) positions:
        >>> positions
        [(0, 0), (58, 0), (289, 0), (289, 113)]

    ..  _`divide-and-conquer algorithm`: https://en.wikipedia.org/wiki/Divide-and-conquer_algorithm

    :param sizes: "(width, height)" of the rectangles to pack.  *Note:
        integer values only!*
    :type sizes: Iterable[Tuple[int, int]]

    :param max_width: Force the enclosing rectangle to not exceed a
        maximum width.  If not possible,
        :py:exc:`rpack.PackingImpossibleError` will be raised.
    :type max_width: Union[None, int]

    :param max_height: Force the enclosing rectangle to not exceed a
        maximum height.  If not possible,
        :py:exc:`rpack.PackingImpossibleError` will be raised.
    :type max_height: Union[None, int]

    :return: List of positions (x, y) of the input rectangles.
    :rtype: List[Tuple[int, int]]
    """
    if max_width is not None and not isinstance(max_width, int):
        raise TypeError("max_width must be an integer")
    if max_height is not None and not isinstance(max_height, int):
        raise TypeError("max_height must be an integer")
    if not isinstance(sizes, list):
        sizes = list(sizes)
    return _pack(sizes, max_width or -1, max_height or -1)
