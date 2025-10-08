import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read the data
df = pd.read_csv('results.csv')

# Calculate mean delays for each arrival rate
voice_means = df.groupby('data_arrival_rate')['voice_mean_delay'].mean()
data_means = df.groupby('data_arrival_rate')['data_mean_delay'].mean()
voice_std = df.groupby('data_arrival_rate')['voice_mean_delay'].std()
data_std = df.groupby('data_arrival_rate')['data_mean_delay'].std()

arrival_rates = voice_means.index

# Plot 1: Combined voice and data delays
plt.figure(figsize=(10, 6))
plt.plot(arrival_rates, voice_means, marker='o', 
         label='Voice Packets', linewidth=2)
plt.plot(arrival_rates, data_means, marker='s', 
         label='Data Packets', linewidth=2)
plt.xlabel('Data Arrival Rate (packets/sec)')
plt.ylabel('Mean Delay (ms)')
plt.title('Part 7: Priority Scheduling - Voice vs Data Packet Delays')
plt.legend()
plt.grid(True, alpha=0.3)
plt.xlim(0.5, 15.5)
plt.yscale('log')
plt.tight_layout()
plt.savefig('part7_combined_delays.png', dpi=300, bbox_inches='tight')
plt.show()

# Plot 2: Voice packets only (linear scale)
plt.figure(figsize=(10, 6))
plt.plot(arrival_rates, voice_means, marker='o', 
         color='blue', linewidth=2)
plt.xlabel('Data Arrival Rate (packets/sec)')
plt.ylabel('Voice Packet Mean Delay (ms)')
plt.title('Part 7: Priority Scheduling - Voice Packet Delay (Linear Scale)')
plt.grid(True, alpha=0.3)
plt.xlim(0.5, 15.5)
plt.ylim(40, 90)
plt.tight_layout()
plt.savefig('part7_voice_linear.png', dpi=300, bbox_inches='tight')
plt.show()

# Print summary statistics
print("Part 7 Priority Scheduling Results Summary:")
print("=" * 50)
print(f"Voice delay range: {voice_means.min():.1f} - {voice_means.max():.1f} ms")
print(f"Data delay range: {data_means.min():.1f} - {data_means.max():.1f} ms")
print(f"Voice delay growth factor: {voice_means.max()/voice_means.min():.1f}x")
print(f"Data delay growth factor: {data_means.max()/data_means.min():.1f}x")