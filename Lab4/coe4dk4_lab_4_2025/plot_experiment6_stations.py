import pandas as pd
import matplotlib.pyplot as plt

data = {
    'num_stations': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
    'mean_delay': [1.2, 1.2, 1.2, 1.2, 1.2, 1.2, 1.2, 1.2, 1.2, 1.2, 1.2, 1.2, 1.2, 1.2, 1.2]
}

df = pd.DataFrame(data)

plt.figure(figsize=(10, 6))
plt.plot(df['num_stations'], df['mean_delay'], 'o-', linewidth=2, markersize=8)
plt.xlabel('NUMBER_OF_STATIONS', fontsize=12)
plt.ylabel('Mean Delay', fontsize=12)
plt.title('Mean Delay vs. NUMBER_OF_STATIONS', fontsize=14)
plt.ylim(0, 2)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('experiment6_stations.png', dpi=300)
plt.show()

print(f"Mean delay range: {df['mean_delay'].min():.1f} - {df['mean_delay'].max():.1f}")