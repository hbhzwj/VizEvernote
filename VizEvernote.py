#!/usr/bin/env python
from __future__ import print_function, division
import time
import itertools
import json
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from dateutil import rrule


def bar(left, height, names, color, width, tick_num, rotation):
    """  bar plot

    Parameters
    ---------------
    left : left coordinates
    height : heights of the bar
    names : names for each bar
    color : color
    width : width of bar
    tick_num : number of xticks. xticks are evenly distributed.
    rotation : rotation of the xtick_labels

    Returns
    --------------
    None
    """
    N = len(left)
    dur = left[-1] - left[0]
    plt.bar(left, height, color='r', width=width)
    if tick_num is not None:
        ticks = [names[pos] for pos in
                 range(0, N, N // tick_num)]
        tick_pos = np.arange(left[0], left[-1], int(dur / tick_num))
        plt.xticks(tick_pos + width / 2., ticks, rotation=rotation)
    else:
        plt.xticks(np.array(left) + width / 2., names, rotation=rotation)


def get_time_diff(start_date, end_date, resolution):
    """  get time difference of *start_date* and *end_date*

    Parameters
    ---------------
    start_date, end_date : datetime struct
    resolution : {'week', 'month', 'year'}
        unit for the return values

    Returns
    --------------
    count : int
        integers values with unit specified by `resolution`
    """
    reso_type = getattr(rrule, resolution.upper() + 'LY')
    months = rrule.rrule(reso_type, dtstart=start_date, until=end_date)
    return months.count()


def group_count(items, group_key):
    """  count the frequence in each group

    Parameters
    ---------------
    items : list
        should be sorted list
    group_key : function
        those iterms t with same *group_key(t)* value belongs to the same
        group

    Returns
    --------------
    """
    groups = itertools.groupby(items, group_key)
    return dict((k, len(list(group))) for k, group in groups)


class VizEvernote(object):
    """  Visualize Evernote Data

    Parameters
    ---------------
    Returns
    --------------
    """

    key_map = {
        'month': '%Y-%m',
        'year': '%Y',
        'week': '%Y-%W',
    }

    dur_map = {
        'month': 30 * 24 * 3600,
        'week': 7 * 24 * 3600,
        'year': 365 * 24 * 3600,
    }

    def __init__(self, notes=None):
        self.notes = notes
        self.stat = dict()

    @staticmethod
    def parse_time(string):
        return time.strptime(string, "%Y%m%dT%H%M%SZ")

    def count(self, t_type, resolution):
        """ count the histogram of time according to resolution

        Parameters
        ---------------
        t_type : {'created', 'updated'}
            type of time
        resolution : {'month', 'week', 'year'}

        Returns
        --------------
        state : dict
        """
        stat_key = t_type + '-' + resolution
        tm = [self.parse_time(note[t_type])
              for note in self.notes
              if note.get(t_type)]
        sorted_tm = sorted(tm, key=lambda x: time.mktime(x))
        group_key = lambda x: time.strftime(self.key_map[resolution], x)
        self.stat[stat_key] = group_count(sorted_tm, group_key)
        return self.stat[stat_key]

    def dump(self, fp):
        json.dump(self.stat, fp)

    def load(self, fp):
        self.stat = json.load(fp)

    @staticmethod
    def sort_pair(d):
        return zip(*sorted(d.items()))

    def strptime(self, t_str, resolution):
        """  convert **t_str** to datetime.time_struct

        Parameters
        ---------------
        t_str : str
            string of time
        resolution : {'week', 'month', 'year'}
            different resolution means different time string format, see
            **self.key_map** for details.

        Returns
        --------------
        time : datetime.time_struct
        """
        if resolution == 'week':
            return datetime.strptime(t_str + '-0', self.key_map['week'] + '-%w')
        return datetime.strptime(t_str, self.key_map[resolution])

    def viz_count(self, t_type, resolution, width, tick_num, rotation):
        """  visualize the counts for notes for a duration.

        Parameters
        ---------------
        t_type : {'created', 'updated'}
            type of time
        resolution : {'week', 'month', 'year'}
        width : float
            width of bar
        tick_num : int
            number of xticks. xticks are evenly distributed.
        rotation : int, {'vertical', 'horizontal'}
            rotation of the xtick_labels

        Returns
        --------------
        """
        keys, values = self.sort_pair(self.stat['%s-%s' % (t_type, resolution)])

        start = self.strptime(keys[0], resolution)
        ind = np.array([get_time_diff(start, self.strptime(k, resolution), resolution)
                        for k in keys])
        bar(ind, values, keys, 'r', width, tick_num, rotation)
        plt.xlabel('time')
        plt.ylabel('No.')
        plt.title("No. of evernotes per '%s' according to '%s' time."
                  % (resolution, t_type))

    def viz(self):
        """  shortcut for visualization
        """
        # plt.figure()
        # self.viz_count('created', 'week', width=0.5, tick_num=30, rotation=90)

        # plt.figure()
        # self.viz_count('created', 'month', width=0.5, tick_num=None, rotation=90)

        # plt.figure()
        # self.viz_count('created', 'year', width=0.5, tick_num=None, rotation=20)


        plt.figure()
        self.viz_count('updated', 'week', width=0.5, tick_num=30, rotation=70)

        plt.figure()
        self.viz_count('updated', 'month', width=0.5, tick_num=None, rotation=70)

        plt.figure()
        self.viz_count('updated', 'year', width=0.5, tick_num=None, rotation=20)

        plt.show()


def count():
    # notes = json.load(open('../data.json', 'r'))
    notes = json.load(open('/home/wangjing/Evernote-2013-07-24.json', 'r'))
    ve = VizEvernote(notes)
    ve.count('created', 'week')
    ve.count('created', 'year')
    ve.count('created', 'month')
    ve.count('updated', 'week')
    ve.count('updated', 'year')
    ve.count('updated', 'month')
    ve.dump(open('./Evernote-2013-07-24-count.json', 'w'))
    # ve.dump(open('./Evernote-2013-07-24-count2.json', 'w'))
    # import ipdb;ipdb.set_trace()
    # ve.monthly_count()
    # daily_evernotes(notes)


def viz():
    ve = VizEvernote()
    ve.load(open('./Evernote-2013-07-24-count.json', 'r'))
    ve.viz()


if __name__ == "__main__":
    # count()
    viz()