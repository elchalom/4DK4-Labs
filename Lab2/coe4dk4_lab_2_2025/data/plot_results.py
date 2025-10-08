import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read the results
df = pd.read_csv('results.csv')

# Calculate total arrival rate (data + voice)
df['total_arrival_rate'] = df['data_arrival_rate'] + 10  # 10 packets/sec voice

# Calculate averages across seeds for each total arrival rate
avg_data = df.groupby('total_arrival_rate').agg({
    'voice_mean_delay': 'mean',
    'data_mean_delay': 'mean'
}).reset_index()

# Create the plot
plt.figure(figsize=(12, 8))

# Plot both packet types
plt.plot(avg_data['total_arrival_rate'], avg_data['voice_mean_delay'], 
         's-', label='Voice Packet', linewidth=2, markersize=8, color='red')
plt.plot(avg_data['total_arrival_rate'], avg_data['data_mean_delay'], 
         'o-', label='Data Packet', linewidth=2, markersize=8, color='blue')

# Formatting
plt.xlabel('MEAN_ARRIVAL_RATE', fontsize=12)
plt.ylabel('Mean Delay (msec)', fontsize=12)
plt.title('Mean Delay vs. MEAN_ARRIVAL_RATE', fontsize=14)
plt.legend(fontsize=11, loc='upper left')
plt.grid(True, alpha=0.3)
plt.xlim(10, 26)
plt.ylim(0, max(avg_data['data_mean_delay'].max(), avg_data['voice_mean_delay'].max()) * 1.1)

plt.tight_layout()
plt.show()

# Print summary
print("Summary Statistics:")
print("=" * 50)
print(f"Voice delay range: {avg_data['voice_mean_delay'].min():.1f} - {avg_data['voice_mean_delay'].max():.1f} ms")
print(f"Data delay range: {avg_data['data_mean_delay'].min():.1f} - {avg_data['data_mean_delay'].max():.1f} ms")
print(f"Total arrival rate range: {avg_data['total_arrival_rate'].min()} - {avg_data['total_arrival_rate'].max()} packets/sec")