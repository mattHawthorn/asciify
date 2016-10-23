#coding:utf-8

import os, argparse
from PIL import Image, ImageFont, ImageDraw
from skimage.measure import *
from numpy import array, argmax, argmin, log, abs, empty, uint8

image_extensions = {'png','jpg','tif'}

def char_chip(char,font,aspect=0.667,bg=255,fill=0,writes = 2,v_offset=-0.18):
    (w,h) = chip_size_from_font(font,aspect)
    image = Image.new("L",(w,h), color = bg)
    chip = ImageDraw.Draw(image)
    for i in range(writes):
        chip.text((int(0*w),int(v_offset*h)), char, fill=fill, font=font)
    return image

def bw_char_chip(char,font):
    return char_chip(char,font,bg=255,fill=0)

def wb_char_chip(char,font):
    return char_chip(char,font,bg=0,fill=255)

def chip_size_from_font(font,aspect=0.667):
    size = font.size
    return (int(aspect*size),size)

def optimal_resize(image,size):
    chip_w,chip_h = size
    w, h = image.width, image.height
    r_w = w % chip_w
    r_h = h % chip_h
    if r_w == 0 and r_h == 0:
        return image
    else:
        n_w = w//chip_w
        n_h = h//chip_h
        aspect = w/h
        small_h = n_h*chip_h
        big_h = (n_h + 1)*chip_h
        small_w = n_w*chip_w
        big_w = (n_w + 1)*chip_w
        resizes = ((small_w,big_h),
                   (big_w,small_h),
                   (big_w,big_h))
        errors = abs(log([(w*h1)/(w1*h) for w1,h1 in resizes]))
        best_resize = resizes[argmin(errors)]
        return image.resize(best_resize)
    
def nearest_chip(chip,chip_dict,sim=compare_ssim):
    names,sims = zip(*((name,sim(array(chip),array(c))) for name,c in chip_dict.items()))
    return names[argmax(sims)]

def nearest_chip_array(image,chip_dict,sim=compare_ssim):
    chip_h,chip_w = array(next(iter(chip_dict.values()))).shape
    w,h = image.width, image.height
    n_w,n_h = w//chip_w, h//chip_h
    # this can now be indexed by (height_index, width_index, :, :) for a chip
    chips = array(image).reshape(n_h,chip_h,n_w,chip_w).swapaxes(1,2)
    return [[nearest_chip(chips[i,j,::],chip_dict,sim=sim) for j in range(chips.shape[1])] for i in range(chips.shape[0])]  

def print_char_array(char_array,file):
    # char_array is assumed a list of lists, as in the output from nearest_chip_array
    with open(file,'w') as f:
        for row in char_array:
            for char in row:
                f.write(char)
            f.write("\n")

def image_from_chars(char_array,chip_dict):
    char_array = array(char_array)
    n_w = char_array.shape[1]
    n_h = char_array.shape[0]
    chip_h,chip_w = next(iter(chip_dict.values())).shape
    image = empty((n_h*chip_h,n_w*chip_w),dtype=uint8)
    for i,h in enumerate(range(0,n_h*chip_h,chip_h)):
        for j,w in enumerate(range(0,n_w*chip_w,chip_w)):
            image[h:(h+chip_h),w:(w+chip_w)] = chip_dict[char_array[i,j]]
    return Image.fromarray(image, "L")

def expand_path(path):
    if ('~' in path):
        return os.path.expanduser(path)
    else:
        return os.path.abspath(path)


def main():
    argParser = argparse.ArgumentParser(add_help=True,description = "A script to take in an image and turn it into ascii art!")
    argParser.add_argument("-i","--input",type=str,
                            help="The image to read in and asciify")
    argParser.add_argument("-o","--output",type=str,
                            help="Path to an image to write out to.\nText will also be written to this path with a .txt extension substituted")
    argParser.add_argument("-f","--font",type=str, default = "cour.ttf",
                            help="The path to the ttf font to use.\nTraditionally, a monospace font is preferred.\nDefault is Courier")
    argParser.add_argument("-s","--size","--font-size",type=int,default=12,
                            help="The size of the font, roughly in pixels, to be overlaid on the image")
    argParser.add_argument("-a","--aspect","--font-aspect",type=int,default=0.6,
                            help="The preferred aspect ratio of character cells for the font, as a ratio of width to height. Default is 0.6")
    argParser.add_argument("--boldness",type=int,default=2,
                            help="The boldness of characters the ascii image.\nInt greater than 0 representing the number of times each char is burned onto the image")
    argParser.add_argument("-b","--background",type=int,default=255,
                            help="The grayscale background color for the ascii image.\nInt between 0 (black) and 255 (white). Default is 255")
    argParser.add_argument("-c","--color","--character-color",type=int,default=0,
                            help="The grayscale color for characters in the ascii image.\nInt between 0 (black) and 255 (white). Default is 0")
    argParser.add_argument("-r","--rescale","--resize",type=float,default=1.0,
                            help="The amount by which to rescale the input image before fitting characters.\nSet this above 1 for higher resolution.")
    
    config = argParser.parse_args()
    
    image_path = expand_path(config.input)
    out_path = expand_path(config.output)
    outname, ext = os.path.splitext(out_path)
    if ext == "":
        ext = ".png"
    
    fontpath = config.font
    fontsize = config.size
    font_color = config.color
    boldness = config.boldness
    bg = config.background
    aspect = config.aspect
    rescaling = config.rescale
    metric = compare_psnr
    
    font = ImageFont.truetype(fontpath, fontsize)
    chip_size = chip_size_from_font(font,aspect)
    
    printable_chars = bytes(range(32,127)).decode('ascii')
    
    chips = {c:array(char_chip(c,font,aspect,bg,font_color,boldness)) for c in printable_chars}
    
    # load the input image
    image = Image.open(image_path)
    # rescale the image to the preferred resolution
    image = image.resize((round(rescaling*image.width), round(rescaling*image.height)))
    # resize optimally for tiling with ascii characters
    image = optimal_resize(image,chip_size).convert("L")
    
    # compute the ascii art
    chars = nearest_chip_array(image,chips,metric)
    # render an image of it
    ascii_art = image_from_chars(chars,chips)
    # save the image
    ascii_art.save(outname + ext)
    # save the ascii text
    print_char_array(chars, outname + ".txt")


if __name__ == '__main__':
    main()
