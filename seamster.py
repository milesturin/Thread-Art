import sys, argparse, io
from math import sin, cos, tau
from PIL import Image, ImageStat, ImageDraw, ImageChops
import numpy as np
from sklearn.cluster import KMeans
from bresenham import bresenham

IMAGE_DIR = 'images/'
RESULT_PATH = 'out.jpg'
INSTRUCTIONS_PATH = 'instructions.txt'
MASK_COLOR = np.array([255, 0, 255])
RESULT_SIZE = 5000
RESULT_SIZE = (RESULT_SIZE, RESULT_SIZE)
NEAR_CULL = 10
THREAD_SUBTRACT = 40

def calculate_nail_coord(nail, total_nails, image_size):
    angle = (nail / total_nails) * tau
    calc_coord = lambda f: min(image_size - 1, max(0, int(round(image_size / 2.0 * (1.0 + f(angle))))))
    return (calc_coord(cos), calc_coord(sin))

parser = argparse.ArgumentParser()
parser.add_argument('-i', metavar='iterations', type=int, default=5000, help='number of iterations')
parser.add_argument('-n', metavar='nails', type=int, default=300, help='number of nails on the board')
parser.add_argument('-k', metavar='colors', type=int, default=4, help='number of colors of thread')
parser.add_argument('image_name', help='the filename of the image, including the extension')
#parser.add_argument('color_palette', nargs='+', type=lambda x: int(x, 0), help='N hexidecimal numbers representing the different colors of thread used.')

args = parser.parse_args(sys.argv[1:])

with Image.open(IMAGE_DIR + args.image_name) as image:
    if image.mode != 'RGB':
        print('Image must be in RGB')
        exit()
    if image.size[0] != image.size[1]:
        print('Image must be square')
        exit()
    mask = Image.new('RGB', image.size, (0, 0, 0))
    draw = ImageDraw.Draw(mask)
    corners = [(0, 0), (image.size[0] - 1, image.size[1] - 1)]
    draw.ellipse(corners, (255, 255, 255))
    image = ImageChops.multiply(image, mask)
    draw.rectangle(corners, tuple(MASK_COLOR))
    draw.ellipse(corners, (0, 0, 0))
    image = ImageChops.add(image, mask)

    data = np.asarray(image).reshape(image.size[0] * image.size[1], 3)
    data = data[np.all(data != MASK_COLOR, axis=1)]

    km = KMeans(n_clusters=args.k)
    km.fit(data)
    print(km.cluster_centers_)
    
"""
    band_means = ImageStat.Stat(image).mean[::-1]
    total = sum(band_means)
    band_threads = [int(round(mean / total * args.i)) for mean in band_means]

    nail_coords = tuple(calculate_nail_coord(nail, args.n, image.size[0]) for nail in range(args.n))
    result_nail_coords = tuple(calculate_nail_coord(nail, args.n, RESULT_SIZE[0]) for nail in range(args.n))

    with open(INSTRUCTIONS_PATH, 'w') as file:
        result = Image.new('CMYK', RESULT_SIZE)
        draw = ImageDraw.Draw(result)
        last_index = 0

        for i, threads in enumerate(band_threads):
            line_color = [0, 0, 0, 0]
            line_color[3 - i] = 255
            line_color = tuple(line_color)
            file.write(f'SWITCH TO {"KYMC"[i]} THREAD\n')
            nail = 0
            for j in range(threads):
                file.write(f'{nail}, ')
                best_nail = -1
                most_filled = 0.0
                for k in range(args.n):
                    if (nail + NEAR_CULL >= args.n or k <= (nail + NEAR_CULL)) and \
                            (nail - NEAR_CULL < 0 or k >= (nail - NEAR_CULL)):
                        continue
                    filled = 0.0
                    pixels = 0
                    for coord in bresenham(*nail_coords[nail], *nail_coords[k]):
                        filled += bands[i][coord[1]][coord[0]]
                        pixels += 1
                    filled /= pixels
                    if filled > most_filled:
                        best_nail = k
                        most_filled = filled
                for coord in bresenham(*nail_coords[nail], *nail_coords[best_nail]):
                    bands[i][coord[1]][coord[0]] = max(0, bands[i][coord[1]][coord[0]] - THREAD_SUBTRACT)
                draw.line((result_nail_coords[nail], result_nail_coords[best_nail]), line_color)
                nail = best_nail
                if j % 10 == 0:
                    print(f'{round(j / threads * 100)}%', end='\r')
            file.write(str(nail))
            print(f'{"KYMC"[i]} band done')

    result.save(RESULT_PATH)"""
