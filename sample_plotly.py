import numpy as np

import sys
from matplotlib import cm
import scipy.io
#pip install numpy==1.16.4
import os, urllib
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

def run_the_app():
    imaging_dir = '/Users/jsh3653/Box/ECoG_imaging/'

    # Get the image data
    trivert = scipy.io.loadmat(f'{imaging_dir}/cvs_avg35_inMNI152/Meshes/lh_pial_trivert.mat')
    v = trivert['vert']
    t = trivert['tri']
    
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
            mode='markers+text',
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