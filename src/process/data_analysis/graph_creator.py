import csv
import numpy as np
from matplotlib import pyplot as plt


class GraphCreator:
    def __init__(self, file_path):
        self.file_path = file_path

    def create_graph_users(self, filename_prefix, start_iteration,
                           end_iteration, col, xlabel, ylabel, title):
        """
        Compare old users with new users
        """
        old_user = []
        value_new = []
        value_old = []
        # read old users
        file_str = filename_prefix + "_iteration_" + str(start_iteration)
        file = open(self.file_path + file_str + '.csv')
        csv_reader = csv.reader(file)
        _ = next(csv_reader)
        for row in csv_reader:
            # old users = new users in start_iteration
            if row[-1] == '1':
                old_user.append(row[1])
        file.close()

        # read final users data
        file_str = filename_prefix + "_iteration_" + str(end_iteration)
        file = open(self.file_path + file_str + '.csv')
        csv_reader = csv.reader(file)
        _ = next(csv_reader)
        for row in csv_reader:
            # col=the column of the value we want to compare
            value = float(row[col])
            # If is the last iteration
            if row[1] in old_user:
                value_old.append(value)
            else:
                value_new.append(value)
        file.close()

        width = 1
        group_gap = 1
        y1 = value_old
        y2 = value_new
        x1 = np.arange(len(y1))
        x2 = np.arange(len(y2)) + group_gap + len(y1)
        fig, ax = plt.subplots()
        _ = ax.bar(x1, y1, width, color='r', edgecolor="black", label="old")
        _ = ax.bar(x2, y2, width, color='b', edgecolor="black", label="new")
        ax.set_title(title, fontsize=14)
        ax.set_ylabel(ylabel, fontsize=14)
        ax.set_xlabel(xlabel)
        # plt.savefig(fig_name)
        plt.show()

    def create_graph_iterations(self, filename_prefix, start_iteration,
                                end_iteration, col, xlabel, ylabel, title):
        """
        Compare users utility score by iteration
        """
        users = []
        value_old = []
        value_new = []
        # read old value
        file_str = filename_prefix + "_iteration_" + str(start_iteration)
        file = open(self.file_path + file_str + '.csv')
        csv_reader = csv.reader(file)
        _ = next(csv_reader)
        for row in csv_reader:
            users.append(row[1])
            value_old.append(row[col])
        file.close()

        # read new value
        file_str = filename_prefix + "_iteration_" + str(end_iteration)
        file = open(self.file_path + file_str + '.csv')
        csv_reader = csv.reader(file)
        _ = next(csv_reader)
        for row in csv_reader:
            if row[1] in users:
                value_new.append(row[col])
        file.close()

        width = 1
        group_gap = 1
        y1 = value_old
        y2 = value_new
        x1 = np.arange(len(y1))
        x2 = np.arange(len(y2)) + group_gap + len(y1)
        fig, ax = plt.subplots()
        _ = ax.bar(x1, y1, width, color='r', edgecolor="black")
        _ = ax.bar(x2, y2, width, color='g', edgecolor="black")
        ax.set_title(title, fontsize=14)
        ax.set_ylabel(ylabel, fontsize=14)
        ax.set_xlabel(xlabel)
        # plt.savefig(fig_name)
        plt.show()