import pandas as pd
import matplotlib.pyplot as plt
import os

def visualize():
    if not os.path.exists("centralized_network_log.csv"):
        print("No data yet!")
        return
    df = pd.read_csv("centralized_network_log.csv")
    plt.figure(figsize=(10, 5))
    for cid, group in df.groupby("Client_ID"):
        plt.plot(group["Timestamp"], group["Speed_Mbps"], marker='o', label=cid)
    plt.title("Network Comparison (3 Laptops)")
    plt.ylabel("Mbps")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    visualize()
