import pandas as pd
import matplotlib.pyplot as plt

data = {
    'arrival_rate': [0.001, 0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
    'mean_delay': [1.1, 1.2, 1.2, 1.3, 1.4, 1.6, 1.9, 2.2, 2.8, 3.6, 5.6, 10.7]
}

df = pd.DataFrame(data)

plt.figure(figsize=(10, 6))
plt.plot(df['arrival_rate'], df['mean_delay'], 'o-', linewidth=2, markersize=8)
plt.xscale('log')
plt.xlabel('PACKET_ARRIVAL_RATE', fontsize=12)
plt.ylabel('Mean Delay', fontsize=12)
plt.title('Mean Delay vs. PACKET_ARRIVAL_RATE', fontsize=14)
plt.xlim(0.0005, 1.0)
plt.ylim(0, 20)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('experiment6_arrival_rate.png', dpi=300)
plt.show()