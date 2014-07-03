import sys
import config
from distance import map_distance
from mapgraph import MapGraph
from mapgraph import map_to_frame_point

MAP_FRAME = config.MAP_FRAME
SVG_SIZE = config.SVG_SIZE
SVG_SCALE = config.SVG_SCALE

def generate_svg(map_graph, trips, frame, scale):
    header = "<html><body>"
    svg_element_open = '<svg width="%d" height="%d" style="border: 1px solid gray">' % (SVG_SIZE[0], SVG_SIZE[1])
    svg_element_close = "</svg>"
    footer = "</body></html>"
    
    print header
    print svg_element_open
    for n in map_graph.nodes.values():
        print n.render(frame, scale)
    for e in map_graph.edges.values():
        print e.render(frame, scale, map_graph.nodes)
    for t in trips:
        x1,y1,x2,y2 = t
        direct_distance = map_distance(x1,y1,x2,y2)
        rail_distance = map_graph.network_distance(x1,y1,x2,y2)
        if rail_distance*1.2 < direct_distance:
            is_using = True
            color = 'blue'
        else:
            is_using = False
            color = 'red'
        cx1,cy1 = map_to_frame_point(x1,y1,frame,scale)
        cx2,cy2 = map_to_frame_point(x2,y2,frame,scale)
        #print '<circle cx="%f" cy="%f" r="10" fill="%s" fill-opacity="0.02"></circle>' % (cx1,cy1,color)
        #print '<circle cx="%f" cy="%f" r="10" fill="%s" fill-opacity="0.02"></circle>' % (cx2,cy2,color)
        if not is_using:
            print '<line x1="%f" y1="%f" x2="%f" y2="%f" stroke="%s" stroke-opacity="0.07"/>' % (cx1,cy1,cx2,cy2,color)
    print svg_element_close
    print footer
    

def main():
    data_files = sys.argv[1:]
    map_graph = MapGraph.read_map(data_files)
    map_graph.compute_apsp()
    trips = [[float(x) for x in l.strip().split(',')] for l in open('../test/trip2.txt').readlines()[1:]]
    generate_svg(map_graph, trips, MAP_FRAME, SVG_SCALE)
    
    
if __name__ == '__main__':
    main()
