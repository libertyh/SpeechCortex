import dash
import plotly.express as px
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import scipy.io
import numpy as np

import plotly.graph_objs as go
import pandas as pd
import json
import plotly.express as px
from plotly.subplots import make_subplots

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.css.append_css({
    "external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"
})


def create_figure():
    imaging_dir = '/Users/jsh3653/Box/ECoG_imaging/'
    trivert = scipy.io.loadmat(f'{imaging_dir}/cvs_avg35_inMNI152/Meshes/lh_pial_trivert.mat')
    v = trivert['vert']
    t = trivert['tri']
    
    # # When you run this cell, the figure output may appear blank, but 
    # # click inside and try to rotate it and it should show up
    # # Blue represents more reponse during production, red more during perception
    # ipv.figure(figsize=(10, 10))
    # # ipf=ny.cortex_plot
    # ipf = ny.cortex_plot([sub.rh.pial_surface, sub.lh.pial_surface], 
    #                      alpha=1, underlay='curvature', mesh_alpha=0.1)
    
    elecs = np.array([[-64, 22, 12],
                      [-45, 22, 30],
                      [-46, 23, 32]])

    curv = scipy.io.loadmat('/Users/jsh3653/Documents/Austin/code/SpeechCortex/cvs_curv.mat')['curv']
    elecs = scipy.io.loadmat('/Users/jsh3653/Documents/Austin/code/SpeechCortex/elecmatrix.mat')['elecmatrix']
    anatomy = scipy.io.loadmat('/Users/jsh3653/Documents/Austin/code/SpeechCortex/elecmatrix.mat')['anatomy']
    anum = np.array([a[0]-1 for a in anatomy])
    anames = scipy.io.loadmat('/Users/jsh3653/Documents/Austin/code/SpeechCortex/elecmatrix.mat')['new7AreaNames']
    anames2 = [a[0] for a in anames[0]]
    anat_labels = [anames2[a[0]-1] for a in anatomy]
    clr = scipy.io.loadmat('/Users/jsh3653/Documents/Austin/code/SpeechCortex/elecmatrix.mat')['area7Cols']
    clrs = [clr[a[0]-1,:].tolist() for a in anatomy]

    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=("Brain", "Receptive field"),
                        column_widths=[0.7, 0.3],
                        specs=[[{'type': 'scene'}, {'type': 'xy'}]])
    fig.add_trace(
        go.Mesh3d(
            x=v[:, 0],
            y=v[:, 1],
            z=v[:, 2],
            colorbar_title='z',
            i=t[:, 0],
            j=t[:, 1],
            k=t[:, 2],
            color='rgb(200,200,200)',
            name='brain',
            opacity=1.0,
            lighting=dict(ambient=0.9, diffuse=0.9),
            intensity=curv,
            colorscale=[[0, 'white'],
                        [0.5, 'gray'],
                        [1, 'black']]
            ),
        row=1,
        col=1
        )
    fig.add_trace(
        go.Scatter3d(
            x=elecs[:, 0],
            y=elecs[:, 1],
            z=elecs[:, 2],
            mode='markers',
            name='electrode',
            text=anat_labels,
            marker=dict(color=clrs)
            ),
        row=1,
        col=1,
        )
    fig.add_trace(
        go.Heatmap(z=np.random.randn(100,100)))
    #scatter = fig.data[1]
    #scatter.on_click(show_strf(fig=fig))
    return fig


f= create_figure()

app.layout = html.Div([html.Button('Delete', id='delete'),
                    html.Button('Clear Selection', id='clear'),
                    dcc.Graph(id = '3d_scat', figure=f),
                    html.Div('selected:'),
                    html.Div(id='selected_points'), #, style={'display': 'none'})),
                    html.Div('deleted:'),
                    html.Div(id='deleted_points') #, style={'display': 'none'}))
])

@app.callback(Output('deleted_points', 'children'),
            [Input('delete', 'n_clicks')],
            [State('selected_points', 'children'),
            State('deleted_points', 'children')])
def delete_points(n_clicks, selected_points, delete_points):
    print('n_clicks:',n_clicks)
    if selected_points:
        selected_points = json.loads(selected_points)
    else:
        selected_points = []

    if delete_points:
        deleted_points = json.loads(delete_points)
    else:
        deleted_points = []
    ns = [p['pointNumber'] for p in selected_points]
    new_indices = [df.index[n] for n in ns if df.index[n] not in deleted_points]
    print('new',new_indices)
    deleted_points.extend(new_indices)
    return json.dumps(deleted_points)



@app.callback(Output('selected_points', 'children'),
            [Input('3d_scat', 'clickData'),
                Input('deleted_points', 'children'),
                Input('clear', 'n_clicks')],
            [State('selected_points', 'children')])
def select_point(clickData, deleted_points, clear_clicked, selected_points):
    ctx = dash.callback_context
    ids = [c['prop_id'] for c in ctx.triggered]

    if selected_points:
        results = json.loads(selected_points)
    else:
        results = []


    if '3d_scat.clickData' in ids:
        if clickData:
            for p in clickData['points']:
                if p not in results:
                    results.append(p)
    if 'deleted_points.children' in ids or  'clear.n_clicks' in ids:
        results = []
    results = json.dumps(results)
    return results

@app.callback(Output('3d_scat', 'figure'),
            [Input('selected_points', 'children'),
            Input('deleted_points', 'children')],
            [State('deleted_points', 'children')])
def chart_3d( selected_points, deleted_points_input, deleted_points_state):
    global f
    deleted_points = json.loads(deleted_points_state) if deleted_points_state else []
    f = create_figure(deleted_points)

    selected_points = json.loads(selected_points) if selected_points else []
    if selected_points:
        f.add_trace(
            go.Scatter3d(
                mode='markers',
                x=[p['x'] for p in selected_points],
                y=[p['y'] for p in selected_points],
                z=[p['z'] for p in selected_points],
                marker=dict(
                    color='red',
                    size=5,
                    line=dict(
                        color='red',
                        width=2
                    )
                ),
                showlegend=False
            )
        )

    return f

if __name__ == '__main__':
    app.run_server(debug=True, host='127.0.0.1')