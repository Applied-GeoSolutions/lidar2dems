---
layout: page
title: "Concepts"
category: doc
date: 2015-05-28 22:36:43
order: 1
---




## Site shapefile




## Interpolation
For areas without a high resolution auxiliary DEM: The most appropriate interpolation technique is selected based on void size and landform typology, and applied on the data immediately surrounding the hole, using SRTM30 derived points inside the hole should it be of a certain size or greater. The best interpolations methods can be generalised as: Kriging or Inverse Distance Weighting interpolation for small and medium size voids in relatively flat low-lying areas; Spline interpolation for small and medium sized voids in high altitude and dissected terrain; Triangular Irregular Network or Inverse Distance Weighting interpolation for large voids in very flat areas, and an advanced Spline Method (ANUDEM) for large voids in other terrains.

## Additional Resources
An explanation of Points2Grid parameters is located here:
http://www.opentopography.org/index.php/Tools/otforge/points2grid

