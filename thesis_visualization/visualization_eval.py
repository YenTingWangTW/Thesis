import json
import random
import streamlit as st
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

with open('./filtered_labels.json', 'r') as f:
    labels = json.load(f)
with open('./labeled_dataset.json', 'r') as f:
    data = json.load(f)
    docs = data['document']
    for k, v in docs.items():
        docs[k] = ', '.join(v[0])
with open('./aug_train_test_labeled_dataset_afterVal.json', 'r') as f:
    dataset = json.load(f)
with open('./eval_results/MaskedSent_generated_summary_newDs_e9.txt', 'r') as f:
    maskedSent_results = [line.rstrip() for line in f]
with open('./eval_results/TML_maskedSent_generated_summary_newDs_e7.txt', 'r') as f:
    TML_results = [line.rstrip() for line in f]
with open('./eval_results/MaskedSent_generated_summary_aug_e4.txt', 'r') as f:
    maskedSent_aug_results = [line.rstrip() for line in f]
with open('./eval_results/TML_maskedSent_generated_summary_aug_e6.txt', 'r') as f:
    TML_aug_results = [line.rstrip() for line in f]
with open('./eval_results/MaskedSent_generated_summary_aug_summNoAug_e2.txt', 'r') as f:
    maskedSent_aug_summNo_results = [line.rstrip() for line in f]
with open('./eval_results/TML_maskedSent_generated_summary_aug_summNoAug_e6.txt', 'r') as f:
    TML_aug_summNo_results = [line.rstrip() for line in f]


def get_key(my_dict, val):
    k_list = []
    for key, value in my_dict.items():
         if val == value:
                k_list.append(key)
    return k_list

model_list = []
for s_t, d_t in zip(dataset['summary_test'], dataset['document_test']):
    model_key = None
    if s_t in labels.values():
        k_list = get_key(labels, s_t)
        if len(k_list) > 1:
            for k in k_list:
                if d_t == docs[k]:
                    model_key = k        
        else:
            model_key = k_list[0]
    model_list.append(model_key)

# # random selection - 25 test samples
# random.seed(25)
# randomlist = random.sample(range(0, 90), 25)
randomlist = range(0, 90)
model_list = [model_list[idx] for idx in randomlist]
test_texts = [dataset['document_test'][idx] for idx in randomlist]
test_labels = [dataset['summary_test'][idx] for idx in randomlist]
maskedSent_results = [maskedSent_results[idx] for idx in randomlist]
TML_results = [TML_results[idx] for idx in randomlist]
maskedSent_aug_results = [maskedSent_aug_results[idx] for idx in randomlist]
TML_aug_results = [TML_aug_results[idx] for idx in randomlist]
maskedSent_aug_summNo_results = [maskedSent_aug_summNo_results[idx] for idx in randomlist]
TML_aug_summNo_results = [TML_aug_summNo_results[idx] for idx in randomlist]

result_dict = {'test_process_models': model_list, 
                'test_texts': test_texts, 
                'test_labels': test_labels, 
                'maskedSent_results': maskedSent_results,
                'TML_results': TML_results,
                'maskedSent_aug_results': maskedSent_aug_results,
                'TML_aug_results': TML_aug_results,
                'maskedSent_aug_summNo_results': maskedSent_aug_summNo_results,
                'TML_aug_summNo_results': TML_aug_summNo_results}

n_process_models = len(result_dict['test_process_models'])
selected_model = st.sidebar.slider(
    'Choose one model to test',
    min_value = 1, max_value = n_process_models
    )


# Create figure
m = result_dict['test_process_models'][selected_model-1]
if m:
    # change folder path to where you store the data
    folder_path = '../../thesis_data/bpmai/models/'
    drawing = svg2rlg(folder_path + m + '.svg')
    png = renderPM.drawToFile(drawing, "process_model.png", fmt = "PNG")
    st.image('process_model.png')
    st.markdown('<br>', unsafe_allow_html=True)

text = result_dict['test_texts'][selected_model-1]
st.markdown('<p style="color:maroon; font-weight: bold; font-size: 18px;">Text:</p>', unsafe_allow_html=True)
st.markdown('<p style="color:peru; font-size: 16px;">%s</p>' %text, unsafe_allow_html=True)
st.markdown('<br>', unsafe_allow_html=True)

maskedSent_results = result_dict['maskedSent_results'][selected_model-1]
TML_results = result_dict['TML_results'][selected_model-1]
maskedSent_aug_results = result_dict['maskedSent_aug_results'][selected_model-1]
TML_aug_results = result_dict['TML_aug_results'][selected_model-1]
maskedSent_aug_summNo_results = result_dict['maskedSent_aug_summNo_results'][selected_model-1]
TML_aug_summNo_results = result_dict['TML_aug_summNo_results'][selected_model-1]

def metrics(key1, key2, key3, key4, key5, key6, HL=False):
    col1, col2, col3 = st.columns(3)
    with col1:
        # only important information should be included
        relevance = st.slider(
        'Relevance',
        min_value = 1, max_value = 5,
        key=key1
        )
    with col2:
        # semantic adequacy - the label is a sufficient representative of process
        informativeness = st.slider(
        'Informativeness',
        min_value = 1, max_value = 5,
        key=key2
        ) 
    with col3:
        # easy to read
        fluency = st.slider(
        'Fluency',
        min_value = 1, max_value = 5,
        key=key3
        )   
    if not HL:
        st.write('Main reason for the choice:')
    else:
        st.write('Best described for the label:')    
    col1, col2, col3 = st.columns(3)
    with col1:
        overview = st.checkbox('Provide good overview', key=key4)
    with col2:
        main_task = st.checkbox('Most important task', key=key5)
    with col3:
        outcome = st.checkbox('Main outcome', key=key6)
    if overview + main_task + outcome > 1:
        st.write('Only one reason can be chosen.')
    st.write('')
    return relevance, informativeness, fluency, overview, main_task, outcome

with st.expander('Model Results'):
    # maskedSent_result
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<p style="color:maroon; font-weight: bold; font-size: 16px;">%s</p>' %maskedSent_results, unsafe_allow_html=True)
    with col2:
            option_1 = st.checkbox('', key='maskedSent_result')  
    if option_1:
         relevance_1, informativeness_1, fluency_1, overview_1, main_task_1, outcome_1 = metrics('r1', 'i1', 'c1', 'o1', 't1', 'out1')

    # TML_maskedSent_result
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<p style="color:maroon; font-weight: bold; font-size: 16px;">%s</p>' %TML_results, unsafe_allow_html=True)
    with col2:
        option_2 = st.checkbox('', key='TML_maskedSent_result')
    if option_2:
        relevance_2, informativeness_2, fluency_2, overview_2, main_task_2, outcome_2 = metrics('r2', 'i2', 'c2', 'o2', 't2', 'out2')

    # maskedSent_aug_result
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<p style="color:maroon; font-weight: bold; font-size: 16px;">%s</p>' %maskedSent_aug_results, unsafe_allow_html=True)
    with col2:
        option_3 = st.checkbox('', key='maskedSent_aug_result')
    if option_3:
        relevance_3, informativeness_3, fluency_3, overview_3, main_task_3, outcome_3 = metrics('r3', 'i3', 'c3', 'o3', 't3', 'out3')

    # TML_maskedSent_aug_result
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<p style="color:maroon; font-weight: bold; font-size: 16px;">%s</p>' %TML_aug_results, unsafe_allow_html=True)
    with col2:
        option_4 = st.checkbox('', key='TML_maskedSent_aug_result')
    if option_4:
        relevance_4, informativeness_4, fluency_4, overview_4, main_task_4, outcome_4 = metrics('r4', 'i4', 'c4', 'o4', 't4', 'out4')

    # maskedSent_aug_summNo_result
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<p style="color:maroon; font-weight: bold; font-size: 16px;">%s</p>' %maskedSent_aug_summNo_results, unsafe_allow_html=True)
    with col2:
        option_5 = st.checkbox('', key='maskedSent_aug_summNo_result')
    if option_5:
        relevance_5, informativeness_5, fluency_5, overview_5, main_task_5, outcome_5 = metrics('r5', 'i5', 'c5', 'o5', 't5', 'out5')

   # TML_maskedSent_aug_summNo_result
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<p style="color:maroon; font-weight: bold; font-size: 16px;">%s</p>' %TML_aug_summNo_results, unsafe_allow_html=True)
    with col2:
        option_6 = st.checkbox('', key='TML_maskedSent_aug_summNo_result')
    if option_6:
        relevance_6, informativeness_6, fluency_6, overview_6, main_task_6, outcome_6 = metrics('r6', 'i6', 'c6', 'o6', 't6', 'out6')
    option_7 = st.checkbox('None of the above is relevant')

label = result_dict['test_labels'][selected_model-1]
with st.expander('Human Label'):
    st.markdown('<p style="color:maroon; font-weight: bold; font-size: 16px;">%s</p>' %label, unsafe_allow_html=True)
    st.write('Compare select model result(s) to the human label:')
    col1, col2, col3 = st.columns(3)
    with col1:
        better = st.checkbox('Better than human label')
    with col2:    
        equal = st.checkbox('Equally good')
    with col3:
        worse = st.checkbox('Worse')
    if better + equal + worse > 1:
        st.write('Only one result can be chosen.')
    title = st.text_input('Labeling suggestion from you (optional):', 'please type...')
 
# option 2
with st.expander('Human Label - option 2'):
    st.markdown('<p style="color:maroon; font-weight: bold; font-size: 16px;">%s</p>' %label, unsafe_allow_html=True)
    relevance_HL, informativeness_HL, fluency_HL, overview_HL, main_task_HL, outcome_HL = metrics('r_HL', 'i_HL', 'c_HL', 'o_HL', 't_HL', 'out_HL', HL=True)
    title = st.text_input('Labeling suggestion from you (optional):', 'please type...', key='HL_2')
 