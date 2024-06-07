import pyppex as px, numpy as np
import plotly.graph_objects as go
from functools import wraps
from pathlib import Path
import logging, json, re



rfh = logging.handlers.RotatingFileHandler(
    filename='main.log', 
    mode='a',
    maxBytes=5*1024*1024,
    backupCount=1,
    encoding=None,
    delay=0
)

logging.basicConfig(
    level=logging.ERROR,
    format="[%(asctime).19s] [%(filename)s -> %(funcName)s():%(lineno)s] %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[rfh]
)

def logger(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except Exception:
            logging.error(f'An error occurred at {func.__name__}:', exc_info=True)
    return wrapper


@logger
def save_files(list_file_path) -> None:
    for file in list_file_path:
        if file == 'pre-cu-antesdeperder.json':
            continue
        with open(file, 'r', encoding='utf-8') as file_in:
            data = json.load(file_in)

            file_name = Path(file)
            file_name = file_name.__str__().replace(file_name.parent.__str__(), 'data')
            file_name = re.sub(r'\.\d+\.', '.', file_name)
            with open(file_name, 'w', encoding='utf-8') as fp:
                json.dump(data, fp, indent=4, ensure_ascii=False)

@logger
def load_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as fp:
        file = json.load(fp)

    return file

@logger
def parse_selection(file, iabs, units, units_chosen) -> dict[str, list[str]]:
    selection = [int(i) for i in units_chosen if '.' not in i]
    for u in units_chosen:
        if u.__contains__('.'):
            childs = [j[0] for i in units for j in i[2] if i[0]==float(u)]
            selection += childs
    
    out = {}
    for i in sorted(iabs):
        temp = []
        for j in selection:
            if file['context_units'][j]['class'] == i:
                temp.append(str(j))
        
        if temp:
            out[i] = temp
    
    return out

@logger
def get_curves(file, units) -> dict[str, dict[str, dict[str, list[float]]]]:
    '''type: score type'''
    y_data = {}
    for i in units:
        temp = {}
        for j in i[2]:
            temp2 = {}
            contx = file['context_units'][j[0]]

            x_score = [contx['score']] * contx['duration']
            x_zscore = [contx['zscore']] * contx['duration']

            curve = np.zeros(contx['start_time'])
            temp2['score'] = curve.tolist() + x_score + np.zeros(int(file['info_video']['duration']) - len(curve)).tolist()
            temp2['zscore'] = curve.tolist() + x_zscore + np.zeros(int(file['info_video']['duration']) - len(curve)).tolist()
            temp2['duration-ratio'] = contx['duration-ratio']
            temp[j[1]] = temp2
        
        y_data[i[1]] = temp

    return y_data

@logger
def get_min_max_score(data, score) -> list[float, float]:
    score = score.replace('-', '').lower() if '-' in score else score.lower()

    data_scores = list(map(lambda x: [v[score] for k,v in x[1].items()], data.items()))
    max_score = np.max([np.max(j) for i in data_scores for j in i])
    min_score = np.min([np.min(j) for i in data_scores for j in i])

    return [np.floor(min_score), np.ceil(max_score)]

@logger
def get_figure(file, data, iabs, units, units_chosen, score, score_range, duration_range, colors):
    '''score: score score'''
    score = score.replace('-', '').lower() if '-' in score else score.lower()
    data = {k:{i:{x:y for x,y in dict(j).items()} for i,j in dict(v).items()} for k,v in dict(data).items()} # Turn taipy data dict into python dict

    selected = parse_selection(file, iabs, units, units_chosen)
    x = [px.timecode(i).split()[0][:-4] for i in range(int(file['info_video']['duration']))]
    y = {i: [
        [f'Context-unit {j}', data.get(i).get(f'Context-unit {j}')[score]]
        for j in selected[i]
        if max(data.get(i).get(f'Context-unit {j}')[score])>=score_range[0] and max(data.get(i).get(f'Context-unit {j}')[score])<=score_range[1]
        and data.get(i).get(f'Context-unit {j}')['duration-ratio']>=duration_range[0] and data.get(i).get(f'Context-unit {j}')['duration-ratio']<=duration_range[1]
    ] 
    for i in selected}

    layout = go.Layout(
        # title='IAB contextualization over time',
        showlegend=False,
        hoverlabel_namelength=-1,
        yaxis_title='Z-Score' if '-' in score else 'Score',
        xaxis_title='Time',
        xaxis={
            'tickmode': 'auto',
            'nticks': 20
        }
    )

    fig = go.Figure(layout=layout)
    for k,v in y.items():
        for i in v:
            fig.add_trace(
                go.Scatter(x=x, y=i[1],
                    mode='lines',
                    fill='tozeroy',
                    name=f'CU: {i[0].split()[1]}, IAB: {k}',
                    marker=dict(color=colors.get(k)),
                    line=dict(width=0)
                )
            )
    
    return fig

@logger
def get_segments(file, unit):
    iabs = set([i['class'] for i in file['context_units'][unit]['segments']])

    segments = []
    for e, iab in enumerate(iabs):
        segment = (e+1, iab, [])

        n = 1
        for ee, seg in enumerate(file['context_units'][unit]['segments']):
            if seg['class'] == iab:
                child = (f'{e+1}.{ee+1}', f'Segment {n}', [])

                nn = 1
                for k, v in seg.items():
                    if k == 'text':
                        child[2].append(
                            (f'{e+1}.{ee+1}.{nn}', f'{k.title()}', [(f'{e+1}.{ee+1}.{nn}.{1}', v)])
                        )
                        nn += 1

                    elif k == 'class':
                        continue

                    else:
                        child[2].append(
                            (f'{e+1}.{ee+1}.{nn}', f'{k.title()}: {v}')
                        )
                        nn += 1

                segment[2].append(child)
            n += 1
            
        segments.append(segment)
    return segments

@logger
def get_unit_info(unit, file):
    u = file['context_units'][unit]

    info = {
        'Class': u['class'],
        'Tier 2': ', '.join(u['TIER2']),
        'Score': u['score'],
        'Z-Score': u['zscore'],
        'Sentiment': u['sentiment'],
        'Duration': u['duration'],
        'Duration ratio': u['duration-ratio'],
        'Tcin': u['tcin'],
        'Tcout': u['tcout'],
        'Start time': u['start_time'],
        'End time': u['end_time']

    }
    text = u['text']
    text = text.encode('utf-8').decode('utf-8')
    segments = u['segments']
    keywords = [i[0] for i in u['keywords']['keywords']]

    return info, text, segments, keywords

@logger
def get_units(file, iabs):
    units = []
    for e, iab in enumerate(sorted(iabs)):
        unit = (float(f'{e+1}.{e+1}'), iab, [])

        n = 1
        for i in file['context_units']:
            if file['context_units'][i]['class'] == iab:
                unit[2].append(
                    (i, f'Context-unit {i}')
                )
                n += 1
    
        units.append(unit)
    return units