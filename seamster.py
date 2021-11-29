import sys, argparse, io
from PIL import Image, ImageStat, ImageDraw, ImageChops
import numpy as np

IMAGE_DIR = 'images/'

parser = argparse.ArgumentParser()
parser.add_argument('-n', metavar='iterations', type=int, default=5000, help='number of iterations')
parser.add_argument('--ideal', action='store_true', help='allows the algorithm to start from any nail each iteration')
parser.add_argument('image_name', help='the filename of the image, including the extension')

args = parser.parse_args(sys.argv[1:])

with Image.open(IMAGE_DIR + args.image_name) as image:
    if image.mode != 'CMYK':
        print('Image must be in CMYK')
        exit()
    mask = Image.new('CMYK', image.size, (255, 255, 255, 255))
    draw = ImageDraw.Draw(mask)
    draw.ellipse([(0, 0), (image.size[0] - 1, image.size[1] - 1)], (0, 0, 0, 0))
    image = ImageChops.subtract(image, mask)

    band_means = ImageStat.Stat(image).mean #try rms
    total = sum(band_means)
    band_threads = [int(round(mean / total * args.n)) for mean in band_means]

    for i, threads in enumerate(band_threads):
        for j in range(threads):

