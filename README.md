# Automatic Generation of Activity Labels for Process Fragments


This repository contains the implementation of the *automatic labeling approach for process fragments* proposed in the thesis. Given the text parsed from process fragments, *text summarization techniques* in ML for NLP was adopted to generate process summaries, namely high-level activity labels. Generally speaking, the approach can be utilized to *summarize business processes* to a desired level of abstraction in practice.   

## Context

Process abstraction is an important task to reduce the complexity of (discovered) process models, which enables process stakeholders to better comprehend a modeled process or gain insights from it. Numerous abstraction techniques exist that address this task by detecting sets of low-level process steps that can be grouped into higher-level business activities. However, identifying such groups does not yet lead to useful abstracted process models, since a proper process model needs suitable labels for each of its activities.

## Labeling Approach

<!-- We applied 2-step training and few optimization steps tailored to solve the domain-specifc task with the limited labeled data at hand. For detailed information, please refer to the thesis report or presentation slides. -->

To illustrate the labeling approach, Jupyter notebooks are provided to guide each training step.

- Training steps (should be implemented as ordered below)
    - Control-flow relation learning (optional step)
        - [Further pre-train Pegasus using contrastive learning (self-supervised learning)](https://github.com/YenTingWangTW/Thesis/blob/master/Pegasus_TML.ipynb)
    - 2-step model training
        - [Further pre-train Pegasus using sentence-masking scheme proposed in the original paper (self-supervised learning)](https://github.com/YenTingWangTW/Thesis/blob/master/Pegasus.ipynb)
        - [Fine-tune Pegasus with labeled data (supervised learning)](https://github.com/YenTingWangTW/Thesis/blob/master/Pegasus_Finetuned_and_Automatic_Evaluation.ipynb)

- Automatic evaluation
    - [Auto eval using BERTScore](https://github.com/YenTingWangTW/Thesis/blob/master/Pegasus_Finetuned_and_Automatic_Evaluation.ipynb)

- Data processing
    - [Process model parsing](https://github.com/YenTingWangTW/Thesis/blob/master/data_preprocessing/data_processing.py)

- Human Evaluation
    - [Survey]()
    - [Results]()

- Detailed information
    - [Presentation slides]()
    - [Thesis report]()

## Reference

- [Data collection]()
- [Pegasus model]()
- [BERTScore]()

<!-- ## Environment Setup

- Google Colab, Amazon SageMaker Studio (Kernel: Python 3 Data Science) or equivalent. -->

## To-be added

- Model inference
- WandB training reports
- Streamlit app to visualize results