from distance import map_distance
from array import array

RAIL_ADVANTAGE_FACTOR = 3.0

def map_to_frame_point(x, y, frame, scale):
    cx = (x - frame['topleft'][1]) * scale
    cy = (frame['topleft'][0] - y) * scale
    return (cx,cy)

class Node:
    def __init__(self,
                 id='',
                 name='',
                 is_station=False,
                 x=0,
                 y=0,
                 imported_line='',
                 options=None):
        self.id = id
        self.name = name
        self.is_station = is_station
        self.x = x
        self.y = y
        if options:
            self.options = options
        else:
            self.options = {}
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
        return map_to_frame_point(self.x, self.y, frame, scale)

    def render(self, frame, scale):
        cx,cy = self.render_location(frame, scale)
        if self.is_station:
            r = 3
        else:
            r = 1
        if 'color' in self.options:
            return ('<circle cx="%f" cy="%f" r="%f" fill="%s"></circle>' % (cx,cy,r,self.options['color']))
        else:
            return ('<circle cx="%f" cy="%f" r="%f"></circle>' % (cx,cy,r))

class Edge:
    def __init__(self, node_id1, node_id2, options=None):
        self.node_id1 = node_id1
        self.node_id2 = node_id2
        self.node1 = None
        self.node2 = None
        if options:
            self.options = options
        else:
            self.options = {}
        if options and ('adv_factor' in options):
            self.adv_factor = options['adv_factor']
        else:
            self.adv_factor = RAIL_ADVANTAGE_FACTOR

    def associate_nodes(self, nodes):
        self.node1 = nodes[self.node_id1]
        self.node2 = nodes[self.node_id2]

    def length(self):
        return ((map_distance(self.node1.x, self.node1.y,
                              self.node2.x, self.node2.y))/self.adv_factor)

    def render(self, frame, scale, nodes=None):
        if nodes:
            n1 = nodes[self.node_id1]
            n2 = nodes[self.node_id2]
        else:
            n1 = self.node1
            n2 = self.node2
        cx1, cy1 = n1.render_location(frame, scale)
        cx2, cy2 = n2.render_location(frame, scale)
        if 'color' in self.options:
            return ('<line x1="%f" y1="%f" x2="%f" y2="%f" stroke="%s"/>' %
                    (cx1,cy1,cx2,cy2,self.options['color']))
        else:
            return ('<line x1="%f" y1="%f" x2="%f" y2="%f" stroke="black"/>' %
                    (cx1,cy1,cx2,cy2))

    
class MapGraph:
        
    INFINITY = 10000

    def __init__(self, nodes={}, edges={}):
        self.nodes = nodes
        self.edges = edges

        
    @staticmethod
    def __read_from_file(filename,
                         nodes,
                         edges,
                         options=None,
                         node_options=None,
                         edge_options=None):
        fp = open(filename)
        n,m = [int(x) for x in fp.readline().strip().split(',')]

        if not node_options:
            node_options = {}
        if not edge_options:
            edge_options = {}
        if options:
            for option in options:
                key,val = option.split(':')
                if key == 'color':
                    node_options['color'] = val
                    edge_options['color'] = val
                if key == 'adv_factor':
                    edge_options['adv_factor'] = float(val)
        
        for i in range(n):
            l = fp.readline()
            new_node = Node(imported_line=l, options=node_options)
            nodes[new_node.id] = new_node
        for i in range(m):
            l = fp.readline()
            n1,n2 = [x.strip() for x in l.strip().split(',')]
            new_edge = Edge(n1, n2, options=edge_options)
            edges[(n1,n2)] = new_edge

            
    @staticmethod
    def read_map(filenames):
        nodes = {}
        edges = {}
        for fname in filenames:
            MapGraph.__read_from_file(fname, nodes, edges)
        return MapGraph(nodes, edges)

    def append_from_file(self,
                         filename,
                         options=None,
                         node_options=None,
                         edge_options=None):

        MapGraph.__read_from_file(filename,
                                  self.nodes,
                                  self.edges,
                                  options,
                                  node_options,
                                  edge_options)

    def network_distance(self,x1,y1,x2,y2):
        mind = MapGraph.INFINITY
        for n1 in self.nodes.values():
            if not n1.is_station:
                continue
            for n2 in self.nodes.values():
                if not n2.is_station:
                    continue
                ni = self.__idmap[n1.id]
                nj = self.__idmap[n2.id]
                if ni != nj:
                    d = (map_distance(x1,y1,n1.x,n1.y)
                         + self.__d[ni][nj]
                         + map_distance(n2.x,n2.y,x2,y2))
                    if d < mind:
                        #print ">>", n1.id, ni, n2.id, nj, self.__d[ni][nj]
                        mind = d
        return mind

    def compute_apsp(self):
        n = len(self.nodes)
        idmap = {}
        revmap = {}
        i = 0
        for nd in self.nodes.values():
            idmap[nd.id] = i
            revmap[i] = nd
            i += 1

        d = [array('d') for i in range(n)]
        for i in range(n):
            for j in range(n):
                if revmap[i].is_station and revmap[j].is_station:
                    n1 = revmap[i]
                    n2 = revmap[j]
                    d[i].append(map_distance(n1.x, n1.y, n2.x, n2.y))
                else:
                    d[i].append(MapGraph.INFINITY)
        for i in range(n):
            d[i][i] = 0

        for k,e in self.edges.items():
            (nid1,nid2) = k
            u = idmap[nid1]
            v = idmap[nid2]
            e.associate_nodes(self.nodes)
            d[u][v] = e.length()
            d[v][u] = e.length()

        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if d[i][j] > d[i][k] + d[k][j]:
                        d[i][j] = d[i][k] + d[k][j]

        self.__idmap = idmap
        self.__d = d

        
    def export_raw_network(self, filename):
        n = len(self.nodes)
        f = open(filename,'w')
        m = len(self.edges)

        print >> f, n, m

        idmap = {}
        revmap = {}
        i = 0
        for nd in self.nodes.values():
            idmap[nd.id] = i
            revmap[i] = nd

            if nd.is_station:
                station_flag = 1
            else:
                station_flag = 0

            print >> f, i, station_flag, nd.id, nd.x, nd.y

            i += 1

        for k,e in self.edges.items():
            (nid1,nid2) = k
            u = idmap[nid1]
            v = idmap[nid2]
            e.associate_nodes(self.nodes)

            print >> f, u, v, e.length()

        f.close()
        
        
