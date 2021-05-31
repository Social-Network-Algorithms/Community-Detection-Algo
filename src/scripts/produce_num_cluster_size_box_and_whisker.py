import glob
import json
import argparse
import matplotlib.pyplot as plt
import numpy as np

def produce_plots(user_name):
    # series = ['100', '80', '60', '40', '20']
    series = ['0', '200', '400', '600', '800', '1000', '1200', '1400', '1600', '1800', '2000']
    labels = []
    series_means = {}

    # fig = plt.figure()

    fig, axes = plt.subplots(2, 3)
    fig.suptitle('Cluster Size by Data Cleaning Threshold for User: ' + str(user_name))
    types = ['default', 'follower_only', 'tweet_only']
    titles = ['Data Cleaning By Tweets and Followers', 'Data Cleaning By Followers Only', 'Data Cleaning By Tweets Only']

    for i in range(len(types)):
        ax1, ax2 = axes[:, i]
        type = types[i]
        title = titles[i]

        series_counts = []
        for val in series:
            filename_list = glob.glob('./dc3_exp/' + str(type) + '/clusters_' + str(val) + '/' + str(user_name) + '_clusters_*.json')
            counts1 = []
            counts2 = []

            for filename in filename_list:
                with open(filename, 'r') as file:
                    user_lists = json.load(file)
                    count = len(user_lists)
                    if count == 2:
                        if len(user_lists[0]) > len(user_lists[1]):
                            cluster1 = user_lists[0]
                            cluster2 = user_lists[1]
                        else:
                            cluster1 = user_lists[1]
                            cluster2 = user_lists[0]

                        counts1.append(len(cluster1))
                        counts2.append(len(cluster2))

            series_counts.append([counts1, counts2])

        num_series = len(series)

        data1 = []
        data2 = []

        for i in range(len(series)):
            count1, count2 = series_counts[i]
            data1.append(count1)
            data2.append(count2)

        ax1.boxplot(data1, labels=series)
        print(data1)
        ax2.boxplot(data2, labels=series)

        x = np.arange(len(series))

        # Add some text for labels, title and custom x-axis tick labels, etc.
        for ax in [ax1, ax2]:
            ax.set_ylabel('Size of Cluster (Number of Users)')
            ax.set_xlabel('Data Cleaning Parameter (threshold)')

        ax1.set_title("Cluster 1\n" +  title, fontsize=10)
        ax2.set_title("Cluster 2\n" +  title, fontsize=10)

    plt.show()

if __name__ == "__main__":
    """
    Short script to produce scatter plots
    """
    parser = argparse.ArgumentParser(description='Short script to produce scatter plots of utility')
    parser.add_argument('-n', '--screen_name', dest='name',
        help="The screen name of the user to download", required=True)

    args = parser.parse_args()

    produce_plots(args.name)
