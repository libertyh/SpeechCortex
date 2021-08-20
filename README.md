# SpeechCortex

This is an interactive viewer to accompany the paper:

[Hamilton LS, Oganian Y, Hall J, and Chang EF (2021). Parallel and distributed speech encoding across human auditory cortex.  Cell 2021.](https://doi.org/10.1016/j.cell.2021.07.019)

There is a short [tutorial video](https://www.youtube.com/watch?v=Q0zulm4ciRI&ab_channel=LibertyHamilton) available on YouTube.

The viewer shows a left hemisphere brain reconstruction with electrodes recorded from patients with intractable epilepsy as they listened to speech. The receptive fields for different types of models can be shown by clicking on individual electrodes and choosing the features of interest from the dropdown menus. Stimulation data is also shown by changing the far right dropdown menu. 

## How to use this repo ##
You can clone this repo by running `git clone https://github.com/libertyh/SpeechCortex`.

Then, if you wish to run this locally on your browser, you may wish to create a new virtual environment using the pip requirements from `requirements.txt`. You should be able to run the app locally by typing `python app.py`, and this will launch a server on your localhost (check your Terminal for the URL).

This viewer was created by Liberty Hamilton at The University of Texas at Austin, 2021. 

The app makes heavy use of the python [Plotly](https://plotly.com/) library and [Dash framework](https://dash.plotly.com/). This app is currently hosted at http://speechbrainviewer.com, but is deployed to [Heroku](http://heroku.com).

