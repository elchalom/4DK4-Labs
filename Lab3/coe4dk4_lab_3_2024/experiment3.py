import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def erlang_b(A, N):
    """
      B(0) = 1
      B(n) = (A * B(n-1)) / (n + A * B(n-1))
    """
    if N < 0:
        raise ValueError("N must be non-negative")
    B = 1.0
    for n in range(1, N + 1):
        B = (A * B) / (n + A * B)
    return B


def find_max_load_for_target_pb(N, target_pb=0.015, tol=1e-6):
    """Binary search to find maximum A such that erlang_b(A, N) <= target_pb.
    """
    A_low = 0.0
    A_high = N * 2.0  # heuristic
    
    # safety check
    if erlang_b(A_low, N) > target_pb:
        return 0.0
    
    # Binary search
    while (A_high - A_low) > tol:
        A_mid = (A_low + A_high) / 2.0
        pb_mid = erlang_b(A_mid, N)
        
        if pb_mid <= target_pb:
            A_low = A_mid  # can increase load
        else:
            A_high = A_mid  # must decrease load
    
    return A_low


def main():
    target_pb = 0.015  # 1.5% blocking probability
    N_min = 1
    N_max = 40
    
    results = []
    
    print(f"Finding maximum offered load for PB <= {target_pb*100:.1f}%")
    print("=" * 60)
    
    for N in range(N_min, N_max + 1):
        max_A = find_max_load_for_target_pb(N, target_pb=target_pb)
        pb_check = erlang_b(max_A, N)
        results.append({'N_channels': N, 'Max_Offered_Load_Erlangs': max_A, 'PB_check': pb_check})
        print(f"N={N:2d} channels -> Max A = {max_A:6.3f} Erlangs (PB = {pb_check:.6f})")
    
    # Convert to DataFrame
    df = pd.DataFrame(results)
    df.to_csv('experiment3_results.csv', index=False)
    print(f"\nSaved experiment3_results.csv")
    
    # Plot
    plt.figure(figsize=(10, 7))
    plt.plot(df['N_channels'], df['Max_Offered_Load_Erlangs'], 
             marker='o', linewidth=2, markersize=6, color='blue')
    plt.xlabel('Number of Cellular Channels')
    plt.ylabel('Maximum Offered Loading (Erlangs)')
    plt.title('Maximum Offered Loading vs. Number of Cellular Channels\n(for 1.5% Blocking Probability)')
    plt.grid(True, alpha=0.3)
    plt.xlim(N_min - 1, N_max + 1)
    plt.ylim(0, df['Max_Offered_Load_Erlangs'].max() * 1.05)
    plt.tight_layout()
    plt.savefig('experiment3_plot.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"Saved experiment3_plot.png")
    
    # Print key observations
    print("\n" + "=" * 60)
    print("KEY OBSERVATIONS:")
    print("=" * 60)
    min_channels_needed = df[df['Max_Offered_Load_Erlangs'] >= 1.0]['N_channels'].min()
    print(f"Minimum channels for A >= 1 Erlang at PB=1.5%: N = {min_channels_needed}")
    print(f"At N=40 channels: Max load = {df.iloc[-1]['Max_Offered_Load_Erlangs']:.2f} Erlangs")


if __name__ == '__main__':
    main()