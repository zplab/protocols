# ffmpeg usage tips
Author: Zachary Pincus  
Date: 2018-07-25 
http://zplab.wustl.edu


### Convert image files to a movie (simple)
Assuming you have a numbered sequence of images named `image-nnn.png` in some directory, and you want to produce a 10 fps .h264 video (which is what you want) named `movie.mp4`, the following will do the trick:

    ffmpeg -framerate 10 -i path/to/input/image-%03d.png -vcodec libx264 -preset medium -pix_fmt yuv420p movie.mp4

Adjust as required for framerate and image file names. If there are more or fewer digits in the image file numbers, adjust the number in the `%03d` part of the image file name accordingly. If the image filenames are not zero-padded, use `%d`. The `-vcodec libx264` is usually dispensible (it's the default) but best to be safe. You must use `-pix_fmt yuv420p`, otherwise ffmpeg is liable to produce videos in a format that many players can't handle.

### Convert images in memory or from files to a movie
More control is available by using `zplib.image.ffmpeg` (lower-level) or `zplib.image.write_movie` (high-level API) from python to produce movies from image files or images in memory.

### Convert a movie to a sequence of image files

    ffmpeg -i movie.mp4 path/to/output/image-%03d.png
