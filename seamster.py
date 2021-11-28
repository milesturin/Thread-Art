import sys
import getopt
from PIL import Image, ImageStat
import numpy as np

IMAGE_DIR = 'images/'

def rbg_to_cmyk_with_black(image):
    """
    bands = tuple(np.asarray(band).astype(float) for band in image.split())
    inv_red = 1.0 - bands[0] / 255.0
    inv_green = 1.0 - bands[1] / 255.0
    inv_blue = 1.0 - bands[2] / 255.0
    black = np.minimum(inv_red, inv_green, inv_blue)
    inv_black = 1.0 - black
    with np.errstate(invalid='ignore', divide='ignore'):
        cyan = ((inv_red - black) / inv_black) * 255.0
        magenta = ((inv_green - black) / inv_black) * 255.0
        yellow = ((inv_blue - black) / inv_black) * 255.0
    print(inv_blue)
    print(black)
    print(inv_blue - black)
    black *= 255.0
    cyan = cyan.astype(int)
    magenta = magenta.astype(int)
    yellow = yellow.astype(int)
    black = black.astype(int)
    zero = cyan * 0
    Image.fromarray(np.uint8(np.dstack((cyan, zero, zero, zero))), 'CMYK').save('c.jpg')
    Image.fromarray(np.uint8(np.dstack((zero, magenta, zero, zero))), 'CMYK').save('m.jpg')
    Image.fromarray(np.uint8(np.dstack((zero, zero, yellow, zero))), 'CMYK').save('y.jpg')
    Image.fromarray(np.uint8(np.dstack((yellow, yellow, yellow))), 'RGB').save('yyy.jpg')
    Image.fromarray(np.uint8(np.dstack((zero, zero, zero, black))), 'CMYK').save('k.jpg')
    return Image.fromarray(np.uint8(np.dstack((cyan, magenta, yellow, black))), 'CMYK')
    """
    return Image.fromarray(np.dstack((np.asarray(image.convert('CMYK'))[:,:,:3], np.asarray(image.convert('L')))), 'CMYK')

try:
    opts, args = getopt.getopt(sys.argv[1:], 'n:')
    iterations = -1
    for opt, arg in opts:
        if opt == '-n':
            iterations = arg
        else:
            raise getopt.GetoptError("Unknown option")
    if iterations == -1 or len(args) == 0:
        raise getopt.GetoptError("Missing argument")
    image_path = IMAGE_DIR + args[0]
except getopt.GetoptError:
    print(f'Invalid arguments. Proper usage:\n{sys.argv[0]} -n <iterations> <image>')
    exit()

with Image.open(image_path, 'CMYK') as image:
    image.save(out.jpg)
    #rbg_to_cmyk_with_black(image).save('out.jpg')

