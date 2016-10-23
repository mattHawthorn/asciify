# asciify
### it's all in the docs:

    python3 asciify.py --help

    usage: asciify.py [-h] [-i INPUT] [-o OUTPUT] [-f FONT] [-s SIZE] [-a ASPECT]
                      [--boldness BOLDNESS] [-b BACKGROUND] [-c COLOR]
                      [-r RESCALE]

    A script to take in an image and turn it into ascii art!

    optional arguments:
      -h, --help            show this help message and exit
      -i INPUT, --input INPUT
                            The image to read in and asciify
      -o OUTPUT, --output OUTPUT
                            Path to an image to write out to. Text will also be
                            written to this path with a .txt extension substituted
      -f FONT, --font FONT  The path to the ttf font to use. Traditionally, a
                            monospace font is preferred. Default is Courier
      -s SIZE, --size SIZE, --font-size SIZE
                            The size of the font, roughly in pixels, to be
                            overlaid on the image
      -a ASPECT, --aspect ASPECT, --font-aspect ASPECT
                            The preferred aspect ratio of character cells for the
                            font, as a ratio of width to height. Default is 0.6
      --boldness BOLDNESS   The boldness of characters the ascii image. Int
                            greater than 0 representing the number of times each
                            char is burned onto the image
      -b BACKGROUND, --background BACKGROUND
                            The grayscale background color for the ascii image.
                            Int between 0 (black) and 255 (white). Default is 255
      -c COLOR, --color COLOR, --character-color COLOR
                            The grayscale color for characters in the ascii image.
                            Int between 0 (black) and 255 (white). Default is 0
      -r RESCALE, --rescale RESCALE, --resize RESCALE
                            The amount by which to rescale the input image before
                            fitting characters. Set this above 1 for higher
                            resolution.

![](/example/ascii_mandelbrot.png)
