# Pixel and Frame Size of Andor Zyla 5.5
Author: Zachary Pincus
Date: 2018-05-07
http://zplab.wustl.edu

## Advertised pixel dimensions
- Sensor size: 2560 × 2160 pixles / 16.6 × 14 mm
- Pixel size: 6.5 µm square
- At 5×, 1 pixel ≈ 1.3 µm
- At 7× (10× with 0.7× optocoupler), 1 pixel ≈ 0.93 µm

**Note: these figures are theoretical, assuming perfect optics. This should be verified with the lab's micrometer slide before any sensitive calculations are made.**

## Maximum image field sizes
- With the 1× optocoupler and the Zyla 5.5, a circle of diameter ~1860 pixels can be viewed without vignetting. With the 0.7× optocoupler, a circle ~1760 pixels in diameter is the maximum that will fit.
- The unobstructed diameter, and hence largest possible worm food pad  for a given magnification can be calculated as follows. For the 5× objective and 1× optocoupler: 1860 pixels * 0.0065 sensor mm / pixel * 1 sample mm / 5 sensor mm ≈ 2.42 sample mm.

|Objective|Optocoupler|Max Diameter|
|---------|-----------|------------|
| 5×      | 0.7×      | 3.27 mm    |
| 5×      | 1×        | 2.42 mm    |
| 10×     | 0.7×      | 1.63 mm    |
| 10×     | 1×        | 1.21 mm    |
| 20×     | 0.7×      | 0.817 mm   |
| 20×     | 1×        | 0.605 mm   |
