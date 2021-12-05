import sys, argparse, io
from math import sin, cos, tau
from PIL import Image, ImageStat, ImageDraw, ImageChops
import numpy as np
from sklearn.cluster import KMeans
from bresenham import bresenham
from functools import cache

IMAGE_DIR = 'images/'
RESULT_PATH = 'out.jpg'
INSTRUCTIONS_PATH = 'instructions.txt'
MASK_COLOR = (255, 0, 255)
ND_MASK_COLOR = np.array(MASK_COLOR)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RESULT_SIZE = 5000
RESULT_SIZE = (RESULT_SIZE, RESULT_SIZE)
NEAR_CULL = 10
MAX_THREAD_SUBTRACT = 0.2

def calculate_nail_coord(nail, total_nails, image_size):
    angle = (nail / total_nails) * tau
    calc_coord = lambda f: min(image_size - 1, max(0, int(round(image_size / 2.0 * (1.0 + f(angle))))))
    return (calc_coord(cos), calc_coord(sin))

@cache
def calculate_pixel_difference(r0, g0, b0, r1, g1, b1):
   return 1.0 - (((abs(r0 - r1) + abs(g0 - g1) + abs(b0 - b1)) ** 4) / ((255.0 * 3.0) ** 4))

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
    print('Trimming image...')
    mask = Image.new('RGB', image.size, BLACK)
    draw = ImageDraw.Draw(mask)
    corners = [(0, 0), (image.size[0] - 1, image.size[1] - 1)]
    draw.ellipse(corners, WHITE)
    image = ImageChops.multiply(image, mask)
    draw.rectangle(corners, MASK_COLOR)
    draw.ellipse(corners, (0, 0, 0))
    image = ImageChops.add(image, mask)

    print('Calculating optimal thread colors...')
    data = np.asarray(image).reshape(image.size[0] * image.size[1], 3)
    data = data[np.all(data != MASK_COLOR, axis=1)]

    km = KMeans(n_clusters=args.k)
    km.fit(data)
    palette = [tuple(round(color) for color in cluster) for cluster in km.cluster_centers_]
    cluster_stakes = [np.count_nonzero(km.labels_ == i) for i in range(args.k)]
    total_stakes = sum(cluster_stakes)
    cluster_threads = [int(round(stake / total_stakes * args.i)) for stake in cluster_stakes]
    total_threads = sum(cluster_threads)
    clusters = sorted(zip(palette, cluster_threads), reverse=True, key=lambda p: p[1])

    data = np.asarray(image)
    fill = np.zeros(image.size, float)
    for i in range(image.size[0]):
        for j in range(image.size[1]):
            if np.logical_not(np.array_equal(data[i][j], ND_MASK_COLOR)):
                fill[i][j] = 1.0

    nail_coords = tuple(calculate_nail_coord(nail, args.n, image.size[0]) for nail in range(args.n))
    result_nail_coords = tuple(calculate_nail_coord(nail, args.n, RESULT_SIZE[0]) for nail in range(args.n))

    with open(INSTRUCTIONS_PATH, 'w') as file:
        result = Image.new('RGB', RESULT_SIZE, WHITE)
        draw = ImageDraw.Draw(result)
        for i, cluster in enumerate(clusters):
            file.write(f'SWITCH TO {str(cluster[0])} THREAD\n')
            nail = 0
            last_index = sum(cluster[1] for cluster in clusters[:i])
            for j in range(cluster[1]):
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
                        filled += calculate_pixel_difference(*cluster[0], *data[coord[0]][coord[1]]) * fill[coord[0]][coord[1]]
                        pixels += 1
                    filled /= pixels
                    if filled > most_filled:
                        best_nail = k
                        most_filled = filled
                for coord in bresenham(*nail_coords[nail], *nail_coords[best_nail]):
                    diff = calculate_pixel_difference(*cluster[0], *data[coord[0]][coord[1]]) #also multiply by fill here?
                    fill[coord[0]][coord[1]] = max(0.0, fill[coord[0]][coord[1]] - diff * MAX_THREAD_SUBTRACT)
                draw.line((result_nail_coords[nail], result_nail_coords[best_nail]), cluster[0])
                nail = best_nail
                if j % 5 == 0:
                    print(f'Threading: {round((last_index + j) / total_threads * 100, 2)}%     ', end='\r')
            file.write(f'{nail}\n')

    result.save(RESULT_PATH)
    print('\nDone!')
