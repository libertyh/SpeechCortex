import scipy.io
import numpy as np

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
from dash.dependencies import Input, Output, State, ClientsideFunction
import plotly.express as px
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objs as go
import time
import os
from flask_caching import Cache
from dash.exceptions import PreventUpdate

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

suppress_callback_exceptions=True
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
cache = Cache(app.server, config={
        'CACHE_TYPE': 'redis',
        'CACHE_REDIS_URL': os.environ.get('REDIS_URL', '')
    })

timeout = 300

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

full_strf = scipy.io.loadmat('full_strf.mat')['strf']
spect_strf = scipy.io.loadmat('spect_strf.mat')['strf']
onset_strf = scipy.io.loadmat('onset_strf.mat')['strf']
elecs = scipy.io.loadmat('elecmatrix.mat')['elecmatrix']
vcorrs1 = scipy.io.loadmat('vcorrs.mat')['vcorrs']
vcorrs = scipy.io.loadmat('uvar.mat')['uvar']
vcorrs = np.hstack((vcorrs, vcorrs1))

trivert = scipy.io.loadmat('lh_pial_trivert.mat')
v = trivert['vert']
t = trivert['tri']

temporal_trivert = scipy.io.loadmat('cvs_avg_inMNI152_lh_temporal_pial.mat')
tv = temporal_trivert['vert']
tt = temporal_trivert['tri']

curv = scipy.io.loadmat('cvs_curv.mat')['curv']
anatomy = scipy.io.loadmat('elecmatrix.mat')['anatomy']
anum = np.array([a[0]-1 for a in anatomy])
elecs[anum>=5,0] = elecs[anum>=5,0]-1
anames = scipy.io.loadmat('elecmatrix.mat')['new7AreaNames']
anames2 = [a[0] for a in anames[0]]
anat_labels = [anames2[a[0]-1] for a in anatomy]
clr = scipy.io.loadmat('elecmatrix.mat')['area7Cols']
clrs = [clr[a[0]-1,:].tolist() for a in anatomy]

#stim_effects = pd.read_excel(io='/Users/jsh3653/Dropbox/Heschls_STRFs/data/stim/HG_stim_summary.xlsx',
#                             sheet_name='unique_for_manuscript')
stim_effects = pd.read_excel(io='stim_results.xlsx', sheet_name='Sheet1')
stim_df = pd.DataFrame(
            data={'elec_number': np.arange(len(stim_effects)),
              'x': stim_effects['x'],
              'y': stim_effects['y'],
              'z': stim_effects['z'],
              'anatomy': stim_effects['anatomy'],
              'effect': stim_effects['effect'],
              'passive_effect': stim_effects['passive_effect'],
              'repetition_effect': stim_effects['repetition_effect']},
        )

def create_figure(dropdownData='RF', elec_marker='vcorrs', 
                  show_rest_of_brain=True, corr_type=12):
    '''
    Create the brain figure and modify the electrode
    colors based on dropdown menus. The frontal lobe
    will be shown or not depending on the value of the
    show_rest_of_brain switch.
    '''
    if dropdownData=='RF':
        chosen_elecs = np.arange(elecs.shape[0])
        df = pd.DataFrame(
            data={'elec_number': chosen_elecs,
              'x': elecs[chosen_elecs,0],
              'y': elecs[chosen_elecs,1],
              'z': elecs[chosen_elecs,2],
              'anatomy': [anat_labels[a] for a in chosen_elecs],
              'anatomy_num': [anum[a] for a in chosen_elecs],
              'vcorrs': vcorrs[chosen_elecs,corr_type]},
        )
    else:
        df = stim_df


    if elec_marker == 'anatomy_num':
        marker = dict(color=clrs, 
                      size=6)
    elif elec_marker == 'vcorrs':
        marker = dict(color=df['vcorrs'], 
                      colorscale='RdBu_r', 
                      cmin=-df['vcorrs'].max(), 
                      cmax=df['vcorrs'].max(),
                      size=6, colorbar=dict(title='Corr.', thickness=20))
    elif elec_marker == 'stim_eff':
        marker = dict(color=df['effect'], 
                      colorscale='RdBu_r', 
                      cmin=1, 
                      cmax=3,
                      size=6, colorbar=dict(title='Effect', thickness=20))        

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
            name='temporal lobe',
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


def create_rf(elec_num=310, corr_type=12):
    '''
    This creates the receptive field heat map plot for
    the model of interest (based on `corr_type` number).
    For reference, those corr numbers are:
        Unique Onset: 0
        Unique Peak rate: 1
        Unique Features: 2 
        Unique Abs Pitch: 3
        Unique Rel Pitch: 4
        Unique ...': 5
        Full phonological+pitch: 12,
        Spectrogram: 20
    '''
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
            **Receptive field viewer**: Click on an electrode on the brain to see its corresponding receptive field on the right.

            **Brain Controls:**
            * Zoom in and out of the brain by scrolling
            * Rotate the brain by clicking and dragging

            Note that the nonlinear warping of electrodes sometimes means the electrodes will seem farther forward
            or back than expected. The anatomical name that shows on hover is taken from the original (native space)
            brain data. Electrodes have been projected to the nearest surface vertex for ease of clicking. 
            ''')

# This creates the initial app in its first instantiation. This will be
# modified by user behaviors (clicking, changing menu items, etc.)
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
            html.Div([
                dcc.Graph(
                    id='rf',
                    figure=rf_fig,
                ),
            ],
            id="rf_div",
            style={'width': '100%', 'display': 'inline-block', 'vertical-align': 'top'},
            ),
            html.Div([
                html.H4('Stimulation effects'),
                html.P('Click on an electrode to see effects of stimulation on passive \
                        listening and on speech perception. We recommend you turn off\
                        the "whole brain" switch at the top left to show the temporal lobe only.')
                html.P('Effect types: ', style={'font-weight': 'bold'}),
                html.P('1 (blue): sound hallucination + no problems perceiving speech',
                       style={'background-color': '#0c2350', 'padding': '10px', 'color': '#ffffff'}),
                html.P('2 (white): no sound hallucination + problems perceiving speech',
                       style={'background-color': '#f1f2f2', 'padding': '10px', 'color': '#000000'}),
                html.P('3 (red): Complex response',
                       style={'background-color': '#73001c', 'padding': '10px', 'color': '#ffffff'}),
                html.P('Click on an electrode to show stimulation effects.', 
                       id='stim_desc'),
                html.P('', id='repet_effect')
                ],
            id="stim_div",
            style={'width': '100%', 'display': 'none', 'vertical-align': 'middle'},
            )
        ],
        id="rf_or_stim_div",
        style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'top'}),

        html.Div([
                rf_markdown,
            ],
            style={'background-color': 'lightgrey', 'padding': '10px'}),
    
    ],
    style={'max-width': '1200px'}, 
)


# This callback will create the receptive field figure
# based on the correlation type you choose and what you
# have clicked on the brain figure
@app.callback(
     [Output('rf', 'figure'),
      Output('stim_desc', 'children'),
      Output('repet_effect', 'children')],
    [Input('brain-fig', 'clickData'),
     Input('corr-type-dropdown', 'value'),
     Input('rf-stim-dropdown', 'value')])
def update_rf(clickData, corr_val, rf_value):
    ctx = dash.callback_context
    prop_id = ctx.triggered[0]['prop_id'].split('.')[0]

    try:
        elec_num = clickData['points'][0]['id']
    except:
        elec_num = None
    
    if rf_value == 'RF':
        rf_updated = create_rf(elec_num=elec_num, corr_type=int(corr_val))
        stim_updated = 'No data'
        rep_updated = ''
    else:
        if (prop_id == 'rf-stim-dropdown') or (prop_id=='corr-type-dropdown'):
            elec_num = 0
            stim_updated = 'Click on an electrode to see stimulation results.'
            rep_updated = ''
        else: 
            passive_description = stim_df['passive_effect'][elec_num]
            repet_description = stim_df['repetition_effect'][elec_num]
            rf_updated = create_rf(elec_num=elec_num, corr_type=int(corr_val))
            stim_updated = 'Passive: ' + passive_description 
            rep_updated = 'Repetition: ' + repet_description

    return rf_updated, stim_updated, rep_updated

# This callback will change the brain figure to show
# either receptive field data or stimulation data 
# based on the dropdown values. It will also change
# the correlation type that is shown if in "RF" mode
@app.callback(
    [Output('brain-fig', 'figure'),
     Output('show-brain', 'label'),
     Output('rf_div', 'style'),
     Output('stim_div', 'style'),],
    [Input('rf-stim-dropdown', 'value'), 
     Input('radio-color', 'value'),
     Input('show-brain', 'on'),
     Input('corr-type-dropdown', 'value')])
@cache.memoize(timeout=timeout)  # in seconds, cache the data 
def display_click_data(rf_value, radio_value, brain_value, corr_val):
    ctx = dash.callback_context
    prop_id = ctx.triggered[0]['prop_id'].split('.')[0]
    value = ctx.triggered[0]['value']

    if rf_value == 'ST':
        # Override elec_marker type
        el_marker = 'stim_eff'
        stim_style = {'width': '100%', 'display': 'inline-block', 'vertical-align': 'middle'}
        rf_style = {'width': '100%', 'display': 'none', 'vertical-align': 'top'}
    else:
        el_marker = radio_value
        stim_style = {'width': '100%', 'display': 'none', 'vertical-align': 'middle'}
        rf_style = {'width': '100%', 'display': 'inline-block', 'vertical-align': 'top'}
    
    fig = create_figure(dropdownData=rf_value, elec_marker=el_marker, 
                        show_rest_of_brain=brain_value, corr_type=int(corr_val))

    if brain_value:
        show_brain = "Whole brain"
    else:
        show_brain = "Temporal lobe only"

    # if rf_value=='RF':
    #     rf_stim_update = dcc.Loading(dcc.Graph(id='rf', figure=rf_fig))
    # else:
    #     rf_stim_update = ... #markdown for stim

    return fig, show_brain, rf_style, stim_style


if __name__ == '__main__':
    app.run_server(processes=6)
    #app.run_server(debug=True, host='127.0.0.1')