import json
import scipy.io
import numpy as np

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
from dash.dependencies import Input, Output, ClientsideFunction
import plotly.express as px
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objs as go
import time

#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

suppress_callback_exceptions=True
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

full_strf = scipy.io.loadmat('/Users/jsh3653/Documents/Austin/code/SpeechCortex/full_strf.mat')['strf']
spect_strf = scipy.io.loadmat('/Users/jsh3653/Documents/Austin/code/SpeechCortex/spect_strf.mat')['strf']
onset_strf = scipy.io.loadmat('/Users/jsh3653/Documents/Austin/code/SpeechCortex/onset_strf.mat')['strf']
elecs = scipy.io.loadmat('/Users/jsh3653/Documents/Austin/code/SpeechCortex/elecmatrix.mat')['elecmatrix']
vcorrs1 = scipy.io.loadmat('/Users/jsh3653/Documents/Austin/code/SpeechCortex/vcorrs.mat')['vcorrs']
vcorrs = scipy.io.loadmat('/Users/jsh3653/Documents/Austin/code/SpeechCortex/uvar.mat')['uvar']
vcorrs = np.hstack((vcorrs, vcorrs1))

imaging_dir = '/Users/jsh3653/Box/ECoG_imaging/'
trivert = scipy.io.loadmat(f'{imaging_dir}/cvs_avg35_inMNI152/Meshes/lh_pial_trivert.mat')
v = trivert['vert']
t = trivert['tri']

temporal_trivert = scipy.io.loadmat('/Users/jsh3653/Documents/Austin/code/SpeechCortex/cvs_avg_inMNI152_lh_temporal_pial.mat')
tv = temporal_trivert['vert']
tt = temporal_trivert['tri']

curv = scipy.io.loadmat('/Users/jsh3653/Documents/Austin/code/SpeechCortex/cvs_curv.mat')['curv']
anatomy = scipy.io.loadmat('/Users/jsh3653/Documents/Austin/code/SpeechCortex/elecmatrix.mat')['anatomy']
anum = np.array([a[0]-1 for a in anatomy])
elecs[anum>=5,0] = elecs[anum>=5,0]-1
anames = scipy.io.loadmat('/Users/jsh3653/Documents/Austin/code/SpeechCortex/elecmatrix.mat')['new7AreaNames']
anames2 = [a[0] for a in anames[0]]
anat_labels = [anames2[a[0]-1] for a in anatomy]
clr = scipy.io.loadmat('/Users/jsh3653/Documents/Austin/code/SpeechCortex/elecmatrix.mat')['area7Cols']
clrs = [clr[a[0]-1,:].tolist() for a in anatomy]

stim_effects = pd.read_excel(io='/Users/jsh3653/Dropbox/Heschls_STRFs/data/stim/HG_stim_summary.xlsx',
                             sheet_name='unique_for_manuscript')

def create_figure(dropdownData='RF', elec_marker='vcorrs', 
                  show_rest_of_brain=True, corr_type=12):

    if dropdownData=='RF':
        chosen_elecs = np.arange(elecs.shape[0])
    else:
        chosen_elecs = np.arange(5)

    df = pd.DataFrame(
        data={'elec_number': chosen_elecs,
              'x': elecs[chosen_elecs,0],
              'y': elecs[chosen_elecs,1],
              'z': elecs[chosen_elecs,2],
              'anatomy': [anat_labels[a] for a in chosen_elecs],
              'anatomy_num': [anum[a] for a in chosen_elecs],
              'vcorrs': vcorrs[chosen_elecs,corr_type]},
    )

    if elec_marker == 'anatomy_num':
        marker = dict(color=clrs, 
                      size=6)
    elif elec_marker == 'vcorrs':
        marker = dict(color=df['vcorrs'], 
                      colorscale='RdBu_r', 
                      cmin=-df['vcorrs'].max(), 
                      cmax=df['vcorrs'].max(),
                      size=6, colorbar=dict(title='Corr.', thickness=20))

    fig = go.Figure(
        data = [go.Mesh3d(
            x=tv[:, 0],
            y=tv[:, 1],
            z=tv[:, 2],
            i=tt[:, 0],
            j=tt[:, 1],
            k=tt[:, 2],
            colorbar=None,
            showscale=False,
            color='rgb(200,200,200)',
            name='brain',
            opacity=0.6,
            lighting=dict(ambient=0.9, diffuse=0.9),
            intensity=curv,
            colorscale=[[0, 'white'],
                        [0.5, 'gray'],
                        [1, 'black']]
            ),
        ])

    if show_rest_of_brain:
        fig.add_trace(
            go.Mesh3d(
                x=v[:, 0],
                y=v[:, 1],
                z=v[:, 2],
                i=t[:, 0],
                j=t[:, 1],
                k=t[:, 2],
                colorbar=None,
                showscale=False,
                color='rgb(200,200,200)',
                name='brain',
                text=None,
                opacity=0.2,
                lighting=dict(ambient=0.9, diffuse=0.9),
                intensity=curv,
                colorscale=[[0, 'white'],
                            [0.5, 'gray'],
                            [1, 'black']]
                )
            )

    fig.add_trace(
        go.Scatter3d(
            x=df['x'],
            y=df['y'],
            z=df['z'],
            ids=df['elec_number'],
            mode='markers',
            name='electrode',
            text=df['anatomy'],
            marker=marker,
            ),
        )

    camera = dict(
        up=dict(x=0, y=0, z=1),
        center=dict(x=0, y=0, z=0),
        eye=dict(x=-1.25, y=0.1, z=0.13),
    )

    fig.update_layout(clickmode='event+select',
                  scene=dict(
                    xaxis=dict(showticklabels=False, showgrid=False, title='L-R'),
                    yaxis=dict(showticklabels=False, showgrid=False, title='A-P'),
                    zaxis=dict(showticklabels=False, showgrid=False, title='D-V'), 
                    ),
                  scene_camera=camera,
                  height=int(500),
                  )
    fig.update_scenes(xaxis_showbackground=False,
                  yaxis_showbackground=False,
                  zaxis_showbackground=False,
                  xaxis_showaxeslabels=False,
                  yaxis_showaxeslabels=False,
                  zaxis_showaxeslabels=False,)

    return fig

# def update_electrodes(colorby='vcorrs', ids=[]):
#     fig.update_traces(selector=dict(ids=ids),
#                       marker=dict(color='blue'))
#     return fig

def create_rf(elec_num=310, corr_type=12):
    #if elec_num <= spect_strf.shape[0]:
    if elec_num is None:
        elec_num = 310
        title = 'Please select an electrode...'
        strf = np.zeros((spect_strf.shape[1], spect_strf.shape[2]))
        yticks = []
        yticklabels = []
        ticksize = 12
        ylabel = ''
        autorange = True
    else:
        title = 'Electrode %d, r=%2.2f'%(elec_num, vcorrs[elec_num,corr_type])
        if corr_type == 20:
            strf = np.fliplr(spect_strf[elec_num,:,:])
            yticks = [11, 43, 79]
            yticklabels = [0.5, 2, 8]
            ticksize = 12
            ylabel = 'Frequency (kHz)'
            autorange = True
        else:
            strf = np.fliplr(full_strf[elec_num,:,:])
            #yticks = [0,1,15,25,35]
            #yticklabels = ['on','ph','ab','rl','dr']
            yticks = np.arange(full_strf.shape[1])
            yticklabels = ['onset','sonorant','obstruent','voiced',
                           'nasal','syllabic','fricative','plosive',
                           'back','low','front','high','labial',
                           'coronal','dorsal','abs. pitch','','','',
                           '','','','','','','rel. pitch','','','',
                           '','','','','','','∆rel. pitch','','','',
                           '','','','','','','peakRate']
            ticksize = 6
            ylabel = ''
            autorange = 'reversed'

    smax = np.abs(strf.max())
    if smax==0:
        smax = 1
    fig = go.Figure(data = [
            go.Heatmap(
                    x=np.linspace(-0.6,0,60),
                    z=strf,
                    zmin=-smax,
                    zmax=smax,
                    colorscale='RdBu_r',
                    colorbar=dict(title='Beta<br>weight<br>(A.U.)',
                                  tickvals=[-smax,0,smax],
                                  ticktext=['-max','0','max']),
            )
        ]
    )

    if corr_type != 20:
        fig.add_hline(y=0.5, line_width=1, line_color='black', line_dash='dash')
        fig.add_hline(y=14.5, line_width=1, line_color='black', line_dash='dash')
        fig.add_hline(y=24.5, line_width=1, line_color='black', line_dash='dash')
        fig.add_hline(y=34.5, line_width=1, line_color='black', line_dash='dash')
        fig.add_hline(y=44.5, line_width=1, line_color='black', line_dash='dash')
    else:
        fig.add_hline(y=11, line_width=1, line_color='black', line_dash='dash')
        fig.add_hline(y=43, line_width=1, line_color='black', line_dash='dash')
        fig.add_hline(y=79, line_width=1, line_color='black', line_dash='dash')
        
    fig.update_layout(
        title={'text': title,
               'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'},
        xaxis={'title': 'Time (s)'},
        yaxis={'title': ylabel, 
               'tickmode': 'array',
               'tickvals': yticks,
               'ticktext': yticklabels, 'showgrid': False,
               'autorange': autorange,
               'tickfont_size': ticksize,
               'automargin': False,
               }
        )
    return fig

fig = create_figure()
rf_fig = create_rf()

#fig = px.scatter(df, x="x", y="y", color="fruit", custom_data=["customdata"])

#fig.update_traces(selector=dict(name='electrode'), marker=dict(color='mediumblue', size=20), row=1, col=1)
rf_markdown = dcc.Markdown('''
            ## This brain area responds to vowels. ##
            **Receptive field viewer**: Click on an electrode on the brain to see its corresponding receptive field on the right.

            **Brain Controls:**
            * Zoom in and out of the brain by scrolling
            * Rotate the brain by clicking and dragging
            ''')

app.layout = html.Div([
            html.Div([
            dcc.Markdown('''
                    ### Parallel and distributed speech encoding across human auditory cortex ###
    
                    *Citation*: [Hamilton, Oganian, Hall, and Chang. _Cell_ 2021](https://doi.org/10.1016/j.cell.2021.07.019)
    
                    This is an interactive tool to accompany our paper showing receptive fields across
                    multiple sub-fields of auditory cortex. Select from the Dropdown menu below to
                    explore receptive field findings and stimulation findings.
    
                    '''),
            ]),
            html.Div([
                html.Div([
                daq.BooleanSwitch(
                    id='show-brain',
                    on=True,
                    label="Whole brain",
                    labelPosition="top",
                ),
                ], className='three columns',
                style={'background-color': 'lightgrey', 'padding': '10px',
                       'float': 'left'}),

                html.Div([
                html.Label('Color electrodes by:'),
                dcc.RadioItems(
                    id='radio-color',
                    options=[
                        {'label': 'Anatomy', 'value': 'anatomy_num'},
                        {'label': 'Correlation', 'value': 'vcorrs'},
                    ],
                    value='vcorrs'
                )], className='three columns',
                style={'background-color': 'lightgrey', 'padding': '10px'}),
                
                html.Div([
                html.Label('Correlation type:'),
                dcc.Dropdown(
                    id='corr-type-dropdown',
                    options=[
                        {'label': 'Unique Onset', 'value': '0'},
                        {'label': 'Unique Peak rate', 'value': '1'},
                        {'label': 'Unique Features', 'value': '2'},
                        {'label': 'Unique Abs Pitch', 'value': '3'},
                        {'label': 'Unique Rel Pitch', 'value': '4'},
                        {'label': 'Unique ...', 'value': '5'},
                        {'label': 'Full phonological+pitch', 'value': '12'},
                        {'label': 'Spectrogram', 'value': '20'},
                    ],
                    # options=[
                    #     {'label': 'Onset', 'value': '0'},
                    #     {'label': 'Full', 'value': '6'},
                    #     {'label': 'Relative pitch', 'value': '12'},
                    #     {'label': 'Spectrogram', 'value': '14'},
                    # ],
                    value='12'
                )], className='three columns', 
                style={'background-color': 'lightgrey', 
                        'padding': '10px', 'display': 'inline-block'}),

                html.Div([
                html.Label('Choose results to explore:'),
                dcc.Dropdown(
                    id='rf-stim-dropdown',
                    options=[
                        {'label': 'Receptive Fields', 'value': 'RF'},
                        {'label': 'Stimulation', 'value': 'ST'},
                    ],
                    value='RF'
                )], className='three columns', 
                style={'background-color': 'lightgrey', 
                        'padding': '10px', 'display': 'inline-block',
                        'float': 'right'}),
                ],
            style={'background-color': 'lightgrey', 'display': 'inline-block', 'width': '100%'}
            ),
        html.Div([
            dcc.Loading(
                dcc.Graph(
                id='brain-fig',
                figure=fig,
                ),
                type='circle',
            ),
        ],

    style={'width': '70%', 'display': 'inline-block', 'height': '70%'}),

    html.Div([
    dcc.Graph(
        id='rf',
        figure=rf_fig,
    ),
    ],
    style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'top'}),
    #style={'width': '30%', 'display': 'block', 'vertical-align': 'top'}),

    html.Div([
            rf_markdown,
        ],
        style={'background-color': 'lightgrey', 'padding': '10px'}),
    html.Div([
            dcc.Markdown("""
                **Zoom and Relayout Data**

                Click and drag on the graph to zoom or click on the zoom
                buttons in the graph's menu bar.
                Clicking on legend items will also fire
                this event.
            """),
            html.Pre(id='relayout-data', style=styles['pre']),
        ], className='three columns'),
    html.Div(className='row', children=[
        html.Div([
            dcc.Markdown("""
                **Hover Data**

                Mouse over values in the graph.
            """),
            html.Pre(id='hover-data', style=styles['pre'])
        ], className='three columns'),

        html.Div([
            dcc.Markdown("""
                **Click Data**

                Click on points in the graph.
            """),
            html.Pre(id='click-data', style=styles['pre']),
        ], className='three columns'),

        html.Div([
            dcc.Markdown("""
                **Radio Data**

            """),
            html.Pre(id='radio-data', style=styles['pre']),
        ], className='three columns'),
    ])
    ],
    style={'max-width': '1200px'}, 
)


# app.clientside_callback(
#     ClientsideFunction("clientside", "figure"),
#     Output(component_id="graph", component_property="figure"),
#     [Input("fig-data", "data"), Input("corr-type-dropdown", "value")]
# )

@app.callback(
    Output('hover-data', 'children'),
    Input('brain-fig', 'hoverData'))
def display_hover_data(hoverData):
    return json.dumps(hoverData, indent=2)


@app.callback(
    Output('click-data', 'children'),
    Input('brain-fig', 'clickData'))
def display_click_data(clickData):
    return json.dumps(clickData, indent=2)


@app.callback(
    Output('rf', 'figure'),
    [Input('brain-fig', 'clickData'),
     Input('corr-type-dropdown', 'value')])
def update_rf(clickData, corr_val):
    try:
        elec_num = clickData['points'][0]['id']
    except:
        elec_num = None
    return create_rf(elec_num=elec_num, corr_type=int(corr_val))

@app.callback(
    Output('relayout-data', 'children'),
    Input('brain-fig', 'relayoutData'))
def display_relayout_data(relayoutData):
    return json.dumps(relayoutData, indent=2)


@app.callback(
    [Output('brain-fig', 'figure'),
     Output('radio-data','children'),
     Output('show-brain', 'label')],
    [Input('rf-stim-dropdown', 'value'), 
     Input('radio-color', 'value'),
     Input('show-brain', 'on'),
     Input('corr-type-dropdown', 'value')])
def display_click_data(rf_value, radio_value, brain_value, corr_val):
    ctx = dash.callback_context
    prop_id = ctx.triggered[0]['prop_id'].split('.')[0]
    value = ctx.triggered[0]['value']
    fig = create_figure(dropdownData=rf_value, elec_marker=radio_value, 
                        show_rest_of_brain=brain_value, corr_type=int(corr_val))

    #elif prop_id == 'rf-stim-dropdown':
    #    return create_figure(dropdownData=value)

    #if prop_id == 'rf-stim-dropdown':
    #    return create_figure(dropdownData=value)
    #elif prop_id == 'radio-color':
    #    return update_electrodes(colorby=value)
    json_data = json.dumps({
         'states': ctx.states,
         'triggered': ctx.triggered,
         'inputs': ctx.inputs,
         'value': value,
         'radiovalue': radio_value,
         'rf_value': rf_value,
         'brain_value': brain_value,
         }, indent=2)

    if brain_value:
        show_brain = "Whole brain"
    else:
        show_brain = "Temporal lobe only"
    return fig, json_data, show_brain


if __name__ == '__main__':
    app.run_server(debug=True, host='127.0.0.1')