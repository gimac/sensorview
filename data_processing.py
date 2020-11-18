"""

    Copyright (C) 2019 - 2020  Zhengyu Peng
    E-mail: zpeng.me@gmail.com
    Website: https://zpeng.me

    `                      `
    -:.                  -#:
    -//:.              -###:
    -////:.          -#####:
    -/:.://:.      -###++##:
    ..   `://:-  -###+. :##:
           `:/+####+.   :##:
    .::::::::/+###.     :##:
    .////-----+##:    `:###:
     `-//:.   :##:  `:###/.
       `-//:. :##:`:###/.
         `-//:+######/.
           `-/+####/.
             `+##+.
              :##:
              :##:
              :##:
              :##:
              :##:
               .+:

"""

import numpy as np
from threading import Thread
from queue import Queue

import pandas as pd

from viz.viz import get_figure_data, get_figure_layout, get_host_data


def filter_range(data_frame, name, value):
    temp_frame = data_frame[data_frame[name] >= value[0]]
    return temp_frame[
        temp_frame[name] <= value[1]
    ].reset_index(drop=True)


def filter_picker(data_frame, name, value):
    return data_frame[pd.DataFrame(
        data_frame[name].tolist()
    ).isin(value).any(1)].reset_index(drop=True)


def filter_all(
        data_frame,
        numerical_key_list,
        numerical_key_values,
        categorical_key_list,
        categorical_key_values
):
    filtered_table = data_frame
    for filter_idx, filter_name in enumerate(numerical_key_list):
        filtered_table = filter_range(
            filtered_table,
            filter_name,
            numerical_key_values[filter_idx])

    for filter_idx, filter_name in enumerate(categorical_key_list):
        filtered_table = filter_picker(
            filtered_table,
            filter_name,
            categorical_key_values[filter_idx])

    return filtered_table


class DataProcessing(Thread):
    def __init__(self, task_queue):
        Thread.__init__(self)

        self.config = dict()

        self.data = pd.DataFrame()

        self.frame_idx = []

        self.task_queue = task_queue

        self.filtering_ready = False
        self.frame_list_ready = False

        self.frame_ready_index = -1

        self.filtered_table = pd.DataFrame()

        self.fig_list = []

        self.is_locked = True

        self.graph_params = dict()
        self.graph_layout = dict()

    def load_data(self, data):
        self.is_locked = True
        self.data = data
        self.frame_idx = self.data[
            self.config['numerical']
            [self.config['slider']]['key']].unique()
        self.is_locked = False

    def is_filtering_ready(self):
        return self.filtering_ready

    def is_frame_list_ready(self):
        return self.frame_list_ready

    def get_frame_ready_index(self):
        return self.frame_ready_index

    def get_frame(self, idx):
        return self.fig_list[idx]

    def get_filtered_data(self):
        # print(self.filtered_table['Visibility'])
        return self.filtered_table
    
    def get_data(self):
        return self.data

    def run(self):
        skip_filter = False
        while True:
            work = self.task_queue.get()

            if work['trigger'] == 'filter':
                print('start filtering')
                self.filtering_ready = False

                self.config = work['config']

                new_data = work.get('data', None)
                if new_data is not None:
                    self.load_data(new_data)

                cat_values = work['cat_values']
                num_values = work['num_values']
                cat_keys = work['cat_keys']
                num_keys = work['num_keys']

                skip_filter = False

                self.frame_list_ready = False
                self.frame_ready_index = -1

                self.graph_params = work.get('graph_params', self.graph_params)
                self.graph_layout = work.get('graph_layout', self.graph_layout)

                self.filtered_table = self.data

                for filter_idx, filter_name in enumerate(num_keys):
                    self.filtered_table = filter_range(
                        self.filtered_table,
                        filter_name,
                        num_values[filter_idx])

                    if not self.task_queue.empty():
                        self.filtering_ready = False
                        skip_filter = True
                        self.frame_ready_index = -1
                        break

                for filter_idx, filter_name in enumerate(cat_keys):
                    self.filtered_table = filter_picker(
                        self.filtered_table,
                        filter_name,
                        cat_values[filter_idx])

                    if not self.task_queue.empty():
                        self.filtering_ready = False
                        skip_filter = True
                        self.frame_ready_index = -1
                        break
                # print(self.filtered_table)
                if not skip_filter:
                    # print('filtering done')
                    self.filtering_ready = True

                    self.fig_list = []
                    for idx, frame in enumerate(self.frame_idx):
                        filtered_list = self.filtered_table[
                            self.filtered_table['Frame'] == frame
                        ]
                        filtered_list = filtered_list.reset_index()
                        # print(self.filtered_table)

                        self.fig_list.append(dict(
                            data=[
                                get_figure_data(
                                    det_list=filtered_list,
                                    x_key=self.graph_params['x_det_key'],
                                    y_key=self.graph_params['y_det_key'],
                                    z_key=self.graph_params['z_det_key'],
                                    color_key=self.graph_layout['color_key'],
                                    color_label=self.graph_layout['color_label'],
                                    name='Index: ' +
                                    str(idx) + ' (' +
                                    self.config['numerical'][
                                        self.config['slider']
                                    ]['description']+')',
                                    hover_dict={
                                        **self.config['numerical'],
                                        **self.config['categorical']
                                    },
                                    c_range=self.graph_layout['c_range']
                                ),
                                get_host_data(
                                    det_list=filtered_list,
                                    x_key=self.graph_params['x_host_key'],
                                    y_key=self.graph_params['y_host_key'],
                                )
                            ],
                            layout=get_figure_layout(
                                x_range=self.graph_layout['x_range'],
                                y_range=self.graph_layout['y_range'],
                                z_range=self.graph_layout['z_range'])
                        )
                        )

                        self.frame_ready_index = idx
                        # print(idx)

                        if not self.task_queue.empty():

                            skip_filter = True
                            self.filtering_ready = False
                            self.frame_ready_index = -1
                            break

                    if not skip_filter:
                        self.frame_list_ready = True

                    self.task_queue.task_done()
