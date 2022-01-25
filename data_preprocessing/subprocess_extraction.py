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
training_label = []
# bpmn20_filtered_id = ['69285564', '159373', '448828966', '1536606145']
for file_num in bpmn20_filtered_id:
    pools_and_lanes = False
    file = '../thesis_data/data/bpmai/models/' + file_num + '.json'
    try:
        subprocess = load_JSON(file, extract_subprocess=True)
        if subprocess:
            print(subprocess)
            for k, v in subprocess.items():
                temp_training_data.append(v)
                training_label.append(k)
                flows_extracted.append(file_num)
    except:
        # print('file skipped - error occurred')
        print(file_num)
        models_skipped.append(file_num)

training_data = []
for td in temp_training_data:
    td = ", ".join(td)
    training_data.append(td)


train_subprocess = {'document': training_data, 'summary': training_label, 
                'flows_extracted': flows_extracted, 'models_skipped': models_skipped}
with open('train_subprocess.json', 'w') as f:
    json.dump(train_subprocess, f)


    
    
