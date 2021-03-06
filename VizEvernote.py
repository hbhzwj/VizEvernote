#!/usr/bin/env python
from __future__ import print_function, division, absolute_import
import time
import itertools
import json
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from dateutil import rrule
from util import bar


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


class Analyzer(object):

    def dump(self, fp):
        json.dump(self.stat, fp)

    def load(self, fp):
        self.stat = json.load(fp)


class EvernoteAnalyzer(Analyzer):
    """  Analyze Evernote Data

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
        'day': 24 * 3600,
    }

    def __init__(self, notes=None):
        self.notes = notes
        self.stat = dict()

    @staticmethod
    def parse_time(string):
        return time.strptime(string, "%Y%m%dT%H%M%SZ")

    @staticmethod
    def filter(notes, t_type, tag=None):
        """  filter notes

        Parameters
        ---------------
        notes : list
            a list of notes
        t_type : {'created', 'updated'}
            type of time. Only notes with this field is presented
        tag : {None, str}
            if tag == None: tag field is not checked. Otherwise, only notes
                whose tag field equals are preserved.

        Returns
        --------------
        selected_notes : list
        """
        if tag is None:
            return [note for note in notes if note.get(t_type)]
        else:
            return [note for note in notes
                    if note.get(t_type) and note.get('tag', '') == tag]

    def count(self, t_type, resolution, tag=None):
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
        if tag is None:
            stat_key = '%s-%s' % (t_type, resolution)
        else:
            stat_key = '%s-%s-%s' % (t_type, resolution, tag)

        notes = self.filter(self.notes, t_type, tag)
        # if resolution == 'year': import ipdb;ipdb.set_trace()
        tm = [self.parse_time(note[t_type]) for note in notes]
        sorted_tm = sorted(tm, key=lambda x: time.mktime(x))
        group_key = lambda x: time.strftime(self.key_map[resolution], x)
        self.stat[stat_key] = group_count(sorted_tm, group_key)
        return self.stat[stat_key]

    def group_by_tags(self, t_type):
        notes = sorted(self.notes, key=lambda x: x.get('tag'))
        tags_groups = itertools.groupby(notes, lambda x: x.get('tag'))
        tag_t = dict()
        for tag, tag_notes in tags_groups:
            stat_key = '%s-%s' % (tag, t_type)
            tag_t[stat_key] = [note[t_type] for note in tag_notes if note.get(t_type)]
        self.stat['tag_t'] = tag_t

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


class EvernoteVisualizer(EvernoteAnalyzer):

    @staticmethod
    def sort_pair(d):
        return zip(*sorted(d.items()))

    def plot_count(self, t_type, resolution, width, tick_num, rotation):
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

    def plot_tags_t(self, t_type, xticks_type, rotation):
        """  For each tag, plot the `t_type` time of notes with this tag.

        Parameters
        ---------------
        t_type : {'created', 'updated'}
            type of time
        xticks_type: {'week', 'month', 'year'}
        rotation : int, {'vertical', 'horizontal'}
            rotation of the xtick_labels

        Returns
        --------------
        None
        """
        tag_t = self.stat['tag_t']
        tag_seq = 0
        markers = 'o+x>'
        tags = []
        # xtick_labels = []
        min_t = np.inf
        max_t = -np.inf
        for k, v in tag_t.iteritems():
            kr = k.rsplit('-')
            if kr[1] == t_type and kr[0] != 'None':
                tags.append(kr[0])
                tag_seq += 1
                vt = np.array([time.mktime(self.parse_time(v_)) for v_ in v])
                min_vt = min(vt)
                min_t = min_vt if min_vt < min_t else min_t
                max_vt = max(vt)
                max_t = max_vt if max_vt > max_t else max_t
                # vt /= (3600 * 24 * 30)
                plt.plot(vt, tag_seq * np.ones((len(vt),)),
                         linestyle='', marker=markers[tag_seq % len(markers)])
        xticks = np.arange(min_t, max_t, self.dur_map[xticks_type])
        plt.xticks(xticks,
                   [str(i) for i in range(len(xticks))],
                   rotation=rotation)
        plt.xlabel(xticks_type)
        plt.yticks(range(1, len(tags) + 1), tags)
        plt.ylim([0, len(tags) + 1])
        plt.title("'%s' time by '%s' of different tags."
                  % (t_type, xticks_type))
