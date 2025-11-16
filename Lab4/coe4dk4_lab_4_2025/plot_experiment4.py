import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv('experiment4_data.csv', sep='\t')

df_10 = df[df['num_stations'] == 10].sort_values('arrival_rate')
df_5 = df[df['num_stations'] == 5].sort_values('arrival_rate')

# df_10 = df_10[df_10['arrival_rate'] <= 1]
# df_5 = df_5[df_5['arrival_rate'] <= 1]

fig, ax = plt.subplots(1, 1, figsize=(10, 7))

ax.plot(df_5['arrival_rate'], df_5['other_stations_delay'], 
        marker='o', linewidth=2.5, markersize=7, 
        label='5 Stations (Excluding Station 0)', 
        color='#1f77b4', clip_on=True)

ax.plot(df_5['arrival_rate'], df_5['station0_delay'], 
        marker='s', linewidth=2.5, markersize=7, 
        label='5 Stations (Only Station 0)', 
        color='#ff7f0e', clip_on=True)

ax.plot(df_10['arrival_rate'], df_10['other_stations_delay'], 
        marker='D', linewidth=2.5, markersize=7, 
        label='10 Stations (Excluding Station 0)', 
        color='#2ca02c', clip_on=True)

ax.plot(df_10['arrival_rate'], df_10['station0_delay'], 
        marker='^', linewidth=2.5, markersize=7, 
        label='10 Stations (Only Station 0)', 
        color='#d62728', clip_on=True)

ax.set_xscale('log')
ax.set_xlabel('Arrival Rate', fontsize=13)
ax.set_ylabel('Mean Delay', fontsize=13)
ax.set_title('Mean Delay vs. Packet Arrival Rate\n(Station 0 Persists, Others Use Binary Exp. Backoff)', 
             fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3, linestyle='--', which='both')
ax.legend(fontsize=11, loc='upper left')
ax.set_xlim(1e-2, 0.5)
ax.set_ylim(0, 40)

plt.tight_layout()
plt.savefig('experiment4_results.png', dpi=300, bbox_inches='tight')
plt.show()

print("Plot saved as experiment4_results.png")

print("\n=== Station 0 (Persisting) vs Other Stations ===")
key_rates = [0.05, 0.1, 0.12, 0.15, 0.18]
for num_stations in [10, 5]:
    subset = df[df['num_stations'] == num_stations]
    print(f"\n{num_stations} Stations:")
    for rate in key_rates:
        row = subset[subset['arrival_rate'] == rate]
        if not row.empty:
            st0 = row['station0_delay'].values[0]
            others = row['other_stations_delay'].values[0]
            if others < 1000:
                advantage = ((others - st0) / others) * 100 if others > 0 else 0
                print(f"  λ={rate:.2f}: Station 0={st0:.1f}, Others={others:.1f}, "
                      f"Advantage={advantage:.1f}%")

print("\n=== Points Beyond Y-axis Limit (delay > 40) ===")
high_delay = df[df['other_stations_delay'] > 40]
for _, row in high_delay.iterrows():
    print(f"N={int(row['num_stations'])}, λ={row['arrival_rate']:.2f}: "
          f"Station 0={row['station0_delay']:.1f}, Others={row['other_stations_delay']:.1f}")