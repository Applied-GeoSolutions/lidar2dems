---
layout: page
title: "Changelog"
category: dev
date: 2017-04-27 08:20:10
order: 2
---

v1.1.1:
- tests updated (#32)

v1.1.0:
- Working with PDAL release v1.0.1
- When combinining tiles covering a polygon, the entire area is clipped to a buffered version of the polygon. This can greatly reduce processing times when there the tiles are larger and the polygon only covers a small region. This requires PDAL be built with GEOS (see Installation)
- Improved error handling and reporting
- overwrite option added
- set nodata in CHM where either DTM or DSM is nodata
- Calculate CHM in the DTM/DSM pieces rather than the whole to avoid memory errors on large datasets
- Several bug fixes

v1.0.0:
- Initial public release
