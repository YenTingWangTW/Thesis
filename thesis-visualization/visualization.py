import json
import streamlit as st
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

selected_masking = st.sidebar.selectbox(
    'Choose one finetuned masking strategy',
    ('Masking not optimized', 'Masking optimized')
    )

selected_result = st.sidebar.selectbox(
    'Choose one finetuned result',
    ('Step1 - Masked sentences result', 'Step2 - Subprocess result')
    )

if selected_masking == 'Masking not optimized':
    if selected_result == 'Step1 - Masked sentences result':
        file = 'results-step1.json'
    else:
        file = 'results-step2.json'
else:
    if selected_result == 'Step1 - Masked sentences result':
        file = 'results-masked-optimized-step1.json'
    else:
        file = 'results-masked-optimized-step2.json'

with open(file, 'r') as f:
    result_dict = json.load(f)

n_process_models = len(result_dict['test_process_models'])
selected_model = st.sidebar.slider(
    'Choose one model to test',
    min_value = 1, max_value = n_process_models
    )


# Create figure
m = result_dict['test_process_models'][selected_model-1]
# change folder path to where you store the data
folder_path = '../thesis_data/data/bpmai/models/'
drawing = svg2rlg(folder_path + m + '.svg')
png = renderPM.drawToFile(drawing, "process_model.png", fmt = "PNG")
st.image('process_model.png')
st.markdown('<br>', unsafe_allow_html=True)

text = result_dict['test_texts'][selected_model-1]
st.markdown('<p style="color:maroon; font-weight: bold; font-size: 18px;">Text:</p>', unsafe_allow_html=True)
st.markdown('<p style="color:peru; font-size: 16px;">%s</p>' %text, unsafe_allow_html=True)
st.markdown('<br>', unsafe_allow_html=True)

result = result_dict['results'][selected_model-1]
with st.expander('Model Result'):
    st.markdown('<p style="color:maroon; font-weight: bold; font-size: 16px;">%s</p>' %result, unsafe_allow_html=True)

label = result_dict['test_labels'][selected_model-1]
with st.expander('Label'):
    st.markdown('<p style="color:maroon; font-weight: bold; font-size: 16px;">%s</p>' %label, unsafe_allow_html=True)
