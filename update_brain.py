import json

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

df = pd.DataFrame({
    "x": [1,2,1,2],
    "y": [1,2,3,4],
    "customdata": [1,2,3,4],
    "fruit": ["apple", "apple", "orange", "orange"]
})

#fig = px.scatter(df, x="x", y="y", color="fruit", custom_data=["customdata"])

imaging_dir = '/Users/jsh3653/Box/ECoG_imaging/'
#sub = ny.freesurfer_subject(f'{imaging_dir}/cvs_avg35_inMNI152')
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

fig = go.FigureWidget(make_subplots(rows=1, cols=2,
                    subplot_titles=("Brain", "Receptive field"),
                    column_widths=[0.7, 0.3],
                    specs=[[{'type': 'scene'}, {'type': 'xy'}]]))
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
#fig.show()


fig.update_layout(clickmode='event+select')

fig.update_traces(marker_size=20)

app.layout = html.Div([
    dcc.Graph(
        id='basic-interactions',
        figure=fig
    ),

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
                **Selection Data**

                Choose the lasso or rectangle tool in the graph's menu
                bar and then select points in the graph.

                Note that if `layout.clickmode = 'event+select'`, selection data also
                accumulates (or un-accumulates) selected data if you hold down the shift
                button while clicking.
            """),
            html.Pre(id='selected-data', style=styles['pre']),
        ], className='three columns'),

        html.Div([
            dcc.Markdown("""
                **Zoom and Relayout Data**

                Click and drag on the graph to zoom or click on the zoom
                buttons in the graph's menu bar.
                Clicking on legend items will also fire
                this event.
            """),
            html.Pre(id='relayout-data', style=styles['pre']),
        ], className='three columns')
    ])
])


@app.callback(
    Output('hover-data', 'children'),
    Input('basic-interactions', 'hoverData'))
def display_hover_data(hoverData):
    return json.dumps(hoverData, indent=2)


@app.callback(
    Output('click-data', 'children'),
    Input('basic-interactions', 'clickData'))
def display_click_data(clickData):
    return json.dumps(clickData, indent=2)


@app.callback(
    Output('selected-data', 'children'),
    Input('basic-interactions', 'selectedData'))
def display_selected_data(selectedData):
    return json.dumps(selectedData, indent=2)


@app.callback(
    Output('relayout-data', 'children'),
    Input('basic-interactions', 'relayoutData'))
def display_relayout_data(relayoutData):
    return json.dumps(relayoutData, indent=2)


if __name__ == '__main__':
    app.run_server(debug=True)