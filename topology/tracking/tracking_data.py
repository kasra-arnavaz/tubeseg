from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from cached_property import cached_property
import os

from topology.cyc_cmp import Cycle, Component, NxGraph
from topology.unpickle import read_pickle

class TrackingData(ABC):

    @abstractmethod
    def get_data(self):
        pass

    def plot_data(self):
        data = self.get_data()
        plt.figure()
        plt.title('Data')
        plt.scatter(data.x, data.y, c=data.iloc[:,-1], s=5, cmap='jet')
        plt.gca().invert_yaxis()
        plt.xlim((0,1024))
        plt.ylim(0,1024)
        plt.show()


class Silja(TrackingData):

    def __init__(self, path, name):
        self.path = path
        self.name = name
        

    def get_data(self):
        return pd.read_csv(f'{self.path}/{self.name}.csv')

class Prediction(TrackingData):

    def __init__(self, cyc_path, name):
        self.cyc_path = cyc_path
        self.name = name
        self.num_tp = len([file for file in os.listdir(self.cyc_path) if file.endswith('.cyc')])

    @cached_property
    def all_cycles(self):
        x = []
        for tp in range(self.num_tp):
            y = read_pickle(f'{self.cyc_path}/{self.name}_tp{tp+1}.cyc')
            x.append(y)
        return x

    @cached_property
    def all_centers(self):
        centers = {}
        for t, cyc in enumerate(self.all_cycles):
            temp = np.zeros([cyc.len, 3])
            for i, center in cyc.center.items():
                temp[i] = center
            centers[t+1] = temp
        return centers

    def get_centers_and_frames(self):
        center_and_frames = np.zeros([1,4])
        for t, centers in self.all_centers.items():
            frame_appended = np.append(centers, np.tile(t, centers.shape[0]).reshape(-1,1), axis=1)
            center_and_frames = np.append(center_and_frames, frame_appended, axis=0)
        return center_and_frames[1:]

    def get_data(self):
        return pd.DataFrame(self.get_centers_and_frames(), columns=['z', 'y', 'x', 'frame'])


if __name__ == '__main__':
    pred = Silja('.', 'LI 2018-12-07_emb6_pos4_val')
    pred.plot_data()    