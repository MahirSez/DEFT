import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def fit_latency(ax, x, y):    
    mask = np.isnan(y)
    x = x[~mask]
    y = y[~mask]

    ax.plot(x, y, marker='x', markersize=10, markeredgecolor='red', label='Latency')

    ax.set_xlabel("Time(s)", fontsize=20)
    ax.set_ylabel("Latency(ms)", fontsize=20)
    y_lim = 41
    ax.set_ylim(0, y_lim)
    ax.set_xlim(left=x.values[0], right=x.values[len(x.values)-1])
    ax.tick_params(axis='x', labelsize=16)
    ax.tick_params(axis='y', labelsize=16)
    ax.set_yticks(np.arange(0, y_lim, 5))
    ax.set_xticks(np.arange(x.values[0], x.values[len(x.values)-1], 0.2))
    ax.legend(loc='upper left', fontsize=20)

    y_labels = ax.get_yticklabels()
    for y_label in y_labels:
        y_label_ycord = y_label.get_position()[1]
        ax.axhline(y=y_label_ycord, color='gray', linestyle='-', alpha=0.2)



def fit_throughput(ax2, x, z):

    ax2.plot(x, z, alpha=0.1, color="green", label='Throughput')
    ax2.set_ylabel('Throughput(Kpps)', fontsize=20)
    ax2.fill_between(x, 0, z, color='green', alpha=0.1)
    y_max = 16
    ax2.set_yticks(np.arange(0, y_max, 2))
    ax2.set_ylim(0, y_max)
    ax2.tick_params(axis='y', labelsize=16)
    leg = ax2.legend(loc='upper center', fontsize=20)

    for line in leg.get_lines():
        line.set_linewidth(10.0)
        line.set_alpha(0.4)



def retrieve_data():
    df = pd.read_csv('results/timelapse-173.16.1.2.csv')

    df = df.rename(columns={
        "Time(s)": "X",
        "Latency": "Y",
        "PPS": "Z"})

    # x_min = 24
    # x_max = 25.6
    
    x_min = 23
    x_max = 25.5

    
    with open('results/x_lims.txt', 'w') as file:
        file.write(f'x_min={x_min}\n')
        file.write(f'x_max={x_max}\n')


    df = df.loc[(x_min <= df['X']) & (df['X'] <= x_max)]

    df['Y'] = pd.to_numeric(df['Y'], errors='coerce')

    x = df['X']
    y = df['Y']
    z = df['Z'] / 10 ** 3


    return x, y, z



def main():
    x, y, z = retrieve_data()
    fig = plt.figure(figsize=(20, 10))
    ax = fig.add_subplot()
    ax.clear()
    ax2 = ax.twinx()

    fit_latency(ax, x, y)
    fit_throughput(ax2, x, z)


    plt.draw()
    plt.show()

    fig.savefig('results/timelapse.pdf', format='pdf', dpi=1200)
    # fig.savefig('results/timelapse.png')



if __name__ == "__main__":
    main()