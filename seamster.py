import sys, argparse, io
from math import sin, cos, tau
from PIL import Image, ImageStat, ImageDraw, ImageChops
import numpy as np
from bresenham import bresenham
from functools import cache

IMAGE_DIR = 'images/'
RESULT_PATH = 'out.jpg'
INSTRUCTIONS_PATH = 'instructions.txt'
RESULT_SIZE = 5000
RESULT_SIZE = (RESULT_SIZE, RESULT_SIZE)
NEAR_CULL = 10
THREAD_SUBTRACT = 40

def calculate_nail_coord(nail, total_nails, image_size):
    angle = (nail / total_nails) * tau
    calc_coord = lambda f: min(image_size - 1, max(0, int(round(image_size / 2.0 * (1.0 + f(angle))))))
    return (calc_coord(cos), calc_coord(sin))

@cache
def memo_bresenham(x0, y0, x1, y1):
    return tuple(bresenham(x0, y0, x1, y1))

parser = argparse.ArgumentParser()
parser.add_argument('-i', metavar='iterations', type=int, default=5000, help='number of iterations')
parser.add_argument('-n', metavar='nails', type=int, default=300, help='number of nails on the board')
parser.add_argument('image_name', help='the filename of the image, including the extension')

args = parser.parse_args(sys.argv[1:])

with Image.open(IMAGE_DIR + args.image_name) as image:
    if image.mode != 'CMYK':
        print('Image must be in CMYK')
        exit()
    if image.size[0] != image.size[1]:
        print('Image must be square')
        exit()
    mask = Image.new('CMYK', image.size, (255, 255, 255, 255))
    draw = ImageDraw.Draw(mask)
    draw.ellipse([(0, 0), (image.size[0] - 1, image.size[1] - 1)], (0, 0, 0, 0))
    image = ImageChops.subtract(image, mask)
    bands = [np.asarray(band) for band in image.split()]

    band_means = ImageStat.Stat(image).mean
    total = sum(band_means)
    band_threads = [int(round(mean / total * args.i)) for mean in band_means]
    steps = reversed([(threads, tuple(255 if j == i else 0 for j in range(4)), 'CMYK'[i]) for i, threads in enumerate(band_threads)])

    nail_coords = tuple(calculate_nail_coord(nail, args.n, image.size[0]) for nail in range(args.n))
    result_nail_coords = tuple(calculate_nail_coord(nail, args.n, RESULT_SIZE[0]) for nail in range(args.n))

    with open(INSTRUCTIONS_PATH, 'w') as file:
        result = Image.new('CMYK', RESULT_SIZE)
        draw = ImageDraw.Draw(result)
        total_threaded = 0
        for i, step in enumerate(steps):
            file.write(f'SWITCH TO {step[2]} THREAD\n')
            nail = 0
            for j in range(step[0]):
                file.write(f'{nail}, ')
                best_nail = -1
                most_filled = 0.0
                for k in range(args.n):
                    if (nail + NEAR_CULL >= args.n or k <= (nail + NEAR_CULL)) and \
                            (nail - NEAR_CULL < 0 or k >= (nail - NEAR_CULL)):
                        continue
                    filled = 0.0
                    pixels = 0
                    for coord in memo_bresenham(*nail_coords[nail], *nail_coords[k]):
                        filled += bands[i][coord[1]][coord[0]]
                        pixels += 1
                    filled /= pixels
                    if filled > most_filled:
                        best_nail = k
                        most_filled = filled
                for coord in memo_bresenham(*nail_coords[nail], *nail_coords[best_nail]):
                    bands[i][coord[1]][coord[0]] = max(0, bands[i][coord[1]][coord[0]] - THREAD_SUBTRACT)
                draw.line((result_nail_coords[nail], result_nail_coords[best_nail]), step[1])
                nail = best_nail
                if j % 10 == 0:
                    print(f'{round((j + total_threaded) / args.i * 100, 1)}%', end='\r')
            file.write(f'{nail}\n')
            total_threaded += step[0]

    result.save(RESULT_PATH)
    print("Done!")
