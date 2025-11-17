import pandas as pd
import matplotlib.pyplot as plt


data = {
    'x_xr_ratio': [1, 2, 3, 5, 10, 15, 16, 18, 20, 22, 24, 26, 28, 30],
    'capacity': [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.499865, 0.49886, 0.453555, 0.416635, 0.38433, 0.357635, 0.333695]
}

df = pd.DataFrame(data)

plt.figure(figsize=(10, 6))
plt.plot(df['x_xr_ratio'], df['capacity'], 'o-', linewidth=2, markersize=8)
plt.xlabel('X/Xr', fontsize=12)
plt.ylabel('Capacity', fontsize=12)
plt.title('Capacity vs. X/Xr', fontsize=14)
plt.xlim(0, 31)
plt.ylim(0, 0.6)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('experiment6_capacity.png', dpi=300)
plt.show()

print(f"\nCapacity Analysis:")
print(f"Peak capacity: {df['capacity'].max():.3f} at X/Xr = {df.loc[df['capacity'].idxmax(), 'x_xr_ratio']:.0f}")
print(f"Capacity at X/Xr=30: {df[df['x_xr_ratio']==30]['capacity'].values[0]:.3f}")