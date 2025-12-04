from collections import deque
import heapq
import numpy as np
import matplotlib.pyplot as plt

# Event types
EVENT_PACKET_ARRIVAL = "PACKET_ARRIVAL"
EVENT_TOKEN_GENERATION = "TOKEN_GENERATION"

class Event:
    def __init__(self, time, event_type, data=None):
        self.time = time
        self.event_type = event_type
        self.data = data
    
    def __lt__(self, other):
        return self.time < other.time


class TokenBucketSimulator:
    def __init__(self, token_bucket_size, data_bucket_size, token_rate, 
                 arrival_rate, run_time, random_seed=None):
        """
        - token_bucket_size: max. number of tokens (Bt_max)
        - data_bucket_size: max. number of packets (Bd_max)
        - token_rate: rate of token generation (tokens/sec)
        - arrival_rate: packet arrival rate (packets/sec)
        - run_time: simulation duration (seconds)
        - random_seed: random seed for reproducibility
        """
        self.token_bucket_size = token_bucket_size  # Bt_max
        self.data_bucket_size = data_bucket_size    # Bd_max
        self.token_rate = token_rate                # tokens/sec
        self.arrival_rate = arrival_rate            # packets/sec
        self.run_time = run_time
        
        self.token_bucket = 0  # current number of tokens
        self.data_bucket = deque()  # queue of packets
        
        self.packets_arrived = 0
        self.packets_lost = 0
        self.packets_transmitted = 0
        self.current_time = 0
        self.last_stat_time = 0
        self.total_queue_time = 0
        
        self.event_queue = []
        
        if random_seed is not None:
            np.random.seed(random_seed)
    
    def schedule_event(self, event):
        """add event to priority queue"""
        heapq.heappush(self.event_queue, event)
    
    def generate_exponential(self, mean):
        """generate exponentially distributed r.v"""
        return np.random.exponential(mean)
    
    def packet_arrival_event(self):
        self.packets_arrived += 1
        
        # try adding packet to data bucket
        if len(self.data_bucket) < self.data_bucket_size:
            self.data_bucket.append(self.current_time)
            # try transmitting immediately
            self.try_transmit_packet()
        else:
            # data bucket full, drop packet
            self.packets_lost += 1
        
        # schedule next arrival
        next_arrival_time = self.current_time + self.generate_exponential(1.0 / self.arrival_rate)
        if next_arrival_time < self.run_time:
            self.schedule_event(Event(next_arrival_time, EVENT_PACKET_ARRIVAL))
    
    def token_generation_event(self):
        # add token to bucket if not full
        if self.token_bucket < self.token_bucket_size:
            self.token_bucket += 1
        
        # try to transmit packet
        self.try_transmit_packet()
        
        # schedule next token generation
        next_token_time = self.current_time + (1.0 / self.token_rate)
        if next_token_time < self.run_time:
            self.schedule_event(Event(next_token_time, EVENT_TOKEN_GENERATION))
    
    def try_transmit_packet(self):
        """try to transmit if both token and packet are available"""
        while len(self.data_bucket) > 0 and self.token_bucket > 0:
            # remove packet from data bucket and consume one token
            arrival_time = self.data_bucket.popleft()
            self.token_bucket -= 1
            self.packets_transmitted += 1
    
    def update_statistics(self):
        time_diff = self.current_time - self.last_stat_time
        self.total_queue_time += len(self.data_bucket) * time_diff
        self.last_stat_time = self.current_time
    
    def run(self):
        print(f"  Token bucket size: {self.token_bucket_size}, Data bucket size: {self.data_bucket_size}")
        print(f"  Token rate: {self.token_rate} tokens/sec, Arrival rate: {self.arrival_rate} pkt/sec")
        
        # schedule first packet arrival
        first_arrival = self.generate_exponential(1.0 / self.arrival_rate)
        self.schedule_event(Event(first_arrival, EVENT_PACKET_ARRIVAL))
        
        # schedule first token generation
        first_token = 1.0 / self.token_rate
        self.schedule_event(Event(first_token, EVENT_TOKEN_GENERATION))
        
        # events
        while self.event_queue:
            event = heapq.heappop(self.event_queue)
            
            if event.time > self.run_time:
                break
            
            self.update_statistics()
            self.current_time = event.time
            
            if event.event_type == EVENT_PACKET_ARRIVAL:
                self.packet_arrival_event()
            elif event.event_type == EVENT_TOKEN_GENERATION:
                self.token_generation_event()
        
        self.current_time = self.run_time
        self.update_statistics()
        
        print(f"  Packets arrived: {self.packets_arrived}, transmitted: {self.packets_transmitted}, lost: {self.packets_lost}")
    
    def get_results(self):
        loss_rate = self.packets_lost / self.packets_arrived if self.packets_arrived > 0 else 0
        mean_output_rate = self.packets_transmitted / self.run_time
        avg_queue_length = self.total_queue_time / self.run_time
        
        return {
            'token_bucket_size': self.token_bucket_size,
            'data_bucket_size': self.data_bucket_size,
            'packets_arrived': self.packets_arrived,
            'packets_transmitted': self.packets_transmitted,
            'packets_lost': self.packets_lost,
            'loss_rate': loss_rate,
            'mean_output_rate': mean_output_rate,
            'avg_queue_length': avg_queue_length
        }
    
    def print_results(self):
        """Print simulation results"""
        results = self.get_results()
        
        print("\n")
        print("SIMULATION RESULTS")
        print("\n")
        print(f"Token bucket size:      {results['token_bucket_size']}")
        print(f"Data bucket size:       {results['data_bucket_size']}")
        print(f"Packets arrived:        {results['packets_arrived']}")
        print(f"Packets transmitted:    {results['packets_transmitted']}")
        print(f"Packets lost:           {results['packets_lost']}")
        print(f"Loss rate:              {results['loss_rate']:.6f} ({results['loss_rate']*100:.2f}%)")
        print(f"Mean output rate:       {results['mean_output_rate']:.2f} packets/sec")
        print(f"Average queue length:   {results['avg_queue_length']:.2f} packets")
        print("\n")


def vary_token_bucket_size():
    """
    Part 3a Experiment 1: Vary token bucket size Bt_max
    Fixed: Bd_max = 20, token_rate = 100 tokens/sec, arrival_rate = 100 pkt/sec
    """
    print("\n")
    print("PART 3a - EXPERIMENT 1: VARYING TOKEN BUCKET SIZE (Bt_max)")
    print("\n")
    
    # fixed parameters
    data_bucket_size = 20
    token_rate = 100  # tokens/sec
    arrival_rate = 100  # packets/sec
    run_time = 1000
    
    token_bucket_sizes = range(1, 51, 2)
    
    results = []
    
    for Bt in token_bucket_sizes:
        print(f"\nRunning with Bt_max = {Bt}...")
        sim = TokenBucketSimulator(
            token_bucket_size=Bt,
            data_bucket_size=data_bucket_size,
            token_rate=token_rate,
            arrival_rate=arrival_rate,
            run_time=run_time,
            random_seed=400430923
        )
        sim.run()
        results.append(sim.get_results())
    
    # plots
    bt_sizes = [r['token_bucket_size'] for r in results]
    loss_rates = [r['loss_rate'] for r in results]
    output_rates = [r['mean_output_rate'] for r in results]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # loss rate
    ax1.plot(bt_sizes, loss_rates, 'bo-', linewidth=2, markersize=6)
    ax1.set_xlabel('Token Bucket Size Bt_max (tokens)', fontsize=12)
    ax1.set_ylabel('Packet Loss Rate', fontsize=12)
    ax1.set_title('Loss Rate vs Token Bucket Size\n(Bd_max=20, R=100 tokens/s, λ=100 pkt/s)', fontsize=13)
    ax1.grid(True, alpha=0.3)
    
    # output rate
    ax2.plot(bt_sizes, output_rates, 'ro-', linewidth=2, markersize=6)
    ax2.axhline(y=arrival_rate, color='g', linestyle='--', linewidth=2, 
                label=f'Arrival rate = {arrival_rate} pkt/s')
    ax2.axhline(y=token_rate, color='b', linestyle='--', linewidth=2, 
                label=f'Token rate = {token_rate} tokens/s')
    ax2.set_xlabel('Token Bucket Size Bt_max (tokens)', fontsize=12)
    ax2.set_ylabel('Mean Output Rate (packets/sec)', fontsize=12)
    ax2.set_title('Output Rate vs Token Bucket Size\n(Bd_max=20, R=100 tokens/s, λ=100 pkt/s)', fontsize=13)
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('lab5_part3a1_token_bucket_size.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("\nPlot saved as 'lab5_part3a1_token_bucket_size.png'")
    return results


def vary_data_bucket_size():
    """
    Part 3a Experiment 2: Vary data bucket size Bd_max
    Fixed: Bt_max = 20, token_rate = 100 tokens/sec, arrival_rate = 100 pkt/sec
    """
    print("\n")
    print("PART 3a - EXPERIMENT 2: VARYING DATA BUCKET SIZE (Bd_max)")
    print("\n")
    
    # fixed parameters
    token_bucket_size = 20
    token_rate = 100  # tokens/sec
    arrival_rate = 100  # packets/sec
    run_time = 1000
    
    data_bucket_sizes = range(1, 51, 2)
    
    results = []
    
    for Bd in data_bucket_sizes:
        print(f"\nRunning with Bd_max = {Bd}...")
        sim = TokenBucketSimulator(
            token_bucket_size=token_bucket_size,
            data_bucket_size=Bd,
            token_rate=token_rate,
            arrival_rate=arrival_rate,
            run_time=run_time,
            random_seed=42
        )
        sim.run()
        results.append(sim.get_results())
    
    # plots
    bd_sizes = [r['data_bucket_size'] for r in results]
    loss_rates = [r['loss_rate'] for r in results]
    output_rates = [r['mean_output_rate'] for r in results]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # loss rate
    ax1.plot(bd_sizes, loss_rates, 'bo-', linewidth=2, markersize=6)
    ax1.set_xlabel('Data Bucket Size Bd_max (packets)', fontsize=12)
    ax1.set_ylabel('Packet Loss Rate', fontsize=12)
    ax1.set_title('Loss Rate vs Data Bucket Size\n(Bt_max=20, R=100 tokens/s, λ=100 pkt/s)', fontsize=13)
    ax1.grid(True, alpha=0.3)
    
    # output rate
    ax2.plot(bd_sizes, output_rates, 'ro-', linewidth=2, markersize=6)
    ax2.axhline(y=arrival_rate, color='g', linestyle='--', linewidth=2, 
                label=f'Arrival rate = {arrival_rate} pkt/s')
    ax2.axhline(y=token_rate, color='b', linestyle='--', linewidth=2, 
                label=f'Token rate = {token_rate} tokens/s')
    ax2.set_xlabel('Data Bucket Size Bd_max (packets)', fontsize=12)
    ax2.set_ylabel('Mean Output Rate (packets/sec)', fontsize=12)
    ax2.set_title('Output Rate vs Data Bucket Size\n(Bt_max=20, R=100 tokens/s, λ=100 pkt/s)', fontsize=13)
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('lab5_part3a2_data_bucket_size.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("\nPlot saved as 'lab5_part3a2_data_bucket_size.png'")
    return results


def vary_both_bucket_sizes():
    """
    Part 3a Experiment 3: Vary both bucket sizes equally (Bt_max = Bd_max = B)
    Fixed: token_rate = 100 tokens/sec, arrival_rate = 100 pkt/sec
    """
    print("\n")
    print("PART 3a - EXPERIMENT 3: VARYING BOTH BUCKET SIZES (Bt_max = Bd_max)")
    print("\n")
    
    # fixed parameters
    token_rate = 100  # tokens/sec
    arrival_rate = 100  # packets/sec
    run_time = 1000
    
    # vary both bucket sizes equally
    bucket_sizes = range(1, 51, 2)
    
    results = []
    
    for B in bucket_sizes:
        print(f"\nRunning with Bt_max = Bd_max = {B}...")
        sim = TokenBucketSimulator(
            token_bucket_size=B,
            data_bucket_size=B,
            token_rate=token_rate,
            arrival_rate=arrival_rate,
            run_time=run_time,
            random_seed=42
        )
        sim.run()
        results.append(sim.get_results())
    
    # plots
    b_sizes = [r['token_bucket_size'] for r in results]
    loss_rates = [r['loss_rate'] for r in results]
    output_rates = [r['mean_output_rate'] for r in results]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # loss rate
    ax1.plot(b_sizes, loss_rates, 'bo-', linewidth=2, markersize=6)
    ax1.set_xlabel('Bucket Size B (Bt_max = Bd_max)', fontsize=12)
    ax1.set_ylabel('Packet Loss Rate', fontsize=12)
    ax1.set_title('Loss Rate vs Bucket Size\n(Bt_max=Bd_max, R=100 tokens/s, λ=100 pkt/s)', fontsize=13)
    ax1.grid(True, alpha=0.3)
    
    # output rate
    ax2.plot(b_sizes, output_rates, 'ro-', linewidth=2, markersize=6)
    ax2.axhline(y=arrival_rate, color='g', linestyle='--', linewidth=2, 
                label=f'Arrival rate = {arrival_rate} pkt/s')
    ax2.axhline(y=token_rate, color='b', linestyle='--', linewidth=2, 
                label=f'Token rate = {token_rate} tokens/s')
    ax2.set_xlabel('Bucket Size B (Bt_max = Bd_max)', fontsize=12)
    ax2.set_ylabel('Mean Output Rate (packets/sec)', fontsize=12)
    ax2.set_title('Output Rate vs Bucket Size\n(Bt_max=Bd_max, R=100 tokens/s, λ=100 pkt/s)', fontsize=13)
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('lab5_part3a3_both_bucket_sizes.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("\nPlot saved as 'lab5_part3a3_both_bucket_sizes.png'")
    return results


if __name__ == "__main__":
    print("\n")
    print("LAB 5 - PART 3a: TOKEN BUCKET (FIXED PACKET SIZE)")
    print("\n")
    
    results1 = vary_token_bucket_size()
    results2 = vary_data_bucket_size()
    results3 = vary_both_bucket_sizes()
    
    print("\n")
    print("ALL PART 3a EXPERIMENTS COMPLETE!")
    print("Generated files:")
    print("  - lab5_part3a1_token_bucket_size.png")
    print("  - lab5_part3a2_data_bucket_size.png")
    print("  - lab5_part3a3_both_bucket_sizes.png")
    print("\n")