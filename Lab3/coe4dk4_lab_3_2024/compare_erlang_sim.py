

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Files
erlang_file = 'erlangb_results.csv'
sim_file = 'simulation_sweep_results.csv'

# Read files
erlang_df = pd.read_csv(erlang_file, index_col='N_channels')
# sim CSV columns: A,N,seed,blocked,arrivals,PB
sim_df = pd.read_csv(sim_file)

# Pivot sim_df to get PB for each (N, A)
sim_pivot = sim_df.pivot_table(index='N', columns='A', values='PB')

# Choose A values to plot (use the same as erlang_df columns)
A_cols = erlang_df.columns.tolist()
A_values = [int(col.split('=')[1]) for col in A_cols]

plt.figure(figsize=(10, 7))
for col in erlang_df.columns:
    plt.plot(erlang_df.index, erlang_df[col], linestyle='-', marker='o', markersize=4, label=f'{col} (theory)')

# Overlay simulation points with 'x' markers
for A in A_values:
    if A in sim_pivot.columns:
        plt.plot(sim_pivot.index, sim_pivot[A], linestyle='None', marker='x', markersize=6, label=f'A={A} (sim)')

plt.yscale('log')
plt.ylim(1e-4, 1)
plt.xlim(1, erlang_df.index.max())
plt.xticks(np.arange(1, erlang_df.index.max()+1, 1))
plt.xlabel('Number of Channels (N)')
plt.ylabel('Blocking Probability $P_B$')
plt.title('Erlang B Theory vs Simulation')
plt.grid(True, which='both', linestyle='--', alpha=0.4)
plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.25), ncol=3, fontsize='small')
plt.tight_layout()
plt.savefig('erlang_vs_sim.png', dpi=300, bbox_inches='tight')
plt.show()

print('Saved erlang_vs_sim.png')
