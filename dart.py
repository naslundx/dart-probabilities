import math
import argparse
import sys

import matplotlib.pyplot as plt
import numpy as np


VALUES = [20, 1, 18, 4, 13, 6, 10, 15, 2, 17, 3, 19, 7, 16, 8, 11, 14, 9, 12, 5]
BULLSEYE_DOUBLE_RADIUS = 7
BULLSEYE_RADIUS = 15
TRIPLE_START_RADIUS = 99
TRIPLE_END_RADIUS = 109
DOUBLE_START_RADIUS = 165
DOUBLE_END_RADIUS = 175
BOARD_SIZE = DOUBLE_END_RADIUS


def rawValueFromAngle(angle):
    angle = (angle + (2 * math.pi / 40)) % (2 * math.pi)
    index = int(angle / (2 * math.pi / 20))
    return VALUES[index]


def cart2pol(x, y):
    radius = math.sqrt(x ** 2 + y ** 2)
    angle = math.atan2(y, x)
    return (radius, angle)


def pol2cart(radius, angle):
    x = radius * math.cos(angle)
    y = radius * math.sin(angle)
    return (x, y)


def value(x, y):
    (radius, angle) = cart2pol(x, y)
    if radius > DOUBLE_END_RADIUS:
        return 0
    if radius < BULLSEYE_DOUBLE_RADIUS:
        return 50
    if radius < BULLSEYE_RADIUS:
        return 25
    if radius < TRIPLE_END_RADIUS and radius > TRIPLE_START_RADIUS:
        return rawValueFromAngle(angle) * 3
    if radius < DOUBLE_END_RADIUS and radius > DOUBLE_START_RADIUS:
        return rawValueFromAngle(angle) * 2
    if radius < DOUBLE_START_RADIUS:
        return rawValueFromAngle(angle)
    return 0


def probabilityAtPoint(x, y, radius, resolution_analysis):
    points, count = 0, 0
    X = x - radius
    while X <= x + radius:
        Y = y - radius
        while Y <= y + radius:
            distance = math.sqrt((x - X) ** 2 + (y - Y) ** 2)
            if distance < radius:
                score = value(X, Y)
                points += score
                count += 1
                if distance < radius / 2:
                    points += score
                    count += 1
            Y += resolution_analysis
        X += resolution_analysis
    return points / count


def scanBoard(inaccuracy, resolution_analysis, resolution_search, print_best, verbose):
    best_probability = 0
    board = []

    y = -BOARD_SIZE / 1.5
    while y <= BOARD_SIZE / 1.5:
        if verbose:
            print("{:.2f}%".format(100 * (y + BOARD_SIZE) / (BOARD_SIZE * 2)))
        row = []
        x = -BOARD_SIZE / 1.5
        while x <= BOARD_SIZE / 1.5:
            probability = probabilityAtPoint(-y, x, inaccuracy, resolution_analysis)
            if probability > best_probability:
                best_probability, best_probability_index = probability, value(-y, x)
                best_prob_x, best_prob_y = -y, x
                if verbose:
                    print(best_probability, best_probability_index)
            row.append(probability)
            x += resolution_search
        board.append(row)
        y += resolution_search

    if print_best:
        print("Best to aim for " + str(best_probability_index) + " at x=" + str(best_prob_x) + ", y=" + str(best_prob_y))
    return board


def main():
    # TODO arg for just trying one location or region (remove /1.5)
    # TODO add gaussian filter for probabilities
    # TODO add docs + readme

    parser = argparse.ArgumentParser(description='Process some integers.')

    parser.add_argument("--save_data", help="save data to file", action="store_true")
    parser.add_argument("--save_image", help="save image to file", action="store_true")
    parser.add_argument("--noshow", help="do not open window", action="store_true")
    parser.add_argument("--print_best", help="print best location found", action="store_true")
    parser.add_argument("-v", "--verbose", help="be verbose during calculations", action="store_true")

    parser.add_argument("--resolution_analysis", help="resolution (mm) in analysis", type=float, default=3.0)
    parser.add_argument("--resolution_search", help="resolution (mm) for search", type=float, default=3.0)
    parser.add_argument("--inaccuracy", help="radius of circular hit area (mm)", type=float, default=50)

    args = parser.parse_args()

    result = scanBoard(args.inaccuracy, args.resolution_analysis, args.resolution_search, args.print_best, args.verbose)
    a = np.array(result)
    filename = "result_" + str(args.inaccuracy)
    if args.save_data:
        np.savetxt(filename + ".txt", a)
        print("Saving to " + filename + ".txt")

    plt.imshow(a, cmap='hot', interpolation='nearest')
    plt.title("Heatmap probabilities, inaccuracy=" + str(args.inaccuracy))

    if args.save_image:
        plt.savefig(filename + ".png")

    if not args.noshow:
        print("Opening window...")
        plt.show()

    return 0


if __name__ == "__main__":
    sys.exit(main())
