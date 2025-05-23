import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker

# Config
LOG_DIR = "./CompactionLogs"
PLOT_DIR = "./plots/"

if not os.path.exists(PLOT_DIR):
    os.makedirs(PLOT_DIR)

FILENAME_REGEX = re.compile(
    r"(?P<strategy>\w+?)_(?P<insertedkeys>\d+)keys_(?P<totalops>\d+)ops_(?P<nodes>\d+)nodes_(?P<workload>[a-zA-Z0-9]+)workload\.log"
)
EXECUTION_LINE_REGEX = re.compile(r"Executed\s+(\d+)\s+ops\s+in\s+([\d.]+)\s+seconds")

sns.set(style="whitegrid")


def parse_filename(filename):
    match = FILENAME_REGEX.match(filename)
    return match.groupdict() if match else None


def parse_execution_time(file_path):
    max_ops = 0
    time_at_max_ops = 0.0
    with open(file_path, 'r') as f:
        for line in f:
            match = EXECUTION_LINE_REGEX.search(line)
            if match:
                ops = int(match.group(1))
                time = float(match.group(2))
                if ops > max_ops:
                    max_ops = ops
                    time_at_max_ops = time
    return max_ops, time_at_max_ops


def collect_data(directory):
    records = []
    for filename in os.listdir(directory):
        if filename.endswith(".log"):
            metadata = parse_filename(filename)
            if metadata:
                file_path = os.path.join(directory, filename)
                max_ops, time_taken = parse_execution_time(file_path)
                metadata.update({
                    'max_ops': max_ops,
                    'time_taken_seconds': time_taken
                })
                records.append(metadata)
    return pd.DataFrame(records)


def preprocess(df):
    # Convert to appropriate types
    df['insertedkeys'] = df['insertedkeys'].astype(int)
    df['totalops'] = df['totalops'].astype(int)
    df['nodes'] = df['nodes'].astype(int)
    df['max_ops'] = df['max_ops'].astype(int)
    df['time_taken_seconds'] = df['time_taken_seconds'].astype(float)
    return df


def plot_all(df):
    # 1. Improved: Compaction strategy impact across workloads (line graph)
    plt.figure(figsize=(12, 6))
    sns.lineplot(
        data=df,
        x="workload",
        y="time_taken_seconds",
        hue="strategy",
        marker="o",
        linewidth=2.5,
        markersize=8
    )
    plt.title("Impact of Compaction Strategy on Execution Time Across Workloads")
    plt.ylabel("Execution Time (s)")
    plt.xlabel("YCSB Workload")
    plt.legend(title="Compaction Strategy")
    plt.tight_layout()
    plt.savefig(PLOT_DIR + "a3.png")

    # # 2. Impact of workload on execution time
    # plt.figure(figsize=(10, 6))
    # sns.boxplot(data=df, x="workload", y="time_taken_seconds")
    # plt.title("Impact of Workload on Execution Time")
    # plt.ylabel("Execution Time (s)")
    # plt.xlabel("YCSB Workload")
    # plt.tight_layout()
    # plt.savefig(PLOT_DIR + "b3.png")

    # # 4. Impact of node count on execution time
    # plt.figure(figsize=(10, 6))
    # sns.boxplot(data=df, x="nodes", y="time_taken_seconds", hue="strategy")
    # plt.title("Impact of Node Count on Execution Time (per Strategy)")
    # plt.ylabel("Execution Time (s)")
    # plt.xlabel("Number of Nodes")
    # plt.tight_layout()
    # plt.savefig(PLOT_DIR + "d3.png")
    # 2. Workload Impact – Separate subplots per node count (with independent Y scales)
    node_counts = sorted(df['nodes'].unique())
    fig, axes = plt.subplots(1, len(node_counts), figsize=(18, 6), sharey=False)

    for i, node in enumerate(node_counts):
        subset = df[df['nodes'] == node]
        sns.boxplot(
            data=subset,
            x="workload",
            y="time_taken_seconds",
            ax=axes[i]
        )
        axes[i].set_title(f"{node} Nodes")
        axes[i].set_xlabel("Workload")
        axes[i].set_ylabel("Exec Time (s)")
        axes[i].tick_params(axis='x', rotation=45)
        axes[i].yaxis.set_major_locator(ticker.MaxNLocator(5))

    plt.suptitle("Impact of Workload on Execution Time (per Node Count)", fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(PLOT_DIR + "b3_workload_vs_nodes.png")
    

    # `4. Node Count Impact – Unified Lineplot with Strategy + Workload
    df["strategy_workload"] = df["strategy"] + "-" + df["workload"]

    plt.figure(figsize=(14, 7))
    sns.lineplot(
        data=df,
        x="nodes",
        y="time_taken_seconds",
        hue="strategy_workload",
        marker="o",
        linewidth=2.0,
        markersize=6
    )
    plt.title("Impact of Node Count on Execution Time (All Strategies and Workloads)")
    plt.ylabel("Execution Time (s)")
    plt.xlabel("Number of Nodes")
    plt.legend(title="Strategy-Workload", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xticks(sorted(df["nodes"].unique()))
    plt.tight_layout()
    plt.savefig(PLOT_DIR + "d3_nodes_vs_execution_combined.png")


def main():
    df = collect_data(LOG_DIR)
    if df.empty:
        print("No valid log files found.")
        return

    df = preprocess(df)
    print("Parsed Dataset:\n", df)
    plot_all(df)


if __name__ == "__main__":
    main()
