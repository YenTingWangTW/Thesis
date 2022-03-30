import glob
import json
import os
import re
import numpy as np

def load_JSON(path_to_json, extract_subprocess = False):
    # function that gets all labels, tasks, pools and lanes
    with open(path_to_json, 'r') as f:
        data = f.read()
        json_data = json.loads(data)
        if 'childShapes' not in json_data.keys():
            print('no elements in '+path_to_json)
            return {}
        elif extract_subprocess:
                (shapes_id, follows, flow), subprocess_name = process_subprocess_no_label(json_data['childShapes'])
                return shapes_id, follows, flow, subprocess_name
        elif pool_exist(path_to_json):
            (shapes_id, follows, lanes), pools = process_pools_and_lanes(json_data['childShapes'])
            return shapes_id, follows, lanes, pools
        else:
            shapes_id, follows, flow = process_flow(json_data['childShapes'])
            return shapes_id, follows, flow
            

def pool_exist(path_to_json):
    meta_file = path_to_json.replace('.json', '.meta.json')
    with open(meta_file, 'r') as f:
        meta_data = f.read()
        json_meta_data = json.loads(meta_data)
        if 'Pool' in json_meta_data['revision']['elementCounts'].keys():
            return True
        else:
            return False     


def process_subprocess_no_label(shapes):
    shapes_id = {}
    follows = {}
    flow = {}
    subprocess_name = ""
    outputs = [shapes_id, follows, flow]
    for shape in shapes:
        shape_stencil = shape['stencil']['id']
        shape_ID = shape['resourceId']
        if shape_stencil == 'SequenceFlow':
            outgoingShapes = [s['resourceId'] for s in shape['outgoing']]
            if shape_ID not in follows.keys():
                follows[shape_ID] = outgoingShapes
            
        if shape_stencil in ['Pool', 'Lane']:
            results = process_subprocess(shape['childShapes'])
            for o, r in zip(outputs, results):
                o.update(r)
                
        if shape_stencil == 'Subprocess':
            results = process_flow(shape['childShapes'])
            for o, r in zip(outputs, results):
                o.update(r)
            if 'name' in shape['properties'] and not shape['properties']['name'] == "":
                subprocess_name = shape['properties']['name'].replace('\n', ' ').replace('\r', '').replace('  ', ' ')
            
    return outputs, subprocess_name

def process_subprocess(shapes):
    subprocess = {}
    
    for shape in shapes:
        if shape['stencil']['id'] in ['Pool', 'Lane']:
            result = process_subprocess(shape['childShapes'])
            subprocess.update(result)
            
        if shape['stencil']['id'] == 'Subprocess' and 'name' in shape['properties'] and not shape['properties']['name'] == "":
            subprocess_name = shape['properties']['name'].replace('\n', ' ').replace('\r', '').replace('  ', ' ')
            task_count = 0
            labels = []
            for childShape in shape['childShapes']:
                if childShape['stencil']['id'] == 'Task':
                    task_count += 1
                    label = childShape['properties']['name'].replace('\n', ' ').replace('\r', '').replace('  ', ' ')
                    labels.append(label)
            if task_count >= 3:
                subprocess.update({subprocess_name: labels})
            
    return subprocess
    
    
def process_flow(shapes):
    shapes_id = {}
    follows = {}
    flow = {}
    tasks_subprocesses = ['Task', 'CollapsedSubprocess', 'Subprocess']
    shapes_unwanted = ['DataObject', 'ITSystem', 'TextAnnotation', 
                      ' Association_Undirected', 'Association_Unidirectional', 'MessageFlow']
    outputs = [shapes_id, follows, flow]

    for shape in shapes:
        shape_stencil = shape['stencil']['id']
        shape_ID = shape['resourceId']
        if shape_stencil in shapes_unwanted:
            continue
        shapes_id.update({shape_ID: shape_stencil})
        
        outgoingShapes = [s['resourceId'] for s in shape['outgoing']]
        if shape_ID not in follows.keys():
            follows[shape_ID] = outgoingShapes
    
        if shape_stencil in tasks_subprocesses:
            if not shape['properties']['name'] == "":
                flow[shape_ID] = shape['properties']['name'].replace('\n', ' ').replace('\r', '').replace('  ', ' ')
            else:
                flow[shape_ID] = 'Task or Subprocess'
        else:
            if 'name' in shape['properties'] and not shape['properties']['name'] == "":
                flow[shape_ID] = shape_stencil + " (" + shape['properties']['name'].replace('\n', ' ').replace('\r', '').replace('  ', ' ') + ")"
            else:
                flow[shape_ID] = shape_stencil

    return outputs
    

def process_pools_and_lanes(shapes):
    shapes_id = {}
    follows = {}
    lanes = {}
    pools = {}
    tasks_subprocesses = ['Task', 'CollapsedSubprocess', 'Subprocess']
    shapes_unwanted = ['DataObject', 'ITSystem', 'TextAnnotation', 
                      ' Association_Undirected', 'Association_Unidirectional', 'MessageFlow']
    outputs = [shapes_id, follows, lanes]

    for shape in shapes:
        shape_stencil = shape['stencil']['id']
        shape_ID = shape['resourceId']
        if shape_stencil in shapes_unwanted:
            continue
        shapes_id.update({shape_ID: shape_stencil})
        outgoingShapes = [s['resourceId'] for s in shape['outgoing']]
        if shape_ID not in follows.keys():
            follows[shape_ID] = outgoingShapes
        
        if shape_stencil == 'Pool':
            if 'name' in shape['properties'] and not shape['properties']['name'] == "":
                pool = shape['properties']['name'].replace('\n', ' ').replace('\r', '').replace('  ', ' ')
            else:
                pool = shape_ID
            results = process_pools_and_lanes(shape['childShapes'])
            for r, o in zip(results[0], outputs):
                o.update(r)
            if len(results[0][2]): #lanes
                pools.update({pool: results[0][2]})
        
        if shape_stencil == 'Lane':
            if shape['childShapes'] != []:
                lane_labels = {}
                for childShape in shape['childShapes']:
                    c_stencil = childShape['stencil']['id']
                    c_shape_ID = childShape['resourceId']
                    if c_stencil == 'Lane':
                        if 'name' in shape['properties'] and not shape['properties']['name'] == "":
                            lane = shape['properties']['name'].replace('\n', ' ').replace('\r', '').replace('  ', ' ')
                        else:
                            lane = shape_ID
                        results = process_pools_and_lanes(shape['childShapes'])
                        for r, o in zip(results[0], outputs):
                            o.update(r)

                    else:
                        if c_stencil in shapes_unwanted:
                            continue
                        shapes_id.update({c_shape_ID: c_stencil})

                        outgoingShapes = [s['resourceId'] for s in childShape['outgoing']]
                        if c_shape_ID not in follows.keys():
                            follows[c_shape_ID] = outgoingShapes

                        if c_stencil in tasks_subprocesses:
                            if not childShape['properties']['name'] == "":
                                lane_labels[c_shape_ID] = childShape['properties']['name'].replace('\n', ' ').replace('\r', '').replace('  ', ' ')
                            else:
                                lane_labels[c_shape_ID] = 'Task or Subprocess'
                        else:
                            if 'name' in childShape['properties'] and not childShape['properties']['name'] == "":
                                lane_labels[c_shape_ID] = c_stencil + " (" + childShape['properties']['name'].replace('\n', ' ').replace('\r', '').replace('  ', ' ') + ")"
                            else:
                                lane_labels[c_shape_ID] = c_stencil

                        if 'name' in shape['properties'] and not shape['properties']['name'] == "":
                            lane = shape['properties']['name'].replace('\n', ' ').replace('\r', '').replace('  ', ' ')
                        else:
                            lane = shape_ID
                        lanes.update({lane: lane_labels})
                
    return outputs, pools

def sort_process_flows(flow, directly_follows, shapes_wanted, gateways_count, temp_closing_count):
    process_flow = []

    for flow_object in flow:
        if flow_object in shapes_wanted and flow_object not in temp_closing_count.keys():
            process_flow.append(flow_object)
        
        if flow_object in gateways_count.keys() and flow_object not in temp_closing_count.keys():
            process_flow.append(flow_object)
            
        if flow_object in temp_closing_count.keys():
            count = temp_closing_count[flow_object]-1
            temp_closing_count.update({flow_object: count})
            if temp_closing_count[flow_object] == 0:
                process_flow.append(flow_object)
            else:
                continue
                    
        if flow_object in directly_follows.keys() and directly_follows[flow_object]: 
            flow = directly_follows[flow_object]
            result = sort_process_flows(flow, directly_follows, shapes_wanted, gateways_count, temp_closing_count)
            process_flow = process_flow + result
            
    return process_flow

    