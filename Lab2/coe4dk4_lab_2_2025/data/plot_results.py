import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read the results
df = pd.read_csv('results.csv')

# Calculate averages across seeds for each P12
avg_data = df.groupby('p12').agg({
    'switch1_mean_delay': 'mean',
    'switch2_mean_delay': 'mean', 
    'switch3_mean_delay': 'mean'
}).reset_index()

# Create the plot
plt.figure(figsize=(12, 8))

# Plot each switch with different markers and colors
plt.plot(avg_data['p12'], avg_data['switch1_mean_delay'], 
         'o-', label='Switch 1', linewidth=2, markersize=8, color='blue')
plt.plot(avg_data['p12'], avg_data['switch2_mean_delay'], 
         's-', label='Switch 2', linewidth=2, markersize=8, color='red')
plt.plot(avg_data['p12'], avg_data['switch3_mean_delay'], 
         '^-', label='Switch 3', linewidth=2, markersize=8, color='green')

# Formatting
plt.xlabel('P₁₂', fontsize=12)
plt.ylabel('Mean Delay (ms)', fontsize=12)
plt.title('Mean Packet Delay vs P₁₂ for Three-Switch Network\n(λ₁=750, λ₂=500, λ₃=500 packets/sec)', fontsize=14)
plt.legend(fontsize=11, loc='best')
plt.grid(True, alpha=0.3)
plt.xlim(0.05, 0.95)
plt.ylim(1.0, 2.6)

# # Add annotations for key points
# plt.annotate('Minimum delay\n(balanced load)', 
#              xy=(0.5, avg_data[avg_data['p12']==0.5]['switch1_mean_delay'].iloc[0]), 
#              xytext=(0.5, 2.3), fontsize=10,
#              arrowprops=dict(arrowstyle='->', color='blue', alpha=0.7))

plt.tight_layout()
plt.show()

# Print summary statistics
print("Summary Statistics:")
print("=" * 50)
print(f"Switch 1 - Min delay: {avg_data['switch1_mean_delay'].min():.3f} ms at P12={avg_data.loc[avg_data['switch1_mean_delay'].idxmin(), 'p12']}")
print(f"Switch 2 - Delay range: {avg_data['switch2_mean_delay'].min():.3f} to {avg_data['switch2_mean_delay'].max():.3f} ms")
print(f"Switch 3 - Delay range: {avg_data['switch3_mean_delay'].min():.3f} to {avg_data['switch3_mean_delay'].max():.3f} ms")