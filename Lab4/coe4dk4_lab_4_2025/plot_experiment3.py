import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv('experiment3_data.csv', sep='\t')

# separate data for 10 and 5 stations
df_10 = df[df['num_stations'] == 10].sort_values('arrival_rate')
df_5 = df[df['num_stations'] == 5].sort_values('arrival_rate')

fig, ax = plt.subplots(1, 1, figsize=(10, 7))

ax.plot(df_10['arrival_rate'], df_10['mean_delay'], 
        marker='o', linewidth=2.5, markersize=7, label='10 Stations', 
        color='#2E86AB', clip_on=True)

ax.plot(df_5['arrival_rate'], df_5['mean_delay'], 
        marker='s', linewidth=2.5, markersize=7, label='5 Stations', 
        color='#A23B72', clip_on=True)

ax.set_xlabel('Arrival Rate', fontsize=13)
ax.set_ylabel('Mean Delay', fontsize=13)
ax.set_title('Mean Delay vs. Packet Arrival Rate\n(Binary Exponential Backoff)', 
             fontsize=15, fontweight='bold')
ax.grid(True, alpha=0.3, linestyle='--')
ax.legend(fontsize=12, loc='upper left')
ax.set_xlim(0, 0.20)
ax.set_ylim(0, 40)

plt.tight_layout()
plt.savefig('experiment3_results.png', dpi=300, bbox_inches='tight')
plt.show()

print("Plot saved as experiment3_results.png")

print("\n=== Binary Exponential Backoff Performance ===")
for num_stations in [10, 5]:
    subset = df[df['num_stations'] == num_stations]
    stable_data = subset[subset['mean_delay'] < 100]
    if len(stable_data) > 0:
        max_stable_rate = stable_data['arrival_rate'].max()
        max_delay_stable = stable_data['mean_delay'].max()
        print(f"\n{num_stations} Stations:")
        print(f"  Max stable arrival rate: {max_stable_rate:.2f}")
        print(f"  Max delay in stable region: {max_delay_stable:.1f}")

print("\n=== Points Beyond Y-axis Limit (delay > 40) ===")
high_delay = df[df['mean_delay'] > 40]
for _, row in high_delay.iterrows():
    print(f"N={int(row['num_stations'])}, λ={row['arrival_rate']:.2f}: "
          f"delay={row['mean_delay']:.1f}")