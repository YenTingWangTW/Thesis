import glob
import json
import re
import numpy as np
from processing_functions import load_JSON, sort_process_flows 

filtered_id = []
filtered_data = []
min_task = 5
# max_task = 10
flows_extracted = []
models_skipped = []

for f in glob.glob('../thesis_data/data/bpmai/models/*.meta.json'):
    with open(f) as jsonFiles:
        data = json.load(jsonFiles)
        if data['model']['naturalLanguage'] == 'en' and not data['model']['modelName'].isdigit():
            filtered_id.append(data['model']['modelId'])
            filtered_data.append(data)

bpmn20 = [x for x in filtered_data if x['model']['modelingLanguage'] == 'bpmn20']
bpmn20_filtered = [x for x in bpmn20 if ('Task' in x['revision']['elementCounts'].keys()) and x['revision']['elementCounts']['Task'] >= min_task]
# bpmn20_filtered = [x for x in bpmn20 if ('Task' in x['revision']['elementCounts'].keys()) and x['revision']['elementCounts']['Task'] >= min_task and x['revision']['elementCounts']['Task'] <= max_task]

bpmn20_filtered_id = [x['model']['modelId'] for x in bpmn20_filtered]
bpmn20_filtered_id = np.unique(bpmn20_filtered_id)
print('num of bpmn20: ' + str(len(bpmn20_filtered_id)))

temp_training_data = []
temp_gap_sentences = []
# bpmn20_filtered_id = ['69285564', '159373', '448828966', '1536606145']
for file_num in bpmn20_filtered_id:
    pools_and_lanes = False
    file = '../thesis_data/data/bpmai/models/' + file_num + '.json'
    try:
        results = load_JSON(file)
        if len(results) == 4:
            pools_and_lanes = True
            shapes_id = results[0]
            directly_follows = results[1]
            lanes = results[2]
            pools = results[3]
        else:
            shapes_id = results[0]
            directly_follows = results[1]
            flows = results[2]

        stencils = set()
        tasks_subprocesses_id = set()
        # pools_lanes_id = set()
        start_events_id = set()
        end_events_id = set()
        int_events_id = set()
        gateways_count = {}
        closing_gateways_id = set()
        shapes_unwanted_id = set()
        tasks_subprocesses = ['Task', 'CollapsedSubprocess', 'Subprocess']
        gateways = ['Exclusive_Databased_Gateway', 'InclusiveGateway', 'ParallelGateway']
        shapes_unwanted = ['DataObject', 'ITSystem', 'TextAnnotation', 
                        'Association_Undirected', 'Association_Unidirectional', 'MessageFlow']

        for s in shapes_id.keys():
            stencils.add(shapes_id[s])
            if re.match('(Start.)', shapes_id[s]):
                start_events_id.add(s)
            if re.match('(End.)', shapes_id[s]):
                end_events_id.add(s)
            if re.match('(Intermediate.)', shapes_id[s]):
                int_events_id.add(s)
            if shapes_id[s] in gateways:
                gateways_count.update({s: len(directly_follows[s])})
                if len(directly_follows[s]) == 1:
                    closing_gateways_id.add(s)
            if shapes_id[s] in tasks_subprocesses:
                tasks_subprocesses_id.add(s)
            if shapes_id[s] in shapes_unwanted:
                shapes_unwanted_id.add(s)

        for f in directly_follows.copy():
            if f in shapes_unwanted_id:
                directly_follows.pop(f)
            if f in directly_follows.keys() and directly_follows[f]:
                for r in directly_follows[f]:
                    if r in shapes_unwanted_id:
                        directly_follows[f].remove(r)

        closing_gateways_tasks_count = {}
        for g in closing_gateways_id:
            count = 0
            for f in directly_follows.values():
                count += sum(1 if re.match(g, x) else 0 for x in f)
            closing_gateways_tasks_count[g] = count

        for t in tasks_subprocesses_id:
            count = 0
            for f in directly_follows.values():
                count += sum(1 if re.match(t, x) else 0 for x in f)
            if count > 1:
                closing_gateways_tasks_count[t] = count

        for e in end_events_id:
            count = 0
            for f in directly_follows.values():
                count += sum(1 if re.match(e, x) else 0 for x in f)
            if count > 1:
                closing_gateways_tasks_count[e] = count

        shapes_wanted = set.union(tasks_subprocesses_id, start_events_id, end_events_id, int_events_id)
        temp_closing_count = closing_gateways_tasks_count.copy()
        for s in start_events_id:
            data = []
            label = []
            flow = directly_follows[s]
            result = sort_process_flows(flow, directly_follows, shapes_wanted, gateways_count, temp_closing_count)
            result.insert(0,s)
            result_copy = result.copy()      

            if pools_and_lanes:
                names = {}
                for x in lanes.values():
                    names.update(x)
            else:
                names = flows
            
            for n, obj in enumerate(result_copy):
                if (obj in start_events_id) or (obj in int_events_id) or (obj in end_events_id):
                    if obj in names:
                        res = re.findall(r'\(.*?\)', names[obj])
                        if res:
                            names[obj] = res[0][1:-1]
                        else:
                            result.remove(obj)
                if obj in gateways_count:
                    result.remove(obj)
                if (obj in list(tasks_subprocesses_id) + list(int_events_id)) and (n < (len(result_copy)-1)):
                    if result_copy[n+1] in gateways_count:
                        if not result_copy[n+1] in closing_gateways_id:
                            if (obj in names) and (obj in result) and (names[obj] != '<mask_1>'):
                                label.append(names[obj])
                                names[obj] = '<mask_1>'
               
            for r in result:
                if r in names:
                    data.append(names[r])
            
            if len(data) >= 5:
                if label:
                    if len(data) >= 10 and len(label) < 2:
                        if data[0] != '<mask_1>':
                            sent = data.pop(0)
                            label.append(sent)
                            data.insert(0, '<mask_1>')
                        else:
                            if data[-1] != '<mask_1>':
                                sent = data.pop()
                                label.append(sent)
                                data.append('<mask_1>')
                else:
                    if data[0] != '<mask_1>':
                        sent = data.pop(0)
                        data.insert(0, '<mask_1>')
                        label.append(sent)
                    if len(data) >= 10 and data[-1] != '<mask_1>':
                        sent = data.pop()
                        label.append(sent)
                        data.append('<mask_1>')
                temp_training_data.append(data)
                temp_gap_sentences.append(label)
                flows_extracted.append(file_num)
    except:
        # print('file skipped - error occurred')
        print(file_num)
        models_skipped.append(file_num)

training_data = []
for td in temp_training_data:
    td = ", ".join(td)
    training_data.append(td)
gap_sentences = []
for gs in temp_gap_sentences:
    gs = ", ".join(gs)
    gap_sentences.append(gs)

train_dataset = {'document': training_data, 'summary': gap_sentences, 
                'flows_extracted': flows_extracted, 'models_skipped': models_skipped}
summary = {'summary': gap_sentences}
with open('train_dataset.json', 'w') as f:
    json.dump(train_dataset, f)

with open('summary.json', 'w') as f:
    json.dump(summary, f)


    
    
