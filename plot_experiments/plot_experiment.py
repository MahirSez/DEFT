import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def plot_batchSize_vs_packetRate():
    latency_data, throughput_data, throughput_kpps, pkt_dropped_data = [], [], [], []
    for b_size in range(20, 150, 20):
        for p_rate in range(2500, 8000, 1000):
            file_name = f'bsize_prate/batch_{b_size}-gf_1-buf_1-pktrate_{p_rate}-flow_cnt_1-stamper_cnt_1.csv'
            df = pd.read_csv(file_name)
            print(df)
            df.drop(0, axis=0, inplace=True)
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
                column_wise_val[3]
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
    fig.savefig('plots/batch_size_vs_pkt_rate/latency.pdf', format='pdf', dpi=1200)
    plt.close()

    lat_plt = sns.lineplot(data=latency_df, x="Batch Size", y="Latency(ms)", hue="Packet Rate(packets/s)", style="Packet Rate(packets/s)", \
                           markers=True, dashes=False, palette=sns.color_palette('icefire'))
    fig = lat_plt.get_figure()
    fig.savefig('plots/batch_size_vs_pkt_rate/latency2.pdf', format='pdf', dpi=1200)
    plt.close()

    tpt_plt = sns.lineplot(data=throughput_df, x="Packet Rate(packets/s)", y="Throughput(MB/s)", hue="Batch Size", style="Batch Size", \
                           markers=True, dashes=False, palette=sns.color_palette('icefire'))
    fig = tpt_plt.get_figure()
    fig.savefig('plots/batch_size_vs_pkt_rate/throughput.pdf', format='pdf', dpi=1200)
    plt.close()

    tpt_kpps_plt = sns.lineplot(data=kpps_df, x="Packet Rate(packets/s)", y="Throughput(kpps)", hue="Batch Size", style="Batch Size", \
                           markers=True, dashes=False, palette=sns.color_palette('icefire'))
    fig = tpt_kpps_plt.get_figure()
    fig.savefig('plots/batch_size_vs_pkt_rate/throughput_kpps.pdf', format='pdf', dpi=1200)
    plt.close()

    pdp_plt = sns.barplot(data=pkt_dropped_df, x="Batch Size", y="Packets Dropped", hue="Packet Rate(packets/s)", palette=sns.color_palette('viridis'))
    fig = pdp_plt.get_figure()
    fig.savefig('plots/batch_size_vs_pkt_rate/packets_dropped.pdf', format='pdf', dpi=1200)
    plt.close()

def plot_flowCount_x_stamperCount():
    latency_data, throughput_data, pkt_dropped_data = [], [], []
    for flow_count in range(5, 30, 5):
        for stamper_count in range(1, 6):
            flow_count_per_nf = flow_count // 5
            latency, throughput, pkt_drop = [], [], []
            for trial in range(1, 6):
                file_name = f'fl_cnt_v_st_cnt/results/run_{trial}-batch_70-buf_1000-pktrate_1500-flow_cnt_{flow_count_per_nf}-stamper_cnt_{stamper_count}.csv'
                df = pd.read_csv(file_name)
                latency.append(df.iloc[:, 1].mean(axis=0))
                throughput.append(df.iloc[:, 2].sum(axis=0)/5)
                pkt_drop.append(df.iloc[:, 3].sum(axis=0)/5)

            latency_data.append([
                flow_count,
                stamper_count,
                np.mean(latency)
            ])

            throughput_data.append([
                flow_count,
                stamper_count,
                np.mean(throughput) / 1e6
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
    throughput_df = pd.DataFrame(np.asarray(throughput_data), columns=['Flow Count', 'Stamper Count', 'Throughput(MB/s)']).astype(dtype_map)
    pkt_dropped_df = pd.DataFrame(np.asarray(pkt_dropped_data), columns=['Flow Count', 'Stamper Count', 'Packets Dropped']).astype(dtype_map)

    lat_plt = sns.lineplot(data=latency_df, x="Stamper Count", y="Latency(ms)", hue="Flow Count", style="Flow Count", \
                           markers=True, dashes=False, palette=sns.color_palette('icefire'))
    fig = lat_plt.get_figure()
    plt.xticks([1, 2, 3, 4, 5])
    plt.ylim([0, 100])
    fig.savefig('plots/flow_count_x_stamper_count/latency.pdf', format='pdf', dpi=1200)
    plt.close()

    tpt_plt = sns.lineplot(data=throughput_df, x="Flow Count", y="Throughput(MB/s)", hue="Stamper Count", style="Stamper Count", \
                           markers=True, dashes=False, palette=sns.color_palette('viridis'))
    plt.xticks([5, 10, 15, 20, 25])
    fig = tpt_plt.get_figure()
    fig.savefig('plots/flow_count_x_stamper_count/throughput.pdf', format='pdf', dpi=1200)
    plt.close()

    pdp_plt = sns.lineplot(data=pkt_dropped_df, x="Stamper Count", y="Packets Dropped", hue="Flow Count", style="Flow Count", \
                           markers=True, dashes=False, palette=sns.color_palette('viridis'))
    fig = pdp_plt.get_figure()
    plt.ylim([0, 100])
    fig.savefig('plots/flow_count_x_stamper_count/packets_dropped.pdf', format='pdf', dpi=1200)
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
    fig.savefig('plots/flow_count_x_stamper_count/latency.pdf', format='pdf', dpi=1200)
    plt.close()

    tpt_plt = sns.lineplot(data=throughput_df, x="Flow Count", y="Throughput(MB/s)", hue="Stamper Count", style="Stamper Count", \
                           markers=True, dashes=False, palette=sns.color_palette('viridis'))
    plt.xticks([5, 10, 15, 20, 25])
    fig = tpt_plt.get_figure()
    fig.savefig('plots/flow_count_x_stamper_count/throughput.pdf', format='pdf', dpi=1200)
    plt.close()

    pdp_plt = sns.lineplot(data=pkt_dropped_df, x="Stamper Count", y="Packets Dropped", hue="Flow Count", style="Flow Count", \
                           markers=True, dashes=False, palette=sns.color_palette('icefire'))
    fig = pdp_plt.get_figure()
    plt.ylim([0, 100])
    fig.savefig('plots/flow_count_x_stamper_count/packets_dropped.pdf', format='pdf', dpi=1200)
    plt.close()

def plot_bufferSize_vs_packetRate():
    latency_data, throughput_data, throughput_kpps, pkt_dropped_data = [], [], [], []
    for b_size in range(1, 11):
        for p_rate in range(500, 6100, 1000):
            file_name = f'pr_vs_bfs/batch_80-buf_{b_size}-pktrate_{p_rate}-flow_cnt_1-stamper_cnt_1.csv'
            df = pd.read_csv(file_name)
            print(df)
            df.drop(0, axis=0, inplace=True)
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
                column_wise_val[3]
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
    fig.savefig('plots/buffer_size_vs_pkt_rate/latency.pdf', format='pdf', dpi=1200)
    plt.close()

    tpt_plt = sns.lineplot(data=throughput_df, x="BufSize_to_BatSize", y="Throughput(MB/s)", hue="Packet Rate(packets/s)", style="Packet Rate(packets/s)", \
                           markers=True, dashes=False, palette=sns.color_palette('icefire'))
    fig = tpt_plt.get_figure()
    fig.savefig('plots/buffer_size_vs_pkt_rate/throughput.pdf', format='pdf', dpi=1200)
    plt.close()

    tpt_kpps_plt = sns.lineplot(data=kpps_df, x="BufSize_to_BatSize", y="Throughput(kpps)", hue="Packet Rate(packets/s)", style="Packet Rate(packets/s)", \
                           markers=True, dashes=False, palette=sns.color_palette('icefire'))
    fig = tpt_kpps_plt.get_figure()
    fig.savefig('plots/buffer_size_vs_pkt_rate/throughput_kpps.pdf', format='pdf', dpi=1200)
    plt.close()

    pdp_plt = sns.barplot(data=pkt_dropped_df, x="BufSize_to_BatSize", y="Packets Dropped", hue="Packet Rate(packets/s)", palette=sns.color_palette('icefire'))
    fig = pdp_plt.get_figure()
    fig.savefig('plots/buffer_size_vs_pkt_rate/packets_dropped.pdf', format='pdf', dpi=1200)
    plt.close()

def plot_globalUpdateFreq_vs_packetRate():
    latency_data, throughput_data, throughput_kpps, pkt_dropped_data = [], [], [], []
    for uf in [1, 5, 10, 15, 20, 40]:
        for p_rate in range(500, 6100, 1000):
            file_name = f'pr_vs_gfu/batch_80-gf_{uf}-buf_1-pktrate_{p_rate}-flow_cnt_1-stamper_cnt_1.csv'
            df = pd.read_csv(file_name)
            print(df)
            df.drop(0, axis=0, inplace=True)
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
                column_wise_val[3]
            ])

    dtype_map = {
        'Packet Rate(packets/s)': 'int64',
        'Global Update Frequency': 'int64'
    }

    latency_df = pd.DataFrame(np.asarray(latency_data), columns=['Global Update Frequency', 'Packet Rate(packets/s)', 'Latency(ms)']).astype(dtype_map)
    throughput_df = pd.DataFrame(np.asarray(throughput_data), columns=['Global Update Frequency', 'Packet Rate(packets/s)', 'Throughput(MB/s)']).astype(dtype_map)
    kpps_df = pd.DataFrame(np.asarray(throughput_kpps), columns=['Global Update Frequency', 'Packet Rate(packets/s)', 'Throughput(kpps)']).astype(dtype_map)
    pkt_dropped_df = pd.DataFrame(np.asarray(pkt_dropped_data), columns=['Global Update Frequency', 'Packet Rate(packets/s)', 'Packets Dropped']).astype(dtype_map)

    lat_plt = sns.lineplot(data=latency_df, x="Global Update Frequency", y="Latency(ms)", hue="Packet Rate(packets/s)", style="Packet Rate(packets/s)", \
                           markers=True, dashes=False, palette=sns.color_palette('icefire'))
    fig = lat_plt.get_figure()
    fig.savefig('plots/uf_vs_pkt_rate/latency.pdf', format='pdf', dpi=1200)
    plt.close()

    tpt_plt = sns.lineplot(data=throughput_df, x="Global Update Frequency", y="Throughput(MB/s)", hue="Packet Rate(packets/s)", style="Packet Rate(packets/s)", \
                           markers=True, dashes=False, palette=sns.color_palette('icefire'))
    fig = tpt_plt.get_figure()
    fig.savefig('plots/uf_vs_pkt_rate/throughput.pdf', format='pdf', dpi=1200)
    plt.close()

    tpt_kpps_plt = sns.lineplot(data=kpps_df, x="Global Update Frequency", y="Throughput(kpps)", hue="Packet Rate(packets/s)", style="Packet Rate(packets/s)", \
                           markers=True, dashes=False, palette=sns.color_palette('icefire'))
    fig = tpt_kpps_plt.get_figure()
    fig.savefig('plots/uf_vs_pkt_rate/throughput_kpps.pdf', format='pdf', dpi=1200)
    plt.close()

    pdp_plt = sns.barplot(data=pkt_dropped_df, x="Global Update Frequency", y="Packets Dropped", hue="Packet Rate(packets/s)", palette=sns.color_palette('icefire'))
    fig = pdp_plt.get_figure()
    fig.savefig('plots/uf_vs_pkt_rate/packets_dropped.pdf', format='pdf', dpi=1200)
    plt.close()


if __name__ == "__main__":
    plot_batchSize_vs_packetRate()
    # plot_flowCount_x_stamperCount()
    # plot_bufferSize_vs_packetRate()
    # plot_globalUpdateFreq_vs_packetRate()
    # df = pd.read_csv('results/batch_10-buf_1000-pktrate_250-flow_cnt_1-stamper_cnt_1.csv')
    # print(df.columns)
    # print(df)
