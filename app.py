from threading import Thread, Event
from time import sleep

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.exceptions import PreventUpdate
import numpy as np
import pandas as pd
import os
import plotly.graph_objs as go
import plotly.io as pio

app = dash.Dash(__name__,
                meta_tags=[{
                    "name": "viewport",
                    "content": "width=device-width,initial-scale=1"
                }])
app.scripts.config.serve_locally = True
app.css.config.serve_locally = True
app.title = 'Radar Viz'

test_cases = []
for (dirpath, dirnames, filenames) in os.walk('./data'):
    test_cases.extend(dirnames)
    break

data_files = []
for r, d, f in os.walk('./data/'+test_cases[0]):
    for file in f:
        if '.pkl' in file:
            data_files.append(file)

det_list = pd.DataFrame()
det_frames = []
fig_list = []
fig_list_ready = False
filter_trigger = 0
callback_indicator = 0
filter_list = ['LookName', 'AFType', 'AzConf',
                           'ElConf', 'Longitude', 'Latitude',
                           'Height', 'Speed', 'Range', 'SNR',
                           'Azimuth', 'Elevation']
filter_values = [[], [], [], [], [0, 0], [0, 0],
                 [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]

app.layout = html.Div([
    html.Div([
        dcc.Graph(
            id='det_grid',
            config={
                "displaylogo": False,
                # 'modeBarButtonsToRemove': ['pan2d', 'lasso2d']
            },
            figure={
                'data': [{'mode': 'markers', 'type': 'scatter3d', 'x': [], 'y': [], 'z': []}
                         ],
                'layout': {'template': pio.templates['plotly_dark'],
                           'height': 650,
                           'scene': {'xaxis': {'range': [-100, 100],
                                               'title': 'Lateral (m)',
                                               'autorange': False},
                                     'yaxis': {'range': [-100, 100],
                                               'title': 'Longitudinal (m)',
                                               'autorange': False},
                                     'zaxis': {'range': [-20, 20], 'title': 'Height (m)', 'autorange': False},
                                     'aspectmode': 'manual',
                                     'aspectratio':{'x': 1, 'y': 1, 'z': 1}
                                     },
                           'margin': {'l': 0, 'r': 0, 'b': 0, 't': 20},
                           'legend': {'x': 0, 'y': 0},
                           'uirevision': 'no_change'
                           }
            },
        ),
        html.Div([
            # html.Label('Frame'),
            dcc.Slider(
                id='frame_slider',
                step=1,
                value=0,
                updatemode='drag',
            )], style={'box-sizing': 'border-box',
                       'width': '100%',
                       'display': 'inline-block',
                       'padding': '2rem 0rem'})
    ], style={'box-sizing': 'border-box',
              'width': '66%',
              'display': 'inline-block',
              'padding': '4rem 4rem',
              'max-height': '100vh',
              'overflow': 'auto', }),

    html.Div([
        html.H4("Radar Viz"),
        html.P("Radar detections visualization"),
        html.Br(),
        html.Label('Test Cases'),
        dcc.Dropdown(
            id='test_case_picker',
            options=[{'label': i, 'value': i} for i in test_cases],
            value=test_cases[0]
        ),
        html.Label('Data Files'),
        dcc.Dropdown(
            id='data_file_picker',
            options=[{'label': i, 'value': i} for i in data_files],
            value=data_files[0]
        ),
        html.Br(),
        html.Label('Color assignment'),
        dcc.Dropdown(
            options=[
                {'label': 'Speed', 'value': 'Speed'},
                {'label': 'RCS', 'value': 'RCS'},
                {'label': 'SNR', 'value': 'SNR'}
            ],
            value='Speed'
        ),
        html.Br(),
        html.Label('Look Type'),
        dcc.Dropdown(
            id='look_type_picker',
            multi=True
        ),
        html.Label('AF Type'),
        dcc.Dropdown(
            id='af_type_picker',
            multi=True
        ),
        html.Label('AF Azimuth Confidence Level'),
        dcc.Dropdown(
            id='az_conf_picker',
            multi=True
        ),
        html.Label('AF Elevation Confidence Level'),
        dcc.Dropdown(
            id='el_conf_picker',
            multi=True
        ),
        html.Label(id='longitude_value',
                   children='Longitude Range'),
        dcc.RangeSlider(
            id='longitude_filter',
            count=1,
            min=0,
            max=10,
            step=0.5,
            value=[0, 10],
            tooltip={'always_visible': False}
        ),
        html.Label(id='latitude_value',
                   children='Latitude Range'),
        dcc.RangeSlider(
            id='latitude_filter',
            count=1,
            min=0,
            max=10,
            step=0.5,
            value=[0, 10],
            tooltip={'always_visible': False}
        ),
        html.Label(id='height_value',
                   children='Height Range'),
        dcc.RangeSlider(
            id='height_filter',
            count=1,
            min=0,
            max=10,
            step=0.5,
            value=[0, 10],
            tooltip={'always_visible': False}
        ),
        html.Label('Speed filter'),
        dcc.RangeSlider(
            id='speed_filter',
            count=1,
            min=0,
            max=10,
            step=0.5,
            value=[0, 10],
            tooltip={'always_visible': False}
        ),
        html.Label('Range filter'),
        dcc.RangeSlider(
            id='range_filter',
            count=1,
            min=0,
            max=10,
            step=0.5,
            value=[0, 10],
            tooltip={'always_visible': False}
        ),
        html.Label('SNR filter'),
        dcc.RangeSlider(
            id='snr_filter',
            count=1,
            min=0,
            max=10,
            step=0.5,
            value=[0, 10],
            tooltip={'always_visible': False}
        ),
        html.Label('Azimuth filter'),
        dcc.RangeSlider(
            id='az_filter',
            count=1,
            min=0,
            max=10,
            step=0.5,
            value=[0, 10],
            tooltip={'always_visible': False}
        ),
        html.Label('Elevation filter'),
        dcc.RangeSlider(
            id='el_filter',
            count=1,
            min=0,
            max=10,
            step=0.5,
            value=[0, 10],
            tooltip={'always_visible': False}
        ),
        # Hidden div inside the app that stores the intermediate value
        html.Div(id='trigger', style={'display': 'none'}),
        html.Div(id='dummy', style={'display': 'none'}),
    ], style={'box-sizing': 'border-box',
              'width': '34%',
              'display': 'inline-block',
              'vertical-align': 'top',
              'padding': '2rem 4rem',
              'margin': '0 0',
              'background-color': '#E0E0E0',
              #   'min-height': '100vh',
              'max-height': '100vh',
              'overflow': 'auto',
              })
], style={'border-width': '0',
          'box-sizing': 'border-box',
          'display': 'flex',
          'padding': '0rem 0rem',
          'background-color': '#111111',
          'min-height': '100vh',
          'max-height': '100vh',
          #   'overflow-y': 'scroll',
          #   'overflow': 'scroll'
          })


def filter_data(data_frame, name, value):
    if name == 'LookName' or name == 'AFType' or name == 'AzConf' or name == 'ElConf':
        return data_frame[pd.DataFrame(data_frame[name].tolist()).isin(value).any(1)].reset_index(drop=True)
    else:
        temp_frame = data_frame[data_frame[name] >= value[0]]
        return temp_frame[temp_frame[name] <= value[1]].reset_index(drop=True)


@app.callback(
    dash.dependencies.Output('det_grid', 'figure'),
    [
        dash.dependencies.Input('frame_slider', 'value'),
        dash.dependencies.Input('look_type_picker', 'value'),
        dash.dependencies.Input('af_type_picker', 'value'),
        dash.dependencies.Input('az_conf_picker', 'value'),
        dash.dependencies.Input('el_conf_picker', 'value'),
        dash.dependencies.Input('longitude_filter', 'value'),
        dash.dependencies.Input('latitude_filter', 'value'),
        dash.dependencies.Input('height_filter', 'value'),
        dash.dependencies.Input('speed_filter', 'value'),
        dash.dependencies.Input('range_filter', 'value'),
        dash.dependencies.Input('snr_filter', 'value'),
        dash.dependencies.Input('az_filter', 'value'),
        dash.dependencies.Input('el_filter', 'value'),
    ],
    [
        dash.dependencies.State('det_grid', 'figure'),
        dash.dependencies.State('trigger', 'children')
    ])
def update_data(frame_slider_value, look_type, af_type, az_conf, el_conf, longitude, latitude, height, speed, rng, snr, az, el, fig, trigger_state):
    global fig_list
    global det_frames
    global fig_list_ready
    global filter_trigger
    global filter_list
    global filter_values

    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if det_list.size == 0:
        min_x = -10
        max_x = 10
        min_y = -10
        max_y = 10
    else:
        min_x = np.min([np.min(det_list['Latitude']),
                        np.min(det_list['VehLat'])])
        max_x = np.max([np.max(det_list['Latitude']),
                        np.max(det_list['VehLat'])])

        min_y = np.min([np.min(det_list['Longitude']),
                        np.min(det_list['VehLong'])])
        max_y = np.max([np.max(det_list['Longitude']),
                        np.max(det_list['VehLong'])])

    if trigger_id == 'frame_slider':
        if len(fig_list) <= frame_slider_value:
            return fig
        elif fig_list_ready:
            print('figure list ready')
            return fig_list[frame_slider_value]
        else:
            print('figure list not ready')

            filterd_frame = det_frames[frame_slider_value]

            for filter_idx, filter_name in enumerate(filter_list):
                filterd_frame = filter_data(
                    filterd_frame, filter_name, filter_values[filter_idx])

            return update_det_graph(filterd_frame, min_x, max_x, min_y, max_y)
    else:
        if look_type is not None and af_type is not None and az_conf is not None and el_conf is not None:
            filter_list = ['LookName', 'AFType', 'AzConf',
                           'ElConf', 'Longitude', 'Latitude',
                           'Height', 'Speed', 'Range', 'SNR',
                           'Azimuth', 'Elevation']
            filter_values = [look_type, af_type,
                             az_conf, el_conf, longitude, latitude,
                             height, speed, rng, snr, az, el]
            filter_trigger = True
            fig_list_ready = False
            filterd_frame = det_frames[frame_slider_value]

            for filter_idx, filter_name in enumerate(filter_list):
                filterd_frame = filter_data(
                    filterd_frame, filter_name, filter_values[filter_idx])
            # print(filter_trigger)
            return update_det_graph(filterd_frame, min_x, max_x, min_y, max_y)
        else:
            return fig


@app.callback(
    [
        dash.dependencies.Output('data_file_picker', 'value'),
        dash.dependencies.Output('data_file_picker', 'options'),
    ],
    [
        dash.dependencies.Input('test_case_picker', 'value')
    ])
def update_data(test_case):
    data_files = []
    for r, d, f in os.walk('./data/'+test_case):
        for file in f:
            if '.pkl' in file:
                data_files.append(file)

    return data_files[0], [{'label': i, 'value': i} for i in data_files]


@app.callback(
    [
        dash.dependencies.Output('frame_slider', 'min'),
        dash.dependencies.Output('frame_slider', 'max'),
        dash.dependencies.Output('frame_slider', 'value'),
        dash.dependencies.Output('look_type_picker', 'options'),
        dash.dependencies.Output('look_type_picker', 'value'),
        dash.dependencies.Output('af_type_picker', 'options'),
        dash.dependencies.Output('af_type_picker', 'value'),
        dash.dependencies.Output('az_conf_picker', 'options'),
        dash.dependencies.Output('az_conf_picker', 'value'),
        dash.dependencies.Output('el_conf_picker', 'options'),
        dash.dependencies.Output('el_conf_picker', 'value'),
        dash.dependencies.Output('longitude_filter', 'min'),
        dash.dependencies.Output('longitude_filter', 'max'),
        dash.dependencies.Output('longitude_filter', 'value'),
        dash.dependencies.Output('latitude_filter', 'min'),
        dash.dependencies.Output('latitude_filter', 'max'),
        dash.dependencies.Output('latitude_filter', 'value'),
        dash.dependencies.Output('height_filter', 'min'),
        dash.dependencies.Output('height_filter', 'max'),
        dash.dependencies.Output('height_filter', 'value'),
        dash.dependencies.Output('speed_filter', 'min'),
        dash.dependencies.Output('speed_filter', 'max'),
        dash.dependencies.Output('speed_filter', 'value'),
        dash.dependencies.Output('range_filter', 'min'),
        dash.dependencies.Output('range_filter', 'max'),
        dash.dependencies.Output('range_filter', 'value'),
        dash.dependencies.Output('snr_filter', 'min'),
        dash.dependencies.Output('snr_filter', 'max'),
        dash.dependencies.Output('snr_filter', 'value'),
        dash.dependencies.Output('az_filter', 'min'),
        dash.dependencies.Output('az_filter', 'max'),
        dash.dependencies.Output('az_filter', 'value'),
        dash.dependencies.Output('el_filter', 'min'),
        dash.dependencies.Output('el_filter', 'max'),
        dash.dependencies.Output('el_filter', 'value'),
    ],
    [
        dash.dependencies.Input('data_file_picker', 'value')
    ],
    [
        dash.dependencies.State('test_case_picker', 'value')
    ])
def update_data(data_file_name, test_case):
    global det_list
    global det_frames
    global fig_list
    global callback_indicator
    callback_indicator = callback_indicator+1
    local_callback_indicator = callback_indicator
    look_options = []
    look_selection = []
    af_type_options = []
    af_type_selection = []
    az_conf_options = []
    az_conf_selection = []
    el_conf_options = []
    el_conf_selection = []
    if data_file_name is not None:
        det_list = pd.read_pickle('./data/'+test_case+'/'+data_file_name)
        min_x = np.min([np.min(det_list['Latitude']),
                        np.min(det_list['VehLat'])])
        max_x = np.max([np.max(det_list['Latitude']),
                        np.max(det_list['VehLat'])])

        min_y = np.min([np.min(det_list['Longitude']),
                        np.min(det_list['VehLong'])])
        max_y = np.max([np.max(det_list['Longitude']),
                        np.max(det_list['VehLong'])])
        det_frames = []
        frame_list = det_list['Frame'].unique()
        for frame_idx in frame_list:
            filtered_list = det_list[det_list['Frame'] == frame_idx]
            filtered_list = filtered_list.reset_index()
            det_frames.append(filtered_list)
            fig_list.append(update_det_graph(
                filtered_list, min_x, max_x, min_y, max_y))
            if local_callback_indicator != callback_indicator:
                print('abort calculation')
                raise PreventUpdate

        look_types = det_list['LookName'].unique()
        for look_name in look_types:
            look_options.append({'label': look_name, 'value': look_name})
            look_selection.append(look_name)
            if local_callback_indicator != callback_indicator:
                print('abort calculation')
                raise PreventUpdate

        af_types = det_list['AFType'].unique()
        for af_type in af_types:
            af_type_options.append({'label': af_type, 'value': af_type})
            af_type_selection.append(af_type)
            if local_callback_indicator != callback_indicator:
                print('abort calculation')
                raise PreventUpdate

        az_conf = det_list['AzConf'].unique()
        for az_c in az_conf:
            az_conf_options.append({'label': az_c, 'value': az_c})
            az_conf_selection.append(az_c)
            if local_callback_indicator != callback_indicator:
                print('abort calculation')
                raise PreventUpdate

        el_conf = det_list['ElConf'].unique()
        for el_c in el_conf:
            el_conf_options.append({'label': el_c, 'value': el_c})
            el_conf_selection.append(el_c)
            if local_callback_indicator != callback_indicator:
                print('abort calculation')
                raise PreventUpdate

        longitude_min = round(np.min(det_list['Longitude']), 1)
        longitude_max = round(np.max(det_list['Longitude']), 1)
        latitude_min = round(np.min(det_list['Latitude']), 1)
        latitude_max = round(np.max(det_list['Latitude']), 1)
        height_min = round(np.min(det_list['Height']), 1)
        height_max = round(np.max(det_list['Height']), 1)
        speed_min = round(np.min(det_list['Speed']), 1)
        speed_max = round(np.max(det_list['Speed']), 1)
        range_min = round(np.min(det_list['Range']), 1)
        range_max = round(np.max(det_list['Range']), 1)
        snr_min = round(np.min(det_list['SNR']), 1)
        snr_max = round(np.max(det_list['SNR']), 1)
        az_min = round(np.min(det_list['Azimuth']), 1)
        az_max = round(np.max(det_list['Azimuth']), 1)
        el_min = round(np.min(det_list['Elevation']), 1)
        el_max = round(np.max(det_list['Elevation']), 1)
        callback_indicator = 0
        print('complete calculation')
        return [0,
                len(det_frames)-1,
                0,
                look_options,
                look_selection,
                af_type_options,
                af_type_selection,
                az_conf_options,
                az_conf_selection,
                el_conf_options,
                el_conf_selection,
                longitude_min,
                longitude_max,
                [longitude_min, longitude_max],
                latitude_min,
                latitude_max,
                [latitude_min, latitude_max],
                height_min,
                height_max,
                [height_min, height_max],
                speed_min,
                speed_max,
                [speed_min, speed_max],
                range_min,
                range_max,
                [range_min, range_max],
                snr_min,
                snr_max,
                [snr_min, snr_max],
                az_min,
                az_max,
                [az_min, az_max],
                el_min,
                el_max,
                [el_min, el_max]]


def update_det_graph(det_frame, min_x, max_x, min_y, max_y):
    fx = det_frame['Latitude']
    fy = det_frame['Longitude']
    fz = det_frame['Height']
    famp = det_frame['Amplitude']
    frcs = det_frame['RCS']
    fframe = det_frame['Frame']
    fsnr = 20*np.log10(det_frame['SNR'])
    faz = det_frame['Azimuth']
    fel = det_frame['Elevation']
    frng = det_frame['Range']
    fspeed = det_frame['Speed']
    fl_type = det_frame['LookName']

    vx = det_frame['VehLat']
    vy = det_frame['VehLong']

    hover = []
    for idx, var in enumerate(fframe.to_list()):
        hover.append('Frame: '+str(int(var))+'<br>' +
                     'Amp: '+'{:.2f}'.format(famp[idx])+'dB<br>' +
                     'RCS: ' + '{:.2f}'.format(frcs[idx])+'dB<br>' +
                     'SNR: ' + '{:.2f}'.format(fsnr[idx])+'dB<br>' +
                     'Az: ' + '{:.2f}'.format(faz[idx])+'deg<br>' +
                     'El: ' + '{:.2f}'.format(fel[idx])+'deg<br>' +
                     'Range: ' + '{:.2f}'.format(frng[idx])+'m<br>' +
                     'Speed: ' + '{:.2f}'.format(fspeed[idx])+'m/s<br>' +
                     'LookType: ' + fl_type[idx] + '<br>')

    det_map = go.Scatter3d(
        x=fx,
        y=fy,
        z=fz,
        text=hover,
        hovertemplate='%{text}'+'Lateral: %{x:.2f} m<br>' +
        'Longitudinal: %{y:.2f} m<br>'+'Height: %{z:.2f} m<br>',
        mode='markers',
        # name='Frame: '+str(int(frame_idx)),
        marker=dict(
            size=3,
            color=fspeed,                # set color to an array/list of desired values
            colorscale='Rainbow',   # choose a colorscale
            opacity=0.8,
            colorbar=dict(
                title='Speed',
            ),
            cmin=-35,
            cmax=35,
        ),
    )

    if len(vx) == 0:
        vx_temp = []
        vy_temp = []
        vz_temp = []
    else:
        vx_temp = [vx[0]]
        vy_temp = [vy[0]]
        vz_temp = [0]
    vel_map = go.Scatter3d(
        x=vx_temp,
        y=vy_temp,
        z=vz_temp,
        hovertemplate='Lateral: %{x:.2f} m<br>' +
        'Longitudinal: %{y:.2f} m<br>',
        mode='markers',
        name='Vehicle',
        marker=dict(color='rgb(255, 255, 255)', size=6, opacity=0.8,
                    symbol='circle')
    )

    plot_layout = dict(
        # title=file_name[:-4],
        template="plotly_dark",
        height=650,
        scene=dict(xaxis=dict(range=[min_x, max_x], title='Lateral (m)', autorange=False),
                   yaxis=dict(range=[min_y, max_y],
                              title='Longitudinal (m)', autorange=False),
                   zaxis=dict(range=[-20, 20],
                              title='Height (m)', autorange=False),
                   #    camera=camera,
                   aspectmode='manual',
                   aspectratio=dict(x=(max_x-min_x)/40,
                                    y=(max_y-min_y)/40, z=1),
                   ),
        margin=dict(l=0, r=0, b=0, t=20),
        legend=dict(x=0, y=0),
        uirevision='no_change',
    )
    return go.Figure(data=[det_map, vel_map], layout=plot_layout)


# def update_figure_list_threaded(figure_list, figure_ready, new_filter, filter_dict):
class Plotting(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        global det_list
        global fig_list
        global fig_list_ready
        global filter_trigger
        global filter_list
        global filter_values

        print('start thread')
        while True:
            if filter_trigger:
                is_skipped = False
                print("recalculating figures")
                filter_trigger = False
                min_x = np.min([np.min(det_list['Latitude']),
                                np.min(det_list['VehLat'])])
                max_x = np.max([np.max(det_list['Latitude']),
                                np.max(det_list['VehLat'])])

                min_y = np.min([np.min(det_list['Longitude']),
                                np.min(det_list['VehLong'])])
                max_y = np.max([np.max(det_list['Longitude']),
                                np.max(det_list['VehLong'])])

                # filter_list = ['LookName', 'AFType', 'AzConf',
                #                'ElConf', 'Longitude', 'Latitude',
                #                'Height', 'Speed', 'Range', 'SNR',
                #                'Azimuth', 'Elevation']
                # filter_values = [look_type, af_type,
                #                  az_conf, el_conf, longitude, latitude,
                #                  height, speed, rng, snr, az, el]
                filterd_det_list = det_list
                for filter_idx, filter_name in enumerate(filter_list):
                    filterd_det_list = filter_data(
                        filterd_det_list, filter_name, filter_values[filter_idx])

                frame_list = det_list['Frame'].unique()
                for idx, frame_idx in enumerate(frame_list):
                    filtered_list = filterd_det_list[filterd_det_list['Frame'] == frame_idx]
                    filtered_list = filtered_list.reset_index()
                    # det_frames.append(filtered_list)
                    fig_list[idx] = update_det_graph(
                        filtered_list, min_x, max_x, min_y, max_y)
                    if filter_trigger:
                        is_skipped = True
                        print("skip recalculating figures")
                        break

                if not is_skipped:
                    fig_list_ready = True
                    print("done recalculating figures")
            if not filter_trigger:
                sleep(1)


if __name__ == '__main__':
    plotting = Plotting()
    plotting.start()
    # t.join()
    app.run_server(debug=True)
