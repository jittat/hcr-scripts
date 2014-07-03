import config
import sys

from random import random

MAP_FRAME = config.MAP_FRAME

def gen_uniform(n):
    maxh = MAP_FRAME['topleft'][0] - MAP_FRAME['bottomright'][0]
    maxw = MAP_FRAME['bottomright'][1] - MAP_FRAME['topleft'][1]
    trips = []
    for i in range(n):
        x1 = MAP_FRAME['topleft'][1] + random()*maxw
        y1 = MAP_FRAME['bottomright'][0] + random()*maxh
        x2 = MAP_FRAME['topleft'][1] + random()*maxw
        y2 = MAP_FRAME['bottomright'][0] + random()*maxh
        trips.append((x1,y1,x2,y2))
    return trips

def output_trips(trips):
    n = len(trips)
    print n 
    for t in trips:
        print "%f,%f,%f,%f" % (t[0], t[1], t[2], t[3])

def main():
    if len(sys.argv) != 3:
        print 'Usage: python gentrip.py [model] [n]'
        quit()

    model = sys.argv[1]
    n = int(sys.argv[2])

    trips = []
    if model=='uniform':
        trips = gen_uniform(n)

    output_trips(trips)

if __name__ == '__main__':
    main()
