import sys

MAP_FRAME = {'topleft': (13.831030, 100.437409),
             'bottomright': (13.632925, 100.659538)}
SVG_SIZE = (888, 792)
SVG_SCALE = 4000

class Node:
    def __init__(self,
                 id='',
                 name='',
                 is_station=False,
                 x=0,
                 y=0,
                 imported_line=''):
        self.id = id
        self.name = name
        self.is_station = is_station
        self.x = x
        self.y = y
        if imported_line:
            self.parse_line(imported_line)

            
    def parse_line(self, imported_line):
        items = [x.strip() for x in imported_line.strip().split(',')]
        self.id = items[0]
        self.name = items[1]
        self.is_station = (items[2] == '1')
        self.y = float(items[3])
        self.x = float(items[4])

    def render_location(self, frame, scale):
        cx = (self.x - frame['topleft'][1]) * scale
        cy = (frame['topleft'][0] - self.y) * scale
        return (cx,cy)

    def render(self, frame, scale):
        cx,cy = self.render_location(frame, scale)
        if self.is_station:
            r = 3
        else:
            r = 1
        return '<circle cx="%f" cy="%f" r="%f"></circle>' % (cx,cy,r)

class Edge:
    def __init__(self, node_id1, node_id2):
        self.node_id1 = node_id1
        self.node_id2 = node_id2

    def render(self, nodes, frame, scale):
        n1 = nodes[self.node_id1]
        n2 = nodes[self.node_id2]
        cx1, cy1 = n1.render_location(frame, scale)
        cx2, cy2 = n2.render_location(frame, scale)
        return ('<line x1="%f" y1="%f" x2="%f" y2="%f" stroke="black"/>' %
                (cx1,cy1,cx2,cy2))

class MapGraph:
    def __init__(self, nodes, edges):
        self.nodes = nodes
        self.edges = edges

        
def read_from_file(filename, nodes, edges):
    fp = open(filename)
    n,m = [int(x) for x in fp.readline().strip().split(',')]
    for i in range(n):
        l = fp.readline()
        new_node = Node(imported_line=l)
        nodes[new_node.id] = new_node
    for i in range(m):
        l = fp.readline()
        n1,n2 = [x.strip() for x in l.strip().split(',')]
        new_edge = Edge(n1,n2)
        edges[(n1,n2)] = new_edge

def read_map(filenames):
    nodes = {}
    edges = {}
    for fname in filenames:
        read_from_file(fname, nodes, edges)
    return MapGraph(nodes, edges)

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
        print e.render(map_graph.nodes, frame, scale)
    print svg_element_close
    print footer
    

def main():
    data_files = sys.argv[1:]
    map_graph = read_map(data_files)
    generate_svg(map_graph, MAP_FRAME, SVG_SCALE)
    
    
if __name__ == '__main__':
    main()
