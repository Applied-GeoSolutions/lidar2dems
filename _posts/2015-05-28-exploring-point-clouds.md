---
layout: page
title: "Exploring Point Clouds"
category: tut
date: 2015-05-28 22:38:03
order: 0
---

The initial dataset most often consists of a series of unclassified LAS files within a single contiguous region. This may be a single LAS file for small areas, or more commonly, a series of swaths correponding with the flight lines of the aircraft or non-overlapping tiles if the swaths were merged together and broken into manageable pieces.

Prior to performing any procesing it is often desirable to examine the data to ensure it is readable, contains the expected fields (dimensions) and meets or exceeds the expected point density (e.g., points/m^2). The pdal info command can be used to output a summary of the dataset:

    $ pdal info filename.las --summary

which will output a summary of the dataset as JSON:

~~~
{
  "filename": "230500-9754000.las",
  "pdal_version": "PDAL 1.0.0.b1 (d281c0) with GeoTIFF 1.4.0 GDAL 1.11.1 LASzip 2.2.0",
  "summary":
  {
    "bounds":
    {
      "X":
      {
        "max": 230999.98999999999,
        "min": 230500
      },
      "Y":
      {
        "max": 9754499.9900000002,
        "min": 9754000
      },
      "Z":
      {
        "max": 541.26999999999998,
        "min": 7.3399999999999999
      }
    },
    "dimensions": "X, Y, Z, Intensity, ReturnNumber, NumberOfReturns, ScanDirectionFlag, EdgeOfFlightLine, Classification, ScanAngleRank, UserData, PointSourceId",
    "num_points": 5871066,
    "spatial_reference": ""
  }
}
~~~


