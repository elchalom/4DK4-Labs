import pandas as pd
import matplotlib.pyplot as plt

data = {
    'slot_duration': [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0],
    'mean_delay': [1.2, 1.4, 1.5, 1.7, 2.0, 2.2, 2.7, 3.5, 4.3, 5.0, 7.3, 11.6, 16.1]
}

df = pd.DataFrame(data)

plt.figure(figsize=(10, 6))
plt.plot(df['slot_duration'], df['mean_delay'], 'o-', linewidth=2, markersize=8)
plt.xlabel('SLOT_DURATION', fontsize=12)
plt.ylabel('Mean Delay', fontsize=12)
plt.title('Mean Delay vs. SLOT_DURATION', fontsize=14)
plt.xlim(0, 2.1)
plt.ylim(0, 15)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('experiment6_slot_duration.png', dpi=300)
plt.show()