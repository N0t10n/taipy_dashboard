from taipy.gui import Gui, navigate, Icon, notify
import pyppex as px, pandas as pd
import os

from utils import get_curves, get_figure, get_segments, get_units, get_unit_info, load_file, save_files, get_min_max_score

def on_login(state):
    # Put your own authentication system here
    if state.username == "dev" and state.password == "":
        state.menu += [('dev', Icon('icons/code-solid.svg', 'DEV'))]
        state.login_open = False
        notify(state, "success", "Logged in!")
    
    elif state.username == '' and state.password == '':
        state.pages.pop('dev')
        state.login_open = False
        notify(state, "success", "Logged in!")

    else:
        notify(state, "error", "Wrong username or password")

def on_menu(state, id, payload):
    page = payload['args'][0]
    navigate(state, to=page)

def on_change(state, var_name, var_value):

    if var_name == 'list_of_files':
        save_files(var_value if isinstance(var_value, list) else [var_value])
        state.list_of_files = [os.path.join('data', i) for i in os.listdir('data')]

    elif var_name == 'file_path':
        state.file = load_file(var_value)
        state.file['context_units'] = {i+1:e[1] for i,e in enumerate(sorted(state.file['context_units'].items(), key=lambda x: x[1]['start_time']))} # Sort and modify key

        state.iabs = list(set([state.file['context_units'][i]['class'] for i in state.file['context_units']]))
        state.colored_iabs = {e:state.colors[i%len(state.colors)] for i,e in enumerate(sorted(state.iabs))}

        state.units = get_units(state.file, state.iabs)
        state.figure_data = get_curves(state.file, state.units)
        state.list_of_units = [(int(i), f'Context-unit {i}') for i in state.file['context_units']]
        state.max_units = len(state.file['context_units'])
        state.units_chosen = [str(i[0]) for i in state.units]

        state.figure = get_figure(state.file, state.figure_data, state.iabs, state.units, state.units_chosen, state.score_chosen, state.score_range, state.duration_range, state.colored_iabs)

        state.unit_chosen = 1
        state.info, state.text, state.segments, state.keywords = get_unit_info(state.unit_chosen, state.file)
        state.unit_info = pd.DataFrame([{'Parameter':k, 'Value':v} for k,v in state.info.items()])
        state.unit_text = [(1, state.text)]
        state.unit_segments = get_segments(state.file, state.unit_chosen)
        state.unit_keywords = pd.DataFrame([i[0] for i in state.file['context_units'][unit_chosen]['keywords']['keywords']], columns=['Keyword'])

        state.data_all_versions = pd.DataFrame({'Module':state.file['all-version'].keys(), 'Version': state.file['all-version'].values()})
        state.data_iab_general = pd.DataFrame({'':state.file['iab_general'].keys(), 'Value':state.file['iab_general'].values()})
        state.data_info_video = pd.DataFrame({'':state.file['info_video'].keys(), 'Value':state.file['info_video'].values()})
        state.data_tappx_data = pd.DataFrame({'':state.file['tappx-data'].keys(), 'Value':state.file['tappx-data'].values()})
        state.data_global_keywords = pd.DataFrame([i[0] for i in state.file['global_keywords']], columns=['Keyword'])
        state.data_others = {'Parameter':['is_inappropiate', 'global_sentiment'], 'Value':[state.file['is_inappropiate'], state.file['global_sentiment']]}

        notify(state, "success", "File successfully loaded")

    elif var_name == 'score_chosen':
        state.score_range = get_min_max_score(state.figure_data, state.score_chosen)
        state.figure = get_figure(state.file, state.figure_data, state.iabs, state.units, state.units_chosen, state.score_chosen, state.score_range, state.duration_range, state.colored_iabs)
    
    elif var_name == 'score_range':
        state.figure = get_figure(state.file, state.figure_data, state.iabs, state.units, state.units_chosen, state.score_chosen, state.score_range, state.duration_range, state.colored_iabs)
    
    elif var_name == 'duration_range':
        state.figure = get_figure(state.file, state.figure_data, state.iabs, state.units, state.units_chosen, state.score_chosen, state.score_range, state.duration_range, state.colored_iabs)

    elif var_name == 'units_chosen':
        state.figure = get_figure(state.file, state.figure_data, state.iabs, state.units, state.units_chosen, state.score_chosen, state.score_range, state.duration_range, state.colored_iabs)

    elif var_name == 'unit_chosen':
        state.unit_chosen = var_value[0] if isinstance(var_value, list) else int(var_value)
        state.max_units = len(state.file['context_units'])

        state.info, state.text, state.segments, state.keywords = get_unit_info(state.unit_chosen, state.file)
        state.unit_info = pd.DataFrame([{'Parameter':k, 'Value':v} for k,v in state.info.items()])
        state.unit_text = [(1, state.text)]
        state.unit_segments = get_segments(state.file, state.unit_chosen)
        state.unit_keywords = pd.DataFrame(state.keywords, columns=['Keyword'])


# LOGIN VARS
login_open = True
username = ''
password = ''

# LOAD VARS (load_md)
list_of_files = [os.path.join('data', i) for i in os.listdir('data')]
file_path =  'data/pre-cu-antesdeperder.json'
file = load_file(file_path)
file['context_units'] = {i+1:e[1] for i,e in enumerate(sorted(file['context_units'].items(), key=lambda x: x[1]['start_time']))} # Sort and modify key

# GENERAL VARS (load_md, user_md, dev_md)
menu = [('load', Icon('icons/file-arrow-up-solid.svg', 'Load files')), ('user', Icon('icons/chart-line-solid.svg', 'Viewer'))]
text1 = 'For multiple selection hold Ctrl + right click for single selection or hold Shift + right range selection.\nBy selecting an IAB category, all nested Context-units are selected or diselected if was previously selected.'
text2 = 'Select a single Context-unit for inspection wether using the selector below or through the Units column.'
colors = ['#636efa', '#EF553B', '#00cc96', '#ab63fa', '#FFA15A', '#19d3f3', '#FF6692', '#B6E880', '#56a3c7', '#37ff83', '#fad263', '#c783ff',
          '#6ea1ff', '#ff5e5e', '#8583ff', '#83ffcb', '#e4ff83', '#b34242', '#3b7ba0', '#8444a1', '#3d9276', '#b1af56', '#b86747', '#775c99']
df_vars = ['class', 'start_time', 'end_time', 'duration', 'score', 'zscore']

data = [file['context_units'][i] for i in file['context_units']]
iabs = list(set([file['context_units'][i]['class'] for i in file['context_units']]))
colored_iabs = {e:colors[i%len(colors)] for i,e in enumerate(sorted(iabs))}
units = get_units(file, iabs)

# graph vars
score_chosen = 'Score'
score_range = [0, 1]
duration_range = [0, 1]
units_chosen = [str(i[0]) for i in units]
figure_data = get_curves(file, units)
figure = get_figure(file, figure_data, iabs, units, units_chosen, score_chosen, score_range, duration_range, colored_iabs)

# context-unit inspection
max_units = len(file['context_units'])
list_of_units = [(int(i), f'Context-unit {i}') for i in file['context_units']]
unit_chosen = 1
info, text, segments, keywords = get_unit_info(unit_chosen, file)
unit_info = pd.DataFrame([{'Parameter':k, 'Value':v} for k,v in info.items()])
unit_text = [(1, text)]
unit_segments = get_segments(file, unit_chosen)
unit_keywords = pd.DataFrame(keywords, columns=['Keyword'])

# global vars
data_all_versions = pd.DataFrame({'Module': list(file['all-version'].keys()), 'Version': list(file['all-version'].values())})
data_iab_general = pd.DataFrame({'Parameter':file['iab_general'].keys() , 'Value':file['iab_general'].values()})
data_info_video = pd.DataFrame({'Parameter':file['info_video'].keys() , 'Value':file['info_video'].values()})
data_tappx_data = pd.DataFrame({'Parameter':file['tappx-data'].keys() , 'Value':file['tappx-data'].values()})
data_global_keywords = pd.DataFrame([i[0] for i in file['global_keywords']], columns=['Keyword'])
data_others = {'Parameter':['is_inappropiate', 'global_sentiment'], 'Value':[str(file['is_inappropiate']), file['global_sentiment']]}



login_md = """
<|{login_open}|dialog|title=Login|width=30%|
**Username**
<|{username}|input|label=Username|class_name=fullwidth|>

**Password**
<|{password}|input|password|label=Password|class_name=fullwidth|>

<br/>
<|Sign in|button|class_name=fullwidth plain|on_action=on_login|>
|>
"""
load_md = """
<|menu|label=Menu|lov={menu}|on_action=on_menu|>
<h1>Contextual Lab</h1>

<center><|{list_of_files}|file_selector|extensions=.json|multiple|label=Upload files|drop_message=Drop here|></center>
<center><|{file_path}|selector|lov={list_of_files}|></center>
"""
user_md = """
<|menu|label=Menu|lov={menu}|on_action=on_menu|>

<|Global information|expandable|expanded=False|partial={partial1}|>


<h3>Context-units overview</h3>
<center><|{text1}|></center>
<center><|{score_range}|slider|min=0|max=1|step=0.1|continuous=False|hover_text=Score range|></center>

<|card|
<center>**IAB contextualization over time**</center>
<|layout|columns=4 1|
    <|
<|chart|figure={figure}|height=48vh|>
    |>
    <|
<|{units_chosen}|tree|lov={units}|multiple|height=453px|value_by_id|class_name=test|id=tree1|>
    |>
|>
|>


<h3>Context-unit inspection</h3>
<center><|{text2}|></center>
<center><|{unit_chosen}|selector|lov={list_of_units}|dropdown|value_by_id|></center>


<|layout|columns=1 1 1 1|
    <|
<h5>Units</h5>
<|{unit_chosen}|tree|lov={units}|expanded=False|filter|select_leafs_only|value_by_id|height=469px|id=tree1|>
    |>
    <|
<h5>Parameters</h5>
<|{unit_info}|table|height=45vh|>
    |>
    <|
<h5>Text</h5>
<|tree|lov={unit_text}|height=469px|>
    |>
    <|
<h5>Keywords</h5>
<|{unit_keywords}|table|height=45vh|>
    |>
|>
"""
dev_md = """
<|menu|label=Menu|lov={menu}|on_action=on_menu|>

<|Global information|expandable|expanded=False|partial={partial1}|>


<h3>Context-units overview</h3>
<center><|{text1}|></center>
<|layout|columns=1 1|
    <|
<center><|{score_chosen}|toggle|lov=Score;Z-Score|hover_text=Hyperparameter selection|></center>
<center><|{score_range}|slider|min=-3|max=3|step=0.1|continuous=False|hover_text={score_chosen} range|></center>
    |>
    <|
<center><|toggle|lov=Duration-ratio|></center>
<center><|{duration_range}|slider|max=1|step=0.1|continuous=False|hover_text=Duration-ratio range|></center>
    |>
|>

<|card|
<center>**IAB contextualization over time**</center>
<|layout|columns=4 1|
    <|
<|chart|figure={figure}|height=48vh|>
    |>
    <|
<|{units_chosen}|tree|lov={units}|multiple|height=453px|value_by_id|class_name=test|id=tree1|>
    |>
|>
|>


<h3>Context-unit inspection</h3>
<center><|{text2}|></center>
<center><|{unit_chosen}|selector|lov={list_of_units}|dropdown|value_by_id|></center>


<|layout|columns=1 1 1 1 1|
    <|
<h5>Units</h5>
<|{unit_chosen}|tree|lov={units}|expanded=False|filter|select_leafs_only|value_by_id|height=45vh|id=tree1|>
    |>
    <|
<h5>Segments</h5>
<|tree|lov={unit_segments}|expanded=False|filter|select_leafs_only|height=45vh|>
    |>
    <|
<h5>Parameters</h5>
<|{unit_info}|table|height=381px|>
    |>
    <|
<h5>Text</h5>
<|tree|lov={unit_text}|height=45vh|>
    |>
    <|
<h5>Keywords</h5>
<|{unit_keywords}|table|height=360px|>
    |>
|>
"""
expandable_1 = """
<|layout|columns=1 1 1|gap=50px|
    <|
<h5>Global keywords</h5>
<|{data_global_keywords}|table|rebuild|page_size_options=50|filter=True|height=56vh|>
    |>
    <|
<h5>All versions</h5>
<|{data_all_versions}|table|show_all|rebuild|>
<h5>Tappx data</h5>
<|{data_tappx_data}|table|show_all|rebuild|>
    |>
    <|
<h5>Info video</h5>
<|{data_info_video}|table|show_all|rebuild|>
<h5>IAB general</h5>
<|{data_iab_general}|table|show_all|rebuild|>
<h5>Others</h5>
<|{data_others}|table|show_all|rebuild|>
    |>
|>
"""

pages = {
    "/": login_md,
    "load": load_md,
    "user": user_md,
    "dev": dev_md
}

stylekit = {
    "primary_color": "#8444a1",
    "selected": "#b7e085"
}


if __name__ == '__main__':
    app = Gui(pages=pages)
    partial1 = app.add_partial(expandable_1)
    app.run(debug=True, use_reloader=True, port=5001, stylekit=stylekit)
