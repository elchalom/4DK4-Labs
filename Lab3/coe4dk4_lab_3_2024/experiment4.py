import math

def factorial(n):
    if n <= 1:
        return 1
    result = 1
    for i in range(2, n+1):
        result *= i
    return result

def erlang_c(A, N):
    """
    Compute Erlang C probability of waiting (Pw).
    
    Pw = (A^N / N!) / [(A^N / N!) + (1 - rho) * sum(A^i / i!) for i=0..N-1]
    where rho = A/N
    """
    if N <= 0:
        raise ValueError("N must be positive")
    
    rho = A / N
    
    if rho >= 1.0:
        raise ValueError("System unstable: rho >= 1 (arrival rate >= service rate)")
    
    # Compute A^N / N!
    numerator = (A ** N) / factorial(N)
    
    # Compute sum(A^i / i!) for i=0..N-1
    sum_term = sum([(A ** i) / factorial(i) for i in range(N)])
    
    # Pw formula
    Pw = numerator / (numerator + (1 - rho) * sum_term)
    
    return Pw

def average_waiting_time(A, N, h):
    """
    Compute average waiting time Tw.
    
    Tw = Pw * h / [N * (1 - A/N)]
    """
    Pw = erlang_c(A, N)
    rho = A / N
    Tw = (Pw * h) / (N * (1 - rho))
    return Tw

def prob_wait_less_than_t(A, N, h, t):
    """
    Compute probability that wait time < t.
    
    W(t) = 1 - Pw * exp(-(N - A) * t / h)
    """
    Pw = erlang_c(A, N)
    W_t = 1 - Pw * math.exp(-(N - A) * t / h)
    return W_t

def main():
    print("Erlang C Calculator - Experiment 4")
    print("=" * 60)
    
    # Test cases (similar to reference group)
    test_cases = [
        {"lambda": 2, "h": 3, "N": 10, "name": "Case 1"},
        {"lambda": 2, "h": 5, "N": 15, "name": "Case 2"},
        {"lambda": 5, "h": 2, "N": 15, "name": "Case 3"},
    ]
    
    for case in test_cases:
        lam = case["lambda"]
        h = case["h"]
        N = case["N"]
        A = lam * h  # offered load
        
        print(f"\n{case['name']}: λ={lam}, h={h}, N={N}")
        print(f"  Offered load A = λ*h = {A:.2f} Erlangs")
        print(f"  Utilization ρ = A/N = {A/N:.4f}")
        
        try:
            Pw = erlang_c(A, N)
            Tw = average_waiting_time(A, N, h)
            W_1min = prob_wait_less_than_t(A, N, h, 1.0)
            
            print(f"  Pw (prob of waiting) = {Pw:.4f}")
            print(f"  Tw (avg wait time) = {Tw:.4f} minutes")
            print(f"  W(1 min) (prob wait < 1 min) = {W_1min:.4f}")
            
        except ValueError as e:
            print(f"  ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("Run your C simulation with these parameters and compare!")
    print("Update simparameters.h:")
    print("  - Set Call_ARRIVALRATE to λ (calls/minute)")
    print("  - Set MEAN_CALL_DURATION to h (minutes)")
    print("  - Set NUMBER_OF_CHANNELS to N")

if __name__ == '__main__':
    main()