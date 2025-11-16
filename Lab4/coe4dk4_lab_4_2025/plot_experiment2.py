import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv('experiment2_data.csv', sep='\t')

# separate data for 10 and 5 stations
df_10 = df[df['num_stations'] == 10]
df_5 = df[df['num_stations'] == 5]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

for backoff in [5, 10, 20]:
    data = df_10[df_10['backoff_duration'] == backoff].copy()
    data_sorted = data.sort_values('arrival_rate')
    
    # clipping display at y=40
    ax1.plot(data_sorted['arrival_rate'], data_sorted['mean_delay'], 
             marker='o', linewidth=2, markersize=6, label=f'B = {backoff}',
             clip_on=True)

ax1.set_xlabel('Arrival Rate', fontsize=12)
ax1.set_ylabel('Mean Delay', fontsize=12)
ax1.set_title('Mean Delay vs. Packet Arrival Rate\n(10 Stations)', fontsize=14, fontweight='bold')
ax1.grid(True, alpha=0.3, linestyle='--')
ax1.legend(fontsize=11)
ax1.set_xlim(left=0)
ax1.set_ylim(0, 40)

for backoff in [3, 5, 7]:
    data = df_5[df_5['backoff_duration'] == backoff].copy()
    data_sorted = data.sort_values('arrival_rate')
    
    # clipping display at y=40
    ax2.plot(data_sorted['arrival_rate'], data_sorted['mean_delay'], 
             marker='s', linewidth=2, markersize=6, label=f'B = {backoff}',
             clip_on=True)

ax2.set_xlabel('Arrival Rate', fontsize=12)
ax2.set_ylabel('Mean Delay', fontsize=12)
ax2.set_title('Mean Delay vs. Packet Arrival Rate\n(5 Stations)', fontsize=14, fontweight='bold')
ax2.grid(True, alpha=0.3, linestyle='--')
ax2.legend(fontsize=11)
ax2.set_xlim(left=0)
ax2.set_ylim(0, 40)

plt.tight_layout()
plt.savefig('experiment2_results.png', dpi=300, bbox_inches='tight')
plt.show()

print("Plot saved as experiment2_results.png")

print("\n=== Summary Statistics ===")
for num_stations in [10, 5]:
    print(f"\n{num_stations} Stations:")
    subset = df[df['num_stations'] == num_stations]
    for backoff in sorted(subset['backoff_duration'].unique()):
        data = subset[subset['backoff_duration'] == backoff]
        stable_data = data[data['mean_delay'] < 100]
        if len(stable_data) > 0:
            max_stable_rate = stable_data['arrival_rate'].max()
            print(f"  B={backoff}: Max stable arrival rate ≈ {max_stable_rate:.2f}")
        else:
            print(f"  B={backoff}: No stable region found")

print("\n=== Points Beyond Y-axis Limit (delay > 40) ===")
high_delay = df[df['mean_delay'] > 40]
for _, row in high_delay.iterrows():
    print(f"N={int(row['num_stations'])}, B={int(row['backoff_duration'])}, "
          f"λ={row['arrival_rate']:.2f}: delay={row['mean_delay']:.1f}")