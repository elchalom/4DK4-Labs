import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def erlang_b(A, N):
    """Compute Erlang-B blocking probability for offered load A and N channels.

    Uses a stable recursive relation:
      B(0) = 1
      B(n) = (A * B(n-1)) / (n + A * B(n-1))
    """
    if N < 0:
        raise ValueError("N must be non-negative")
    # iterative
    B = 1.0
    for n in range(1, N + 1):
        B = (A * B) / (n + A * B)
    return B


def compute_grid(A_values, N_max):
    """Return DataFrame with index N=1..N_max and columns for each A in A_values."""
    data = {}
    N_range = np.arange(1, N_max + 1)
    for A in A_values:
        PBs = [erlang_b(float(A), int(N)) for N in N_range]
        data[f'A={A}'] = PBs
    df = pd.DataFrame(data, index=N_range)
    df.index.name = 'N_channels'
    return df


def plot_erlangb(df, out_png='erlangb_plot.png'):
    plt.figure(figsize=(10, 7))

    # Plot each column (each A)
    for col in df.columns:
        # extract numeric A for label ordering if needed
        plt.plot(df.index, df[col], marker='o', linewidth=1.5, markersize=4, label=col)

    plt.yscale('log')
    plt.xlabel('Number of Channels (N)')
    plt.ylabel('Blocking Probability $P_B$')
    plt.title('Blocking Probability vs Number of Channels for Various Offered Loads (Erlang B)')
    plt.grid(True, which='both', linestyle='--', alpha=0.4)
    plt.xlim(1 - 0.5, df.index.max() + 0.5)
    # x-axis ticks at every integer
    plt.xticks(np.arange(1, int(df.index.max()) + 1, 1))
    # limit y-axis to [1e-4, 1]
    plt.ylim(1e-4, 1)

    # Legend placed below
    plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.25), ncol=5, fontsize='small')
    plt.tight_layout()
    plt.savefig(out_png, dpi=300, bbox_inches='tight')
    plt.show()


def main():
    # Default ranges used in the reference report
    A_values = list(range(1, 21))  # offered load in Erlangs
    N_max = 20

    df = compute_grid(A_values, N_max)

    # Save CSV (rows are N, columns are A)
    df.to_csv('erlangb_results.csv')
    print('Saved erlangb_results.csv (rows: N_channels, columns: A=... )')

    # Quick numeric check from the report: A=5, N=10 should be around 0.184
    pb_5_10 = erlang_b(5.0, 10)
    print(f'Check: PB(A=5,N=10) = {pb_5_10:.6f}')

    # Plot
    plot_erlangb(df, out_png='erlangb_plot.png')


if __name__ == '__main__':
    main()
