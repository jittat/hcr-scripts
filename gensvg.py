import sys
import config
from mapgraph import MapGraph

MAP_FRAME = config.MAP_FRAME
SVG_SIZE = config.SVG_SIZE
SVG_SCALE = config.SVG_SCALE

def generate_svg(map_graph, frame, scale):
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
    print svg_element_close
    print footer
    

def main():
    data_files = sys.argv[1:]
    map_graph = MapGraph.read_map(data_files)
    generate_svg(map_graph, MAP_FRAME, SVG_SCALE)
    
    
if __name__ == '__main__':
    main()
