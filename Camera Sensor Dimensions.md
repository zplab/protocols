# Pixel and Frame Size of Andor Zyla 5.5
Author: Zachary Pincus

Date: 2018-05-07

http://zplab.wustl.edu

## Pixel size in image and sample planes
- Sensor is 2560 × 2160 pixels
- Advertised sensor size is 16.6 × 14 mm
- Advertised pixel size is 6.5 µm square

Sample-plane pixel sizes can be calculated as follows:
```
1 pixel ⋅ (6.5 sensor µm / pixel) ⋅ (1 sample µm / X sensor µm) = Y sample µm
```
Where X is the effective magnification (objective ⋅ optocoupler magnification), and Y is the size of a single pixel on the sample plane.

|Objective|Optocoupler|1 pixel =|
|---------|-----------|---------|
| 5×      | 0.7×      | 1.86 µm |
| 5×      | 1×        | 1.30 µm |
| 10×     | 0.7×      | 0.929 µm|
| 10×     | 1×        | 0.650 µm|
| 20×     | 0.7×      | 0.464 µm|
| 20×     | 1×        | 0.325 µm|
| 40×     | 0.7×      | 0.232 µm|
| 40×     | 1×        | 0.163 µm|
| 63×     | 0.7×      | 0.147 µm|
| 63×     | 1×        | 0.103 µm|

**Note: these figures are theoretical, assuming perfect optics. This should be verified with the lab's micrometer slide before any sensitive calculations are made.**

## Maximum image field sizes
With the 1× optocoupler and the Zyla 5.5, a circle of diameter ~1860 pixels can be viewed without vignetting. With the 0.7× optocoupler, a circle ~1760 pixels in diameter is the maximum that will fit.

The unobstructed diameter, and hence largest possible worm food pad  for a given magnification can be calculated easily. For example, given a 5× objective and the 1× optocoupler with its 1860 pixel field of view:
```
1860 pixels ⋅ (0.0065 sensor mm / pixel) ⋅ (1 sample mm / 5 sensor mm) ≈ 2.42 sample mm
```

|Objective|Optocoupler|Max Diameter|
|---------|-----------|------------|
| 5×      | 0.7×      | 3.27 mm    |
| 5×      | 1×        | 2.42 mm    |
| 10×     | 0.7×      | 1.63 mm    |
| 10×     | 1×        | 1.21 mm    |
| 20×     | 0.7×      | 0.817 mm   |
| 20×     | 1×        | 0.605 mm   |
