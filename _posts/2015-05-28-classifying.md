---
layout: page
title: "Classifying"
category: tut
date: 2015-05-28 22:38:20
order: 1
---

The first step is to classify the ground points using `pdal ground`. The writers.las.format option should be 
used for the SDSU data so that it does not add Time, Red, Green, and Blue dimensions to the file (this specif
ies an earlier LAS format specification...a value of 3, the default, will add them)
$ pdal ground -i input.las -o output.las --classify --writers.las.format=0

# Terrain Types




