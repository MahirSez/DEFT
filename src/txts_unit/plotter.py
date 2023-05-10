import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def plot_batchSize_vs_packetRate():
    latency_data, throughput_data, throughput_kpps, pkt_dropped_data = [], [], [], []
    for b_size in [10, 30, 60, 100, 500, 1000, 10000]:
        for p_rate in [10000]:
            file_name = f'results/batch_{b_size}-buf_10000-pktrate_{p_rate}-flow_cnt_100-stamper_cnt_1.csv'
            df = pd.read_csv(file_name)
            # print(df)
            # df.drop(0, axis=0, inplace=True)
            column_wise_val = df.mean(axis=0)
            latency_data.append([
                b_size,
                p_rate,
                column_wise_val[0]
            ])

            throughput_data.append([
                b_size,
                p_rate,
                column_wise_val[1] / 1e6
            ])

            throughput_kpps.append([
                b_size,
                p_rate,
                column_wise_val[2] / 1e3
            ])

            pkt_dropped_data.append([
                b_size,
                p_rate,
                column_wise_val[4]
            ])

    dtype_map = {
        'Packet Rate(packets/s)': 'int64',
        'Batch Size': 'int64'
    }

    latency_df = pd.DataFrame(np.asarray(latency_data), columns=['Batch Size', 'Packet Rate(packets/s)', 'Latency(ms)']).astype(dtype_map)
    throughput_df = pd.DataFrame(np.asarray(throughput_data), columns=['Batch Size', 'Packet Rate(packets/s)', 'Throughput(MB/s)']).astype(dtype_map)
    kpps_df = pd.DataFrame(np.asarray(throughput_kpps), columns=['Batch Size', 'Packet Rate(packets/s)', 'Throughput(kpps)']).astype(dtype_map)
    pkt_dropped_df = pd.DataFrame(np.asarray(pkt_dropped_data), columns=['Batch Size', 'Packet Rate(packets/s)', 'Packets Dropped']).astype(dtype_map)

    lat_plt = sns.lineplot(data=latency_df, x="Packet Rate(packets/s)", y="Latency(ms)", hue="Batch Size", style="Batch Size", \
                           markers=True, dashes=False, palette=sns.color_palette('icefire'))
    fig = lat_plt.get_figure()
    fig.savefig('results/latency.png', format='png', dpi=1200)
    plt.close()

    lat_plt = sns.lineplot(data=latency_df, x="Batch Size", y="Latency(ms)", hue="Packet Rate(packets/s)", style="Packet Rate(packets/s)", \
                           markers=True, dashes=False, palette=sns.color_palette('icefire'))
    fig = lat_plt.get_figure()
    fig.savefig('results/latency2.png', format='png', dpi=1200)
    plt.close()

    tpt_plt = sns.lineplot(data=throughput_df, x="Packet Rate(packets/s)", y="Throughput(MB/s)", hue="Batch Size", style="Batch Size", \
                           markers=True, dashes=False, palette=sns.color_palette('icefire'))
    fig = tpt_plt.get_figure()
    fig.savefig('results/throughput.png', format='png', dpi=1200)
    plt.close()

    tpt_kpps_plt = sns.lineplot(data=kpps_df, x="Packet Rate(packets/s)", y="Throughput(kpps)", hue="Batch Size", style="Batch Size", \
                           markers=True, dashes=False, palette=sns.color_palette('icefire'))
    fig = tpt_kpps_plt.get_figure()
    fig.savefig('results/throughput_kpps.png', format='png', dpi=1200)
    plt.close()

    pdp_plt = sns.barplot(data=pkt_dropped_df, x="Batch Size", y="Packets Dropped", hue="Packet Rate(packets/s)", palette=sns.color_palette('viridis'))
    fig = pdp_plt.get_figure()
    fig.savefig('results/packets_dropped.png', format='png', dpi=1200)
    plt.close()



def plot_flowCount_x_stamperCount():
    latency_data, throughput_data, pkt_dropped_data = [], [], []
    for flow_count in [120, 240, 360, 480, 540]:
        for stamper_count in range(1, 11):
            latency, throughput, pkt_drop = [], [], []

            # for trial in range(5):
            file_name = f'results/batch_50-buf_10000-pktrate_10000-flow_cnt_{flow_count}-stamper_cnt_{stamper_count}.csv'
            df = pd.read_csv(file_name)
            latency.append(df.iloc[:, 0].mean(axis=0))
            throughput.append(df.iloc[:, 2].sum(axis=0) / stamper_count)
            pkt_drop.append(df.iloc[:,  4].sum(axis=0) / stamper_count)

            latency_data.append([
                flow_count,
                stamper_count,
                np.mean(latency)
            ])

            throughput_data.append([
                flow_count,
                stamper_count,
                np.mean(throughput) / 1e3
            ])

            pkt_dropped_data.append([
                flow_count,
                stamper_count,
                np.mean(pkt_drop)
            ])

    dtype_map = {
        'Flow Count': 'int64',
        'Stamper Count': 'int64'
    }

    latency_df = pd.DataFrame(np.asarray(latency_data), columns=['Flow Count', 'Stamper Count', 'Latency(ms)']).astype(dtype_map)
    throughput_df = pd.DataFrame(np.asarray(throughput_data), columns=['Flow Count', 'Stamper Count', 'Throughput(kpps)']).astype(dtype_map)
    pkt_dropped_df = pd.DataFrame(np.asarray(pkt_dropped_data), columns=['Flow Count', 'Stamper Count', 'Packets Dropped']).astype(dtype_map)

    lat_plt = sns.lineplot(data=latency_df, x="Stamper Count", y="Latency(ms)", hue="Flow Count", style="Flow Count", \
                           markers=True, dashes=False, palette=sns.color_palette('icefire'))
    fig = lat_plt.get_figure()
    plt.xticks([x for x in range(1, 11)])
    plt.xticks([x for x in range(1, 11)])
    plt.ylim([0, 100])
    fig.savefig('results/latency.png', format='png', dpi=1200)
    plt.close()

    tpt_plt = sns.lineplot(data=throughput_df, x="Flow Count", y="Throughput(kpps)", hue="Stamper Count", style="Stamper Count", \
                           markers=True, dashes=False, palette=sns.color_palette('viridis'))
    plt.xticks([120, 240, 360, 480, 540])
    fig = tpt_plt.get_figure()
    fig.savefig('results/throughput.png', format='png', dpi=1200)
    plt.close()

    pdp_plt = sns.lineplot(data=pkt_dropped_df, x="Stamper Count", y="Packets Dropped", hue="Flow Count", style="Flow Count", \
                           markers=True, dashes=False, palette=sns.color_palette('viridis'))
    fig = pdp_plt.get_figure()
    plt.ylim([0, 100])
    fig.savefig('results/packets_dropped.png', format='png', dpi=1200)
    plt.close()


def plot_batch_size_experiment():
    latency_data, throughput_data,\
        throughput_kpps_data, pkt_dropped_data = [], [], [], []
    for size in range(10, 160, 10):
        path = f'batch_size/results/batch_{size}-buf_100-pktrate_0-flow_cnt_1-stamper_cnt_1.csv'
        df = pd.read_csv(path)
        df.drop(0, axis=0, inplace=True)
        column_wise_val = df.mean(axis=0)

        latency_data.append([
            size,
            column_wise_val[0]
        ])

        throughput_data.append([
            size,
            column_wise_val[1] / 1e3
        ])

        throughput_kpps_data.append([
            size,
            column_wise_val[2] / 1e3
        ])

        pkt_dropped_data.append([
            size,
            column_wise_val[3]
        ])

    dtype_map = {
        'Batch Size' : 'int64'
    }

    latency_df = pd.DataFrame(np.asarray(latency_data), columns=['Batch Size', 'Latency(ms)']).astype(dtype_map)
    throughput_df = pd.DataFrame(np.asarray(throughput_data), columns=['Batch Size', 'Throughput (kB/s)']).astype(dtype_map)
    throughput_df = pd.DataFrame(np.asarray(throughput_kpps_data), columns=['Batch Size', 'Throughput (kpps)']).astype(dtype_map)
    pkt_dropped_df = pd.DataFrame(np.asarray(pkt_dropped_data), columns=['Batch Size', 'Packets Dropped']).astype(dtype_map)

    lat_plt = sns.lineplot(data=latency_df, x="Stamper Count", y="Latency(ms)", hue="Flow Count", style="Flow Count", \
                           markers=True, dashes=False, palette=sns.color_palette('icefire'))
    fig = lat_plt.get_figure()
    plt.xticks(range(10, 160, 10))
    plt.ylim([0, 100])
    fig.savefig('plots/flow_count_x_stamper_count/latency.png', format='png', dpi=1200)
    plt.close()

    tpt_plt = sns.lineplot(data=throughput_df, x="Flow Count", y="Throughput(MB/s)", hue="Stamper Count", style="Stamper Count", \
                           markers=True, dashes=False, palette=sns.color_palette('viridis'))
    plt.xticks([5, 10, 15, 20, 25])
    fig = tpt_plt.get_figure()
    fig.savefig('plots/flow_count_x_stamper_count/throughput.png', format='png', dpi=1200)
    plt.close()

    pdp_plt = sns.lineplot(data=pkt_dropped_df, x="Stamper Count", y="Packets Dropped", hue="Flow Count", style="Flow Count", \
                           markers=True, dashes=False, palette=sns.color_palette('icefire'))
    fig = pdp_plt.get_figure()
    plt.ylim([0, 100])
    fig.savefig('plots/flow_count_x_stamper_count/packets_dropped.png', format='png', dpi=1200)
    plt.close()

def plot_bufferSize_vs_packetRate():
    latency_data, throughput_data, throughput_kpps, pkt_dropped_data = [], [], [], []
    for b_size in [1, 2, 3, 4, 5]:
        for p_rate in [4000, 8000, 12000]:
            file_name = f'results/batch_80-buf_{b_size}-pktrate_{p_rate}-flow_cnt_100-stamper_cnt_1.csv'
            df = pd.read_csv(file_name)
            # print(df)
            # df.drop(0, axis=0, inplace=True)
            column_wise_val = df.mean(axis=0)
            latency_data.append([
                b_size,
                p_rate,
                column_wise_val[0]
            ])

            throughput_data.append([
                b_size,
                p_rate,
                column_wise_val[1] / 1e6
            ])

            throughput_kpps.append([
                b_size,
                p_rate,
                column_wise_val[2] / 1e3
            ])

            pkt_dropped_data.append([
                b_size,
                p_rate,
                column_wise_val[4]
            ])

    dtype_map = {
        'Packet Rate(packets/s)': 'int64',
        'BufSize_to_BatSize': 'int64'
    }

    latency_df = pd.DataFrame(np.asarray(latency_data), columns=['BufSize_to_BatSize', 'Packet Rate(packets/s)', 'Latency(ms)']).astype(dtype_map)
    throughput_df = pd.DataFrame(np.asarray(throughput_data), columns=['BufSize_to_BatSize', 'Packet Rate(packets/s)', 'Throughput(MB/s)']).astype(dtype_map)
    kpps_df = pd.DataFrame(np.asarray(throughput_kpps), columns=['BufSize_to_BatSize', 'Packet Rate(packets/s)', 'Throughput(kpps)']).astype(dtype_map)
    pkt_dropped_df = pd.DataFrame(np.asarray(pkt_dropped_data), columns=['BufSize_to_BatSize', 'Packet Rate(packets/s)', 'Packets Dropped']).astype(dtype_map)

    lat_plt = sns.lineplot(data=latency_df, x="BufSize_to_BatSize", y="Latency(ms)", hue="Packet Rate(packets/s)", style="Packet Rate(packets/s)", \
                           markers=True, dashes=False, palette=sns.color_palette('icefire'))
    fig = lat_plt.get_figure()
    fig.savefig('results/latency.png', format='png', dpi=1200)
    plt.close()

    tpt_plt = sns.lineplot(data=throughput_df, x="BufSize_to_BatSize", y="Throughput(MB/s)", hue="Packet Rate(packets/s)", style="Packet Rate(packets/s)", \
                           markers=True, dashes=False, palette=sns.color_palette('icefire'))
    fig = tpt_plt.get_figure()
    fig.savefig('results/throughput.png', format='png', dpi=1200)
    plt.close()

    tpt_kpps_plt = sns.lineplot(data=kpps_df, x="BufSize_to_BatSize", y="Throughput(kpps)", hue="Packet Rate(packets/s)", style="Packet Rate(packets/s)", \
                           markers=True, dashes=False, palette=sns.color_palette('icefire'))
    fig = tpt_kpps_plt.get_figure()
    fig.savefig('results/throughput_kpps.png', format='png', dpi=1200)
    plt.close()

    pdp_plt = sns.barplot(data=pkt_dropped_df, x="BufSize_to_BatSize", y="Packets Dropped", hue="Packet Rate(packets/s)", palette=sns.color_palette('icefire'))
    fig = pdp_plt.get_figure()
    fig.savefig('results/packets_dropped.png', format='png', dpi=1200)
    plt.close()

def plot_globalUpdateFreq_vs_packetRate():
    latency_data, throughput_data, throughput_kpps, pkt_dropped_data = [], [], [], []
    for uf in [1, 2, 3, 4, 5]:
        for p_rate in [1000, 2000, 5000, 8000]:
            # batch_80-gf_1-buf_10000-pktrate_8000-flow_cnt_100-stamper_cnt_1.csv
            file_name = f'results/batch_80-gf_{uf}-buf_10000-pktrate_{p_rate}-flow_cnt_100-stamper_cnt_1.csv'
            df = pd.read_csv(file_name)
            # print(df)
            # df.drop(0, axis=0, inplace=True)
            column_wise_val = df.mean(axis=0)
            latency_data.append([
                uf,
                p_rate,
                column_wise_val[0]
            ])

            throughput_data.append([
                uf,
                p_rate,
                column_wise_val[1] / 1e6
            ])

            throughput_kpps.append([
                uf,
                p_rate,
                column_wise_val[2] / 1e3
            ])

            pkt_dropped_data.append([
                uf,
                p_rate,
                column_wise_val[4]
            ])

    dtype_map = {
        'Packet Rate(kpps)': 'int64',
        'Global Update Frequency': 'int64'
    }

    latency_df = pd.DataFrame(np.asarray(latency_data), columns=['Global Update Frequency', 'Packet Rate(kpps)', 'Latency(ms)']).astype(dtype_map)
    throughput_df = pd.DataFrame(np.asarray(throughput_data), columns=['Global Update Frequency', 'Packet Rate(kpps)', 'Throughput(MB/s)']).astype(dtype_map)
    kpps_df = pd.DataFrame(np.asarray(throughput_kpps), columns=['Global Update Frequency', 'Packet Rate(kpps)', 'Throughput(kpps)']).astype(dtype_map)
    pkt_dropped_df = pd.DataFrame(np.asarray(pkt_dropped_data), columns=['Global Update Frequency', 'Packet Rate(kpps)', 'Packets Dropped']).astype(dtype_map)

    lat_plt = sns.lineplot(data=latency_df, x="Global Update Frequency", y="Latency(ms)", hue="Packet Rate(kpps)", style="Packet Rate(kpps)", \
                           markers=True, dashes=False, palette=sns.color_palette('icefire'))
    fig = lat_plt.get_figure()
    fig.savefig('results/latency.png', format='png', dpi=1200)
    plt.close()

    tpt_plt = sns.lineplot(data=throughput_df, x="Global Update Frequency", y="Throughput(MB/s)", hue="Packet Rate(kpps)", style="Packet Rate(kpps)", \
                           markers=True, dashes=False, palette=sns.color_palette('icefire'))
    fig = tpt_plt.get_figure()
    fig.savefig('results/throughput.png', format='png', dpi=1200)
    plt.close()

    tpt_kpps_plt = sns.lineplot(data=kpps_df, x="Global Update Frequency", y="Throughput(kpps)", hue="Packet Rate(kpps)", style="Packet Rate(kpps)", \
                           markers=True, dashes=False, palette=sns.color_palette('icefire'))
    fig = tpt_kpps_plt.get_figure()
    fig.savefig('results/throughput_kpps.png', format='png', dpi=1200)
    plt.close()

    pdp_plt = sns.barplot(data=pkt_dropped_df, x="Global Update Frequency", y="Packets Dropped", hue="Packet Rate(kpps)", palette=sns.color_palette('icefire'))
    fig = pdp_plt.get_figure()
    fig.savefig('results/packets_dropped.png', format='png', dpi=1200)
    plt.close()


if __name__ == "__main__":
    # plot_batchSize_vs_packetRate()
    plot_flowCount_x_stamperCount()
    # plot_bufferSize_vs_packetRate()
    # plot_globalUpdateFreq_vs_packetRate()
    # df = pd.read_csv('results/batch_10-buf_1000-pktrate_250-flow_cnt_1-stamper_cnt_1.csv')
    # print(df.columns)
    # print(df)
