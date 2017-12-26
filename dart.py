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
    rho = math.sqrt(x ** 2 + y ** 2)
    phi = math.atan2(y, x)
    return (rho, phi)


def pol2cart(rho, phi):
    x = rho * math.cos(phi)
    y = rho * math.sin(phi)
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


def scanBoard(inaccuracy, resolution_analysis, resolution_search):
    best_probability = 0
    board = []

    y = -BOARD_SIZE / 1.5
    while y <= BOARD_SIZE / 1.5:
        print("{:.2f}%".format(100 * (y + BOARD_SIZE) / (BOARD_SIZE * 2)))
        row = []
        x = -BOARD_SIZE / 1.5
        while x <= BOARD_SIZE / 1.5:
            probability = probabilityAtPoint(-y, x, inaccuracy, resolution_analysis)
            if probability > best_probability:
                best_probability = probability
                best_probability_index = value(-y, x)
                best_prob_x = -y
                best_prob_y = x
                print(best_probability, best_probability_index)
            row.append(probability)
            x += resolution_search
        board.append(row)
        y += resolution_search
    
    print("BEST TO AIM FOR: " + str(best_probability_index) + " at x=" + str(best_prob_x) + ", y=" + str(best_prob_y))
    return board


def main():
    # TODO arg for saving best found location
    # TODO arg for just trying one location or region (remove /1.5)
    # TODO save image to file
    # TODO regulate verbosity
    # TODO add gaussian filter for probabilities    
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument("--save", help="save data to file", action="store_true")
    parser.add_argument("--noshow", help="do not open window", action="store_true")
    parser.add_argument("--resolution_analysis", help="resolution (mm) in analysis", type=float, default=3.0)
    parser.add_argument("--resolution_search", help="resolution (mm) for search", type=float, default=3.0)
    parser.add_argument("--inaccuracy", help="radius of circular hit area (mm)", type=float, default=50)
    args = parser.parse_args()

    result = scanBoard(args.inaccuracy, args.resolution_analysis, args.resolution_search)
    a = np.array(result)
    if args.save:
        filename = "result_" + str(inaccuracy) + ".txt"
        np.savetxt(filename, a)
        print("Saving to " + filename)

    if not args.noshow:
        print("Opening window...")
        plt.imshow(a, cmap='hot', interpolation='nearest')
        plt.show()

    return 0


if __name__ == "__main__":
    sys.exit(main())
