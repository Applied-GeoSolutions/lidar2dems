---
layout: page
title: "Changelog"
category: dev
date: 2015-05-28 22:28:09
order: 2
---

v1.1.0:
- Working with PDAL release v1.0.1
- When combinining tiles covering a polygon, the entire area is clipped to a buffered version of the polygon. This can greatly reduce processing times when there the tiles are larger and the polygon only covers a small region. This requires PDAL be built with GEOS (see Installation)
- Improved error handling and reporting
- overwrite option added
- set nodata in CHM where either DTM or DSM is nodata
- Calculate CHM in the DTM/DSM pieces rather than the whole to avoid memory errors on large datasets 

v1.0.0:
- Initial public release
