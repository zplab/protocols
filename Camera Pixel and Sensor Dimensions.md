# Pixel and Sensor Size of Andor Zyla 5.5
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

**Note: these figures are theoretical, assuming perfect optics and exactly 6.5 µm pixels. Pixel sizes should be verified with the lab's micrometer slide before sensitive calculations are made.**

Calibrations:

|   Date   |  Scope  |Objective|Optocoupler|1 pixel = (x)|1 pixel = (y)|
|----------|---------|---------|-----------|-------------|-------------|
|2018-08-03|zpl-9000 | 10×     | 1×        |  0.6431 µm  |  0.6445 µm  |
|2018-08-03|zpl-scope| 10×     | 1×        |  0.6434 µm  |  0.6458 µm  |


## Maximum image field sizes
Roughly, the un-vignetted region for the 0.7× optocoupler is a circle, centered in the middle of the field of view, with a radius of ~0.38× the width of the field. For the 1× optocoupler, the radius is ~0.55x the width of the field (i.e. only the corners are vignetted).

For the Zyla 5.5, this means that the 1x optocoupler permits complete viewing of a circle with a diameter equal to the full height of the 2160 pixel sensor. With the 0.7x optocoupler, a circle with a diameter of ~1945 pixels can be completely viewed.

The maximum unobstructed diameter in millimeters, for any given magnification and optocoupler, can be calculated easily. For example, given a 5× objective and the 1× optocoupler with its 2160 pixel field of view:
```
2160 pixels ⋅ (0.0065 sensor mm / pixel) ⋅ (1 sample mm / 5 sensor mm) ≈ 2.81 sample mm
```

|Objective|Optocoupler|Max Diameter|
|---------|-----------|------------|
| 5×      | 0.7×      | 3.61 mm    |
| 5×      | 1×        | 2.81 mm    |
| 10×     | 0.7×      | 1.81 mm    |
| 10×     | 1×        | 1.40 mm    |
| 20×     | 0.7×      | 0.903 mm   |
| 20×     | 1×        | 0.702 mm   |
| 40×     | 0.7×      | 0.452 mm   |
| 40×     | 1×        | 0.351 mm   |
| 63×     | 0.7×      | 0.287 mm   |
| 63×     | 1×        | 0.223 mm   |

## Camera sensor specifications
All measures below are for 16-bit rolling-shutter slow readout mode. See linked sheets for further detail.

##### [zpl-scope](cameras/VSC-02860.pdf)
- gain: 0.52 e<sup>-</sup>/ADC count
- median read noise: 1.16 e<sup>-</sup> 
- dark current: 0.122 e<sup>-</sup>/pixel/sec

##### [zpl-purple](cameras/VSC-04562.pdf)
- gain: 0.49 e<sup>-</sup>/ADC count
- median read noise: 1.17 e<sup>-</sup> 
- dark current: 0.123 e<sup>-</sup>/pixel/sec

##### [zpl-9000](cameras/VSC-07338.pdf)
- gain: 0.47 e<sup>-</sup>/ADC count
- median read noise: 1.18 e<sup>-</sup> 
- dark current: 0.133 e<sup>-</sup>/pixel/sec

 
