# Generating DEM GeoTiffs  with PDAL


1. Classification

The first step is to classify the ground points using `pdal ground`. The writers.las.format option should be used for the SDSU data so that it does not add Time, Red, Green, and Blue dimensions to the file (this specifies an earlier LAS format specification...a value of 3, the default, will add them)

$ pdal ground -i input.las -o output.las --classify --writers.las.format=0

2. Filtering and DEM creation

The main command here is to use `pdal pipeline` with an XML file desribing the filtering and output options. The input and output files can be specified on the command line. The spatial reference system, which is often not included in LAS files can be specified on the command line and will be added to the GeoTIFF output.

Create GeoTiff of density of points
$ pdal pipeline -i density.xml --input.las.filename=input.las --writers.p2g.filename=outputbasename

where 'input.las' is the input filename and outputbasename is the base name of the output to which will be added '.outtype.tif' where outtype is the type of output: den for density

An explanation of Points2Grid parameters is located here:
http://www.opentopography.org/index.php/Tools/otforge/points2grid



# Interpolation

For areas without a high resolution auxiliary DEM: The most appropriate interpolation technique is selected based on void size and landform typology, and applied on the data immediately surrounding the hole, using SRTM30 derived points inside the hole should it be of a certain size or greater. The best interpolations methods can be generalised as: Kriging or Inverse Distance Weighting interpolation for small and medium size voids in relatively flat low-lying areas; Spline interpolation for small and medium sized voids in high altitude and dissected terrain; Triangular Irregular Network or Inverse Distance Weighting interpolation for large voids in very flat areas, and an advanced Spline Method (ANUDEM) for large voids in other terrains.
