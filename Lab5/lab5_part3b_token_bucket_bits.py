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


class Packet:
    def __init__(self, arrival_time, size):
        self.arrival_time = arrival_time
        self.size = size  # in bits


class BitCountingTokenBucket:
    def __init__(self, token_bucket_size, data_bucket_size, token_rate, 
                 arrival_rate, packet_sizes, run_time, random_seed=None):
        """
        - token_bucket_size: Maximum number of tokens in bits (Bt_max)
        - data_bucket_size: Maximum number of packets (Bd_max)
        - token_rate: Rate of token generation (bits/sec)
        - arrival_rate: Packet arrival rate (packets/sec)
        - packet_sizes: List of possible packet sizes in bits
        - run_time: Simulation duration (seconds)
        - random_seed: Random seed for reproducibility
        """
        self.token_bucket_size = token_bucket_size  # Bt_max in bits
        self.data_bucket_size = data_bucket_size    # Bd_max in packets
        self.token_rate = token_rate                # bits/sec
        self.arrival_rate = arrival_rate            # packets/sec
        self.packet_sizes = packet_sizes
        self.run_time = run_time
        
        self.token_bucket = 0.0  # current number of tokens (bits)
        self.data_bucket = deque()  # queue of Packet objects
        self.last_token_update = 0.0  # last time tokens were updated
        
        self.packets_arrived = 0
        self.packets_lost = 0
        self.packets_transmitted = 0
        self.bits_transmitted = 0
        self.current_time = 0
        self.last_stat_time = 0
        self.total_queue_time = 0
        
        self.event_queue = []
        
        if random_seed is not None:
            np.random.seed(random_seed)
    
    def schedule_event(self, event):
        """add event to the priority queue"""
        heapq.heappush(self.event_queue, event)
    
    def generate_exponential(self, mean):
        """generate exponentially distributed r.v"""
        return np.random.exponential(mean)
    
    def generate_packet_size(self):
        return np.random.choice(self.packet_sizes)
    
    def update_tokens(self, current_time):
        time_diff = current_time - self.last_token_update
        tokens_to_add = time_diff * self.token_rate
        
        self.token_bucket = min(self.token_bucket + tokens_to_add, self.token_bucket_size)
        self.last_token_update = current_time
    
    def packet_arrival_event(self):
        self.packets_arrived += 1
        packet_size = self.generate_packet_size()
        
        self.update_tokens(self.current_time)
        
        # try to add packet to data bucket
        if len(self.data_bucket) < self.data_bucket_size:
            packet = Packet(self.current_time, packet_size)
            self.data_bucket.append(packet)
            # try to transmit immediately
            self.try_transmit_packets()
        else:
            # data bucket full, drop packet
            self.packets_lost += 1
        
        # schedule next arrival
        next_arrival_time = self.current_time + self.generate_exponential(1.0 / self.arrival_rate)
        if next_arrival_time < self.run_time:
            self.schedule_event(Event(next_arrival_time, EVENT_PACKET_ARRIVAL))
    
    def try_transmit_packets(self):
        """if enough tokens are available"""
        while len(self.data_bucket) > 0:
            packet = self.data_bucket[0] 
            
            if self.token_bucket >= packet.size:
                # enough tokens
                self.data_bucket.popleft()
                self.token_bucket -= packet.size
                self.packets_transmitted += 1
                self.bits_transmitted += packet.size
            else:
                # not enough tokens
                break
    
    def update_statistics(self):
        time_diff = self.current_time - self.last_stat_time
        self.total_queue_time += len(self.data_bucket) * time_diff
        self.last_stat_time = self.current_time
    
    def run(self):
        print(f"  Token bucket: {self.token_bucket_size} bits, Data bucket: {self.data_bucket_size} pkts")
        print(f"  Token rate: {self.token_rate/1e3:.1f} kbps, Arrival rate: {self.arrival_rate} pkt/sec")
        
        # schedule first packet arrival
        first_arrival = self.generate_exponential(1.0 / self.arrival_rate)
        self.schedule_event(Event(first_arrival, EVENT_PACKET_ARRIVAL))

        self.token_bucket = self.token_bucket_size
        self.last_token_update = 0.0
        
        # events
        while self.event_queue:
            event = heapq.heappop(self.event_queue)
            
            if event.time > self.run_time:
                break
            
            self.update_statistics()
            self.current_time = event.time
            
            if event.event_type == EVENT_PACKET_ARRIVAL:
                self.packet_arrival_event()
        
        self.current_time = self.run_time
        self.update_tokens(self.current_time)
        self.update_statistics()
        
        print(f"  Arrived: {self.packets_arrived}, transmitted: {self.packets_transmitted}, lost: {self.packets_lost}")
    
    def get_results(self):
        loss_rate = self.packets_lost / self.packets_arrived if self.packets_arrived > 0 else 0
        mean_output_rate_bps = self.bits_transmitted / self.run_time
        mean_output_rate_pps = self.packets_transmitted / self.run_time
        avg_queue_length = self.total_queue_time / self.run_time
        
        return {
            'token_bucket_size': self.token_bucket_size,
            'data_bucket_size': self.data_bucket_size,
            'token_rate': self.token_rate,
            'packets_arrived': self.packets_arrived,
            'packets_transmitted': self.packets_transmitted,
            'packets_lost': self.packets_lost,
            'bits_transmitted': self.bits_transmitted,
            'loss_rate': loss_rate,
            'mean_output_rate_bps': mean_output_rate_bps,
            'mean_output_rate_pps': mean_output_rate_pps,
            'avg_queue_length': avg_queue_length
        }
    
    def print_results(self):
        results = self.get_results()
        
        print("\n")
        print("SIMULATION RESULTS")
        print("\n")
        print(f"Token bucket size:      {results['token_bucket_size']} bits")
        print(f"Data bucket size:       {results['data_bucket_size']} packets")
        print(f"Packets arrived:        {results['packets_arrived']}")
        print(f"Packets transmitted:    {results['packets_transmitted']}")
        print(f"Packets lost:           {results['packets_lost']}")
        print(f"Bits transmitted:       {results['bits_transmitted']}")
        print(f"Loss rate:              {results['loss_rate']:.6f} ({results['loss_rate']*100:.2f}%)")
        print(f"Mean output rate:       {results['mean_output_rate_bps']/1e3:.2f} kbps")
        print(f"Average queue length:   {results['avg_queue_length']:.2f} packets")
        print("\n")


def vary_token_bucket_size_bits():
    """
    Part 3b Experiment 1: Vary token bucket size Bt_max (in bits)
    Fixed: Bd_max = 20, token_rate = 150 kbps, arrival_rate = 100 pkt/sec
    """
    print("\n")
    print("PART 3b - EXPERIMENT 1: VARYING TOKEN BUCKET SIZE (Bt_max in bits)")
    print("\n")
    
    # fixed parameters
    data_bucket_size = 20
    token_rate = 200e3  # 150 kbps
    arrival_rate = 100  # packets/sec
    packet_sizes = [500, 1000, 1500, 2000, 2500]  # bits
    run_time = 1000
    
    # vary token bucket size in bits
    token_bucket_sizes = [500, 1000, 2000, 5000, 10000, 15000, 20000, 30000, 50000]
    
    results = []
    
    for idx, Bt in enumerate(token_bucket_sizes):
        print(f"\nRunning with Bt_max = {Bt} bits...")
        sim = BitCountingTokenBucket(
            token_bucket_size=Bt,
            data_bucket_size=data_bucket_size,
            token_rate=token_rate,
            arrival_rate=arrival_rate,
            packet_sizes=packet_sizes,
            run_time=run_time,
            random_seed = 400430923 + idx
        )
        sim.run()
        results.append(sim.get_results())
    
    # plots
    bt_sizes = [r['token_bucket_size'] for r in results]
    loss_rates = [r['loss_rate'] for r in results]
    output_rates = [r['mean_output_rate_bps']/1e3 for r in results]  # Convert to kbps
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # loss rate
    ax1.plot(bt_sizes, loss_rates, 'bo-', linewidth=2, markersize=8)
    ax1.set_xlabel('Token Bucket Size Bt_max (bits)', fontsize=12)
    ax1.set_ylabel('Packet Loss Rate', fontsize=12)
    ax1.set_title('Loss Rate vs Token Bucket Size\n(Bd_max=20, R=150 kbps, λ=100 pkt/s)', fontsize=13)
    ax1.grid(True, alpha=0.3)
    
    # output rate
    ax2.plot(bt_sizes, output_rates, 'ro-', linewidth=2, markersize=8)
    ax2.axhline(y=token_rate/1e3, color='b', linestyle='--', linewidth=2, 
                label=f'Token rate = 150 kbps')
    avg_arrival_rate = arrival_rate * np.mean(packet_sizes) / 1e3
    ax2.axhline(y=avg_arrival_rate, color='g', linestyle='--', linewidth=2, 
                label=f'Avg arrival rate = {avg_arrival_rate:.1f} kbps')
    ax2.set_xlabel('Token Bucket Size Bt_max (bits)', fontsize=12)
    ax2.set_ylabel('Mean Output Rate (kbps)', fontsize=12)
    ax2.set_title('Output Rate vs Token Bucket Size\n(Bd_max=20, R=150 kbps, λ=100 pkt/s)', fontsize=13)
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('lab5_part3b1_token_bucket_size_bits.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("\nPlot saved as 'lab5_part3b1_token_bucket_size_bits.png'")
    return results


def vary_token_rate():
    """
    Part 3b Experiment 2: Vary token rate
    Fixed: Bt_max = 10000 bits, Bd_max = 20, arrival_rate = 100 pkt/sec
    """
    print("\n")
    print("PART 3b - EXPERIMENT 2: VARYING TOKEN RATE")
    print("\n")
    
    #fFixed parameters
    token_bucket_size = 10000  # bits
    data_bucket_size = 20
    arrival_rate = 100  # packets/sec
    packet_sizes = [500, 1000, 1500, 2000, 2500]  # bits
    run_time = 1000
    
    # vary token rate
    token_rates_kbps = [50, 75, 100, 125, 150, 175, 200]
    token_rates = [R * 1e3 for R in token_rates_kbps]
    
    results = []
    
    for idx, R in enumerate(token_rates):
        print(f"\nRunning with token rate = {R/1e3:.1f} kbps...")
        sim = BitCountingTokenBucket(
            token_bucket_size=token_bucket_size,
            data_bucket_size=data_bucket_size,
            token_rate=R,
            arrival_rate=arrival_rate,
            packet_sizes=packet_sizes,
            run_time=run_time,
            random_seed= 400430923 + idx
        )
        sim.run()
        results.append(sim.get_results())
    
    # plots
    rates = [r['token_rate']/1e3 for r in results]
    loss_rates = [r['loss_rate'] for r in results]
    output_rates = [r['mean_output_rate_bps']/1e3 for r in results]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # loss rate
    ax1.plot(rates, loss_rates, 'bo-', linewidth=2, markersize=8)
    avg_arrival_rate = arrival_rate * np.mean(packet_sizes) / 1e3
    ax1.axvline(x=avg_arrival_rate, color='g', linestyle='--', linewidth=2, 
                label=f'Avg arrival rate = {avg_arrival_rate:.1f} kbps')
    ax1.set_xlabel('Token Rate (kbps)', fontsize=12)
    ax1.set_ylabel('Packet Loss Rate', fontsize=12)
    ax1.set_title('Loss Rate vs Token Rate\n(Bt_max=10k bits, Bd_max=20, λ=100 pkt/s)', fontsize=13)
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # output rate
    ax2.plot(rates, output_rates, 'ro-', linewidth=2, markersize=8)
    ax2.plot(rates, rates, 'k--', linewidth=1, label='Token rate')
    ax2.axhline(y=avg_arrival_rate, color='g', linestyle='--', linewidth=2, 
                label=f'Avg arrival rate = {avg_arrival_rate:.1f} kbps')
    ax2.set_xlabel('Token Rate (kbps)', fontsize=12)
    ax2.set_ylabel('Mean Output Rate (kbps)', fontsize=12)
    ax2.set_title('Output Rate vs Token Rate\n(Bt_max=10k bits, Bd_max=20, λ=100 pkt/s)', fontsize=13)
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('lab5_part3b2_token_rate.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("\nPlot saved as 'lab5_part3b2_token_rate.png'")
    return results


def vary_data_bucket_size_bits():
    """
    Part 3b Experiment 3: Vary data bucket size Bd_max
    Fixed: Bt_max = 10000 bits, token_rate = 150 kbps, arrival_rate = 100 pkt/sec
    """
    print("\n")
    print("PART 3b - EXPERIMENT 3: VARYING DATA BUCKET SIZE (Bd_max)")
    print("\n")
    
    # fixed parameters
    token_bucket_size = 10000  # bits
    token_rate = 200e3  # 150 kbps
    arrival_rate = 100  # packets/sec
    packet_sizes = [500, 1000, 1500, 2000, 2500]  # bits
    run_time = 1000
    
    data_bucket_sizes = range(5, 51, 5)
    
    results = []
    
    for idx, Bd in enumerate(data_bucket_sizes):
        print(f"\nRunning with Bd_max = {Bd} packets...")
        sim = BitCountingTokenBucket(
            token_bucket_size=token_bucket_size,
            data_bucket_size=Bd,
            token_rate=token_rate,
            arrival_rate=arrival_rate,
            packet_sizes=packet_sizes,
            run_time=run_time,
            random_seed = 400430923 + idx
        )
        sim.run()
        results.append(sim.get_results())
    
    # plots
    bd_sizes = [r['data_bucket_size'] for r in results]
    loss_rates = [r['loss_rate'] for r in results]
    output_rates = [r['mean_output_rate_bps']/1e3 for r in results]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # loss rate
    ax1.plot(bd_sizes, loss_rates, 'bo-', linewidth=2, markersize=8)
    ax1.set_xlabel('Data Bucket Size Bd_max (packets)', fontsize=12)
    ax1.set_ylabel('Packet Loss Rate', fontsize=12)
    ax1.set_title('Loss Rate vs Data Bucket Size\n(Bt_max=10k bits, R=150 kbps, λ=100 pkt/s)', fontsize=13)
    ax1.grid(True, alpha=0.3)
    
    # output rate
    ax2.plot(bd_sizes, output_rates, 'ro-', linewidth=2, markersize=8)
    ax2.axhline(y=token_rate/1e3, color='b', linestyle='--', linewidth=2, 
                label=f'Token rate = 150 kbps')
    avg_arrival_rate = arrival_rate * np.mean(packet_sizes) / 1e3
    ax2.axhline(y=avg_arrival_rate, color='g', linestyle='--', linewidth=2, 
                label=f'Avg arrival rate = {avg_arrival_rate:.1f} kbps')
    ax2.set_xlabel('Data Bucket Size Bd_max (packets)', fontsize=12)
    ax2.set_ylabel('Mean Output Rate (kbps)', fontsize=12)
    ax2.set_title('Output Rate vs Data Bucket Size\n(Bt_max=10k bits, R=150 kbps, λ=100 pkt/s)', fontsize=13)
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('lab5_part3b3_data_bucket_size.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("\nPlot saved as 'lab5_part3b3_data_bucket_size.png'")
    return results


if __name__ == "__main__":
    print("\n")
    print("LAB 5 - PART 3b: TOKEN BUCKET (BIT-COUNTING)")
    print("\n")
    
    results1 = vary_token_bucket_size_bits()
    results2 = vary_token_rate()
    results3 = vary_data_bucket_size_bits()
    
    print("\n")
    print("ALL PART 3b EXPERIMENTS COMPLETE!")
    print("Generated files:")
    print("  - lab5_part3b1_token_bucket_size_bits.png")
    print("  - lab5_part3b2_token_rate.png")
    print("  - lab5_part3b3_data_bucket_size.png")
    print("\n")