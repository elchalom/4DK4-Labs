import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read the data
df = pd.read_csv('experiment5_data.csv')

# Create the plot
plt.figure(figsize=(10, 8))

# Plot for both 5 and 10 stations with clipping
plt.plot(df['arrival_rate'], df['stations_5'], 'o-', label='5 Stations', 
         linewidth=2, markersize=8, clip_on=True)
plt.plot(df['arrival_rate'], df['stations_10'], 's-', label='10 Stations', 
         linewidth=2, markersize=8, clip_on=True)

# Set x-axis to log scale
plt.xscale('log')

# Set axis limits with clipping at 40
plt.xlim(0.005, 0.5)
plt.ylim(0, 40)

# Labels and title
plt.xlabel('PACKET_ARRIVAL_RATE', fontsize=12)
plt.ylabel('Mean Delay', fontsize=12)
plt.title('Mean Delay vs. PACKET_ARRIVAL_RATE', fontsize=14)
plt.legend(fontsize=11)
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('experiment5_plot.png', dpi=300, bbox_inches='tight')
plt.show()

print("\n=== Experiment 5 Statistics ===")
print(f"\nArrival Rate Range: {df['arrival_rate'].min():.3f} - {df['arrival_rate'].max():.3f}")
print(f"\n10 Stations:")
print(f"  Min Delay: {df['stations_10'].min():.1f} at λ={df.loc[df['stations_10'].idxmin(), 'arrival_rate']:.2f}")
print(f"  Max Delay: {df['stations_10'].max():.1f} at λ={df.loc[df['stations_10'].idxmax(), 'arrival_rate']:.2f}")
print(f"  At λ=0.10: {df[df['arrival_rate']==0.10]['stations_10'].values[0]:.1f}")
print(f"  At λ=0.15: {df[df['arrival_rate']==0.15]['stations_10'].values[0]:.1f}")
print(f"  At λ=0.20: {df[df['arrival_rate']==0.20]['stations_10'].values[0]:.1f}")

print(f"\n5 Stations:")
print(f"  Min Delay: {df['stations_5'].min():.1f} at λ={df.loc[df['stations_5'].idxmin(), 'arrival_rate']:.2f}")
print(f"  Max Delay: {df['stations_5'].max():.1f} at λ={df.loc[df['stations_5'].idxmax(), 'arrival_rate']:.2f}")
print(f"  At λ=0.10: {df[df['arrival_rate']==0.10]['stations_5'].values[0]:.1f}")
print(f"  At λ=0.15: {df[df['arrival_rate']==0.15]['stations_5'].values[0]:.1f}")
print(f"  At λ=0.20: {df[df['arrival_rate']==0.20]['stations_5'].values[0]:.1f}")

print(f"\nExponential Growth Region (λ ≥ 0.15):")
print(f"  10 Stations: {df[df['arrival_rate']==0.15]['stations_10'].values[0]:.1f} → {df[df['arrival_rate']==0.25]['stations_10'].values[0]:.1f}")
print(f"  5 Stations: {df[df['arrival_rate']==0.15]['stations_5'].values[0]:.1f} → {df[df['arrival_rate']==0.25]['stations_5'].values[0]:.1f}")