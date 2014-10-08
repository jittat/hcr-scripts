import sys
import os
import os.path
import config
from distance import map_distance
from mapgraph import MapGraph
from mapgraph import map_to_frame_point

USES_EXTERNAL_COMPUTATION = True

MAP_FRAME = config.MAP_FRAME
SVG_SIZE = config.SVG_SIZE
SVG_SCALE = config.SVG_SCALE

def generate_svg(map_graph, trips, frame, scale, results=None, config=None):
    header = "<html><body>"
    svg_element_open = '<svg width="%d" height="%d" style="border: 1px solid gray">' % (SVG_SIZE[0], SVG_SIZE[1])
    svg_element_close = "</svg>"
    footer = "</body></html>"
    
    #print header
    print svg_element_open
    for n in map_graph.nodes.values():
        print n.render(frame, scale)
    for e in map_graph.edges.values():
        print e.render(frame, scale, map_graph.nodes)
    total_trips = len(trips)
    total_org_distance = 0
    total_org_switch_distance = 0
    total_new_switch_distance = 0

    switched_trips = 0

    tnum = 0
    for t in trips:
        x1,y1,x2,y2 = t

        if not results:
            direct_distance = map_distance(x1,y1,x2,y2)
            rail_distance = map_graph.network_distance(x1,y1,x2,y2)
            #print direct_distance, rail_distance
        else:
            direct_distance = results[tnum][0]
            rail_distance = results[tnum][1]

        total_org_distance += direct_distance
        if rail_distance*1.2 < direct_distance:
            is_using = True
            color = 'blue'
            switched_trips += 1
            travel_distance = rail_distance
            total_org_switch_distance += direct_distance
            total_new_switch_distance += rail_distance
        else:
            is_using = False
            color = 'red'
            travel_distance = direct_distance
        cx1,cy1 = map_to_frame_point(x1,y1,frame,scale)
        cx2,cy2 = map_to_frame_point(x2,y2,frame,scale)
        #print '<circle cx="%f" cy="%f" r="10" fill="%s" fill-opacity="0.01"></circle>' % (cx1,cy1,color)
        #print '<circle cx="%f" cy="%f" r="10" fill="%s" fill-opacity="0.01"></circle>' % (cx2,cy2,color)

        shows_reject = True
        if (config and (len(config['display']) > 0) and
            config['display'][0] == ['accept']):
            shows_reject = False

        if shows_reject:
            if not is_using:
                print '<line x1="%f" y1="%f" x2="%f" y2="%f" stroke="%s" stroke-opacity="0.15"/>' % (cx1,cy1,cx2,cy2,color)
        else:
            if is_using:
                print '<line x1="%f" y1="%f" x2="%f" y2="%f" stroke="%s" stroke-opacity="0.15"/>' % (cx1,cy1,cx2,cy2,color)

        tnum += 1

    print svg_element_close
    print '<br>'
    print '<small>'
    DIST_RATIO = 2./0.140961
    print 'original avarage distance: %.2f<br>' % (float(total_org_distance * DIST_RATIO)/total_trips)
    print '%% switch: %.2f<br>' % (float(switched_trips*100)/total_trips)
    if switched_trips > 0:
        print ('[switch-only-stat] avarage distance before switch: %.2f<br>'
               % (float(total_org_switch_distance*DIST_RATIO)/switched_trips))
        print ('[switch-only-stat] avarage distance after switch: %.2f (%.2f%% faster)<br>'
               % (float(total_new_switch_distance*DIST_RATIO)/switched_trips,
                  100. - total_new_switch_distance*100/total_org_switch_distance))
    print '</small>'
    #print footer

def read_network_config(filename):
    config_map = { 'network': 'networks',
                   'trip': 'trips',
                   'max-walk-distance': 'max-walk-distance',
                   'display': 'display' }

    nconfig = { 'networks': [],
                'trips': [],
                'max-walk-distance': [],
                'display': [] }
    lines = open(filename).readlines()
    for l in lines:
        items = l.strip().split()
        if len(items)==0:
            continue
        if items[0] in config_map:
            nconfig[config_map[items[0]]].append(items[1:])
    return nconfig

def build_map(network_config):
    map_graph = MapGraph()
    for n in network_config['networks']:
        fname = n[0]
        options = n[1:]
        map_graph.append_from_file(fname, options)
    return map_graph

def read_trip(filename):
    return [[float(x) for x in l.strip().split(',')]
            for l in open(filename).readlines()[1:]]

def read_results(filename):
    return [[float(x) for x in l.strip().split()]
            for l in open(filename).readlines()]

def main():
    network_config = read_network_config(sys.argv[1])

    map_graph = build_map(network_config)

    results = None
    if not USES_EXTERNAL_COMPUTATION:
        map_graph.compute_apsp()
    else:
        map_graph.export_raw_network('net.raw')
        calstat_script = os.path.abspath(os.path.join(os.path.dirname(__file__), 'calstat'))

        if (('max-walk-distance' in network_config) and
            (len(network_config['max-walk-distance']) > 0)):
            try:
                max_walk_distance = float(network_config['max-walk-distance'][0][0])
            except:
                max_walk_distance = -1
            cmd = '%s net.raw %s %f > result.out' % (calstat_script,
                                                     sys.argv[2],
                                                     max_walk_distance)
        else:
            cmd = '%s net.raw %s > result.out' % (calstat_script, sys.argv[2])

        os.system(cmd)
        results = read_results('result.out')
        
    if(len(network_config['trips'])==0):
        trips = read_trip(sys.argv[2])

    generate_svg(map_graph,
                 trips,
                 MAP_FRAME,
                 SVG_SCALE,
                 results,
                 network_config)
        
if __name__ == '__main__':
    main()
