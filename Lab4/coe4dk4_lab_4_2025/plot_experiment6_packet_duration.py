import pandas as pd
import matplotlib.pyplot as plt

data = {
    'packet_duration': [0.1, 0.2, 0.5, 1, 2, 5, 8, 10, 12, 15, 18, 20],
    'mean_delay': [0.3, 0.4, 0.7, 1.2, 2.4, 6.8, 13.6, 20.2, 30.4, 60.4, 183.7, 6328.0]
}

df = pd.DataFrame(data)

plt.figure(figsize=(10, 6))
plt.plot(df['packet_duration'], df['mean_delay'], 'o-', linewidth=2, markersize=8)
plt.xlabel('MEAN_DATA_PACKET_DURATION', fontsize=12)
plt.ylabel('Mean Delay', fontsize=12)
plt.title('Mean Delay vs. MEAN_DATA_PACKET_DURATION', fontsize=14)
plt.xlim(0, 21)
plt.ylim(0, 400)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('experiment6_packet_duration.png', dpi=300)
plt.show()