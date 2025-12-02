import numpy as np
import matplotlib.pyplot as plt
from collections import deque
import heapq

# Event types
EVENT_PACKET_ARRIVAL = "PACKET_ARRIVAL"
EVENT_CLOCK_TICK = "CLOCK_TICK"

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

class BitCountingLeakyBucket:
    def __init__(self, output_rate, arrival_rate, packet_sizes, bucket_size, 
                 clock_period, run_time, random_seed=None):
        """
        output_rate: R, output rate in bits per second (bps)
        arrival_rate: lambda, arrival rate in packets per second
        packet_sizes: list of possible packet sizes in bits
        bucket_size: maximum queue size in packets
        clock_period: clock ticking period in seconds (T)
        run_time: simulation duration in seconds
        """
        self.output_rate = output_rate
        self.arrival_rate = arrival_rate
        self.packet_sizes = packet_sizes
        self.bucket_size = bucket_size
        self.clock_period = clock_period
        self.run_time = run_time
        
        # Counter initialized to n bits per clock tick
        # n = output_rate * clock_period
        self.n = output_rate * clock_period
        
        if random_seed is not None:
            np.random.seed(random_seed)
        
        # Simulation state
        self.current_time = 0.0
        self.event_queue = []
        self.packet_queue = deque()  # The "bucket"
        self.bit_counter = 0  # Current bit counter
        
        # Statistics
        self.packets_arrived = 0
        self.packets_dropped = 0
        self.packets_transmitted = 0
        self.bits_transmitted = 0
        self.total_queue_occupancy = 0.0
        self.last_event_time = 0.0
        
    def schedule_event(self, event):
        """Add event to priority queue"""
        heapq.heappush(self.event_queue, event)
    
    def generate_exponential(self, mean):
        """Generate exponentially distributed random variable"""
        return np.random.exponential(mean)
    
    def generate_packet_size(self):
        """Generate packet size with equal probability from available sizes"""
        return np.random.choice(self.packet_sizes)
    
    def packet_arrival_event(self):
        """Handle packet arrival"""
        self.packets_arrived += 1
        
        # Generate packet
        packet = Packet(self.current_time, self.generate_packet_size())
        
        # Check if bucket has space
        if len(self.packet_queue) < self.bucket_size:
            # Add packet to queue
            self.packet_queue.append(packet)
        else:
            # Bucket full - drop packet
            self.packets_dropped += 1
        
        # Schedule next arrival (Poisson process)
        next_arrival_time = self.current_time + self.generate_exponential(1.0 / self.arrival_rate)
        if next_arrival_time < self.run_time:
            self.schedule_event(Event(next_arrival_time, EVENT_PACKET_ARRIVAL))
    
    def clock_tick_event(self):
        """
        Handle clock tick - transmit packets as long as counter allows
        At each tick:
        1. Initialize counter to n
        2. Transmit packets while counter >= next packet size
        3. Decrement counter by transmitted packet size
        4. Stop when counter < next packet size
        5. Residual counter is lost
        """
        # Initialize counter to n bits
        self.bit_counter = self.n
        
        # Transmit packets while possible
        while len(self.packet_queue) > 0:
            next_packet = self.packet_queue[0]  # Peek at first packet
            
            if self.bit_counter >= next_packet.size:
                # Can transmit this packet
                packet = self.packet_queue.popleft()
                self.bit_counter -= packet.size
                self.packets_transmitted += 1
                self.bits_transmitted += packet.size
            else:
                # Counter too low for next packet, stop transmission
                break
        
        # Residual counter is lost (overwritten at next tick)
        
        # Schedule next clock tick
        next_tick_time = self.current_time + self.clock_period
        if next_tick_time < self.run_time:
            self.schedule_event(Event(next_tick_time, EVENT_CLOCK_TICK))
    
    def update_statistics(self):
        """Update time-weighted statistics"""
        time_delta = self.current_time - self.last_event_time
        self.total_queue_occupancy += len(self.packet_queue) * time_delta
        self.last_event_time = self.current_time
    
    def run(self):
        """Run the simulation"""
        print(f"Starting Bit-Counting Leaky Bucket Simulation...")
        print(f"  Bucket size: {self.bucket_size} packets")
        print(f"  Output rate (R): {self.output_rate/1e6:.2f} Mbps")
        print(f"  Arrival rate (λ): {self.arrival_rate} packets/sec")
        print(f"  Clock period (T): {self.clock_period*1000:.3f} ms")
        print(f"  Bits per tick (n): {self.n:.0f} bits")
        print(f"  Packet sizes: {self.packet_sizes} bits")
        print(f"  Run time: {self.run_time} sec")
        
        # Schedule first packet arrival
        first_arrival = self.generate_exponential(1.0 / self.arrival_rate)
        self.schedule_event(Event(first_arrival, EVENT_PACKET_ARRIVAL))
        
        # Schedule first clock tick
        self.schedule_event(Event(0.0, EVENT_CLOCK_TICK))
        
        # Event loop
        while len(self.event_queue) > 0:
            event = heapq.heappop(self.event_queue)
            
            # Update statistics before processing event
            self.update_statistics()
            
            self.current_time = event.time
            
            if self.current_time >= self.run_time:
                break
            
            # Process event
            if event.event_type == EVENT_PACKET_ARRIVAL:
                self.packet_arrival_event()
            elif event.event_type == EVENT_CLOCK_TICK:
                self.clock_tick_event()
        
        print(f"Simulation complete!")
    
    def get_results(self):
        """Calculate and return simulation results"""
        loss_rate = self.packets_dropped / self.packets_arrived if self.packets_arrived > 0 else 0.0
        mean_output_rate_bps = self.bits_transmitted / self.run_time
        mean_output_rate_pps = self.packets_transmitted / self.run_time
        avg_queue_length = self.total_queue_occupancy / self.run_time
        
        return {
            'packets_arrived': self.packets_arrived,
            'packets_dropped': self.packets_dropped,
            'packets_transmitted': self.packets_transmitted,
            'bits_transmitted': self.bits_transmitted,
            'loss_rate': loss_rate,
            'mean_output_rate_bps': mean_output_rate_bps,
            'mean_output_rate_pps': mean_output_rate_pps,
            'avg_queue_length': avg_queue_length
        }
    
    def print_results(self):
        """Print simulation results"""
        results = self.get_results()
        
        print("\n" + "="*60)
        print("SIMULATION RESULTS")
        print("="*60)
        print(f"Packets arrived:        {results['packets_arrived']}")
        print(f"Packets dropped:        {results['packets_dropped']}")
        print(f"Packets transmitted:    {results['packets_transmitted']}")
        print(f"Bits transmitted:       {results['bits_transmitted']}")
        print(f"Loss rate:              {results['loss_rate']:.6f} ({results['loss_rate']*100:.2f}%)")
        print(f"Mean output rate:       {results['mean_output_rate_bps']/1e6:.4f} Mbps")
        print(f"Mean output rate:       {results['mean_output_rate_pps']:.2f} packets/sec")
        print(f"Average queue length:   {results['avg_queue_length']:.2f} packets")
        print("="*60)


def vary_clock_period():
    """
    Study effect of clock period on loss rate and output rate
    Fixed: R = 1 Mbps, λ = 100 pkt/s, packet sizes [500, 1k, 1.5k, 2k, 2.5k] bits
    """
    print("\n" + "="*70)
    print("EXPERIMENT 1: VARYING CLOCK PERIOD")
    print("="*70)
    
    # Fixed parameters
    output_rate = 1e6  # 1 Mbps
    arrival_rate = 100  # packets/sec
    packet_sizes = [500, 1000, 1500, 2000, 2500]  # bits
    bucket_size = 50  # packets
    run_time = 1000  # seconds
    
    # Average packet size
    avg_packet_size = np.mean(packet_sizes)
    print(f"\nAverage packet size: {avg_packet_size} bits")
    print(f"Average arrival rate: {arrival_rate * avg_packet_size / 1e6:.4f} Mbps")
    
    # Vary clock period from 0.5ms to 20ms
    clock_periods_ms = [0.5, 1, 2, 5, 10, 15, 20]
    clock_periods = [t / 1000 for t in clock_periods_ms]  # Convert to seconds
    
    results = []
    
    for T in clock_periods:
        print(f"\nRunning simulation with T = {T*1000:.1f} ms (n = {output_rate*T:.0f} bits)...")
        
        sim = BitCountingLeakyBucket(
            output_rate=output_rate,
            arrival_rate=arrival_rate,
            packet_sizes=packet_sizes,
            bucket_size=bucket_size,
            clock_period=T,
            run_time=run_time,
            random_seed=12345
        )
        
        sim.run()
        sim_results = sim.get_results()
        
        results.append({
            'clock_period_ms': T * 1000,
            'n_bits': output_rate * T,
            'loss_rate': sim_results['loss_rate'],
            'output_rate_mbps': sim_results['mean_output_rate_bps'] / 1e6
        })
        
        print(f"  Loss rate: {sim_results['loss_rate']:.6f}")
        print(f"  Output rate: {sim_results['mean_output_rate_bps']/1e6:.4f} Mbps")
    
    # Plot results
    clock_periods_list = [r['clock_period_ms'] for r in results]
    loss_rates = [r['loss_rate'] for r in results]
    output_rates = [r['output_rate_mbps'] for r in results]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Plot loss rate
    ax1.plot(clock_periods_list, loss_rates, 'bo-', linewidth=2, markersize=8)
    ax1.set_xlabel('Clock Period T (ms)', fontsize=12)
    ax1.set_ylabel('Packet Loss Rate', fontsize=12)
    ax1.set_title('Loss Rate vs Clock Period\n(R=1Mbps, λ=100pkt/s, B=50)', fontsize=13)
    ax1.grid(True, alpha=0.3)
    
    # Plot output rate
    ax2.plot(clock_periods_list, output_rates, 'ro-', linewidth=2, markersize=8)
    ax2.axhline(y=1.0, color='k', linestyle='--', linewidth=2, 
                label='Configured rate (1 Mbps)')
    ax2.axhline(y=arrival_rate*avg_packet_size/1e6, color='g', linestyle='--', 
                linewidth=2, label=f'Avg arrival rate ({arrival_rate*avg_packet_size/1e6:.3f} Mbps)')
    ax2.set_xlabel('Clock Period T (ms)', fontsize=12)
    ax2.set_ylabel('Mean Output Rate (Mbps)', fontsize=12)
    ax2.set_title('Output Rate vs Clock Period\n(R=1Mbps, λ=100pkt/s, B=50)', fontsize=13)
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('lab5_part2_clock_period.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("\nPlot saved as 'lab5_part2_clock_period.png'")
    return results


def vary_n_bits():
    """
    Study effect of n (bits per clock tick) on performance
    Keep clock period fixed, vary output rate R to change n
    """
    print("\n" + "="*70)
    print("EXPERIMENT 2: VARYING n (BITS PER TICK)")
    print("="*70)
    
    # Fixed parameters
    arrival_rate = 100  # packets/sec
    packet_sizes = [500, 1000, 1500, 2000, 2500]  # bits
    bucket_size = 50  # packets
    clock_period = 0.01  # 10 ms - fixed
    run_time = 1000  # seconds
    
    avg_packet_size = np.mean(packet_sizes)
    
    # Vary output rate to change n
    output_rates_mbps = [0.05, 0.1, 0.15, 0.2, 0.3, 0.5, 1.0]
    output_rates = [R * 1e6 for R in output_rates_mbps]
    
    results = []
    
    for R in output_rates:
        n = R * clock_period
        print(f"\nRunning simulation with R = {R/1e6:.2f} Mbps (n = {n:.0f} bits)...")
        
        sim = BitCountingLeakyBucket(
            output_rate=R,
            arrival_rate=arrival_rate,
            packet_sizes=packet_sizes,
            bucket_size=bucket_size,
            clock_period=clock_period,
            run_time=run_time,
            random_seed=12345
        )
        
        sim.run()
        sim_results = sim.get_results()
        
        results.append({
            'output_rate_mbps': R / 1e6,
            'n_bits': n,
            'loss_rate': sim_results['loss_rate'],
            'output_rate_actual_mbps': sim_results['mean_output_rate_bps'] / 1e6
        })
        
        print(f"  Loss rate: {sim_results['loss_rate']:.6f}")
        print(f"  Output rate: {sim_results['mean_output_rate_bps']/1e6:.4f} Mbps")
    
    # Plot results
    n_bits_list = [r['n_bits'] for r in results]
    loss_rates = [r['loss_rate'] for r in results]
    output_rates_actual = [r['output_rate_actual_mbps'] for r in results]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Plot loss rate
    ax1.plot(n_bits_list, loss_rates, 'bo-', linewidth=2, markersize=8)
    ax1.set_xlabel('n - Bits per Clock Tick', fontsize=12)
    ax1.set_ylabel('Packet Loss Rate', fontsize=12)
    ax1.set_title('Loss Rate vs n\n(T=10ms, λ=100pkt/s, B=50)', fontsize=13)
    ax1.grid(True, alpha=0.3)
    
    # Plot output rate
    ax2.plot(n_bits_list, output_rates_actual, 'ro-', linewidth=2, markersize=8)
    ax2.axhline(y=arrival_rate*avg_packet_size/1e6, color='g', linestyle='--', 
                linewidth=2, label=f'Avg arrival rate ({arrival_rate*avg_packet_size/1e6:.3f} Mbps)')
    ax2.set_xlabel('n - Bits per Clock Tick', fontsize=12)
    ax2.set_ylabel('Mean Output Rate (Mbps)', fontsize=12)
    ax2.set_title('Output Rate vs n\n(T=10ms, λ=100pkt/s, B=50)', fontsize=13)
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('lab5_part2_n_bits.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("\nPlot saved as 'lab5_part2_n_bits.png'")
    return results


def vary_output_rate():
    """
    Study effect of output rate R on performance
    Fixed clock period
    """
    print("\n" + "="*70)
    print("EXPERIMENT 3: VARYING OUTPUT RATE R")
    print("="*70)
    
    # Fixed parameters
    arrival_rate = 100  # packets/sec
    packet_sizes = [500, 1000, 1500, 2000, 2500]  # bits
    bucket_size = 50  # packets
    clock_period = 0.01  # 10 ms
    run_time = 1000  # seconds
    
    avg_packet_size = np.mean(packet_sizes)
    avg_arrival_rate_bps = arrival_rate * avg_packet_size
    
    # Vary output rate from 50 kbps to 300 kbps
    output_rates_kbps = np.arange(50, 301, 25)
    output_rates = output_rates_kbps * 1e3
    
    results = []
    
    for R in output_rates:
        print(f"\nRunning simulation with R = {R/1e3:.0f} kbps...")
        
        sim = BitCountingLeakyBucket(
            output_rate=R,
            arrival_rate=arrival_rate,
            packet_sizes=packet_sizes,
            bucket_size=bucket_size,
            clock_period=clock_period,
            run_time=run_time,
            random_seed=12345
        )
        
        sim.run()
        sim_results = sim.get_results()
        
        results.append({
            'output_rate_kbps': R / 1e3,
            'loss_rate': sim_results['loss_rate'],
            'output_rate_actual_kbps': sim_results['mean_output_rate_bps'] / 1e3
        })
        
        print(f"  Loss rate: {sim_results['loss_rate']:.6f}")
        print(f"  Output rate: {sim_results['mean_output_rate_bps']/1e3:.2f} kbps")
    
    # Plot results
    output_rates_list = [r['output_rate_kbps'] for r in results]
    loss_rates = [r['loss_rate'] for r in results]
    output_rates_actual = [r['output_rate_actual_kbps'] for r in results]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Plot loss rate
    ax1.plot(output_rates_list, loss_rates, 'bo-', linewidth=2, markersize=6)
    ax1.axvline(x=avg_arrival_rate_bps/1e3, color='g', linestyle='--', 
                linewidth=2, label=f'Avg arrival rate ({avg_arrival_rate_bps/1e3:.1f} kbps)')
    ax1.set_xlabel('Configured Output Rate R (kbps)', fontsize=12)
    ax1.set_ylabel('Packet Loss Rate', fontsize=12)
    ax1.set_title('Loss Rate vs Output Rate\n(T=10ms, λ=100pkt/s, B=50)', fontsize=13)
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # Plot output rate
    ax2.plot(output_rates_list, output_rates_actual, 'ro-', linewidth=2, markersize=6)
    ax2.plot(output_rates_list, output_rates_list, 'k--', linewidth=1, 
             label='Configured rate R')
    ax2.axhline(y=avg_arrival_rate_bps/1e3, color='g', linestyle='--', 
                linewidth=2, label=f'Avg arrival rate ({avg_arrival_rate_bps/1e3:.1f} kbps)')
    ax2.set_xlabel('Configured Output Rate R (kbps)', fontsize=12)
    ax2.set_ylabel('Actual Mean Output Rate (kbps)', fontsize=12)
    ax2.set_title('Output Rate vs Configured Rate\n(T=10ms, λ=100pkt/s, B=50)', fontsize=13)
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('lab5_part2_output_rate.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("\nPlot saved as 'lab5_part2_output_rate.png'")
    return results


def analyze_results():
    """
    Analyze and explain observations from bit-counting leaky bucket
    """
    print("\n" + "="*70)
    print("ANALYSIS AND OBSERVATIONS - BIT-COUNTING LEAKY BUCKET")
    print("="*70)
    
    print("\nExperiment 1: Clock Period Effect")
    print("-" * 70)
    print("Justification for clock period choice:")
    print("  • Should be comparable to average packet transmission time")
    print("  • Average packet size = 1500 bits, at R=1Mbps: T_pkt = 1.5ms")
    print("  • Choose T in range [1ms, 10ms] for reasonable operation")
    print("  • Too small T: Overhead from frequent clock ticks")
    print("  • Too large T: Cannot utilize full bandwidth (n might be large")
    print("    but packets smaller than n are transmitted inefficiently)")
    print("\nObservations:")
    print("  • Loss rate generally low when T is moderate")
    print("  • Output rate approaches arrival rate for reasonable T")
    print("  • Very large T can cause inefficiency if n >> packet sizes")
    
    print("\n\nExperiment 2: Effect of n (Bits per Tick)")
    print("-" * 70)
    print("  • n = R × T determines how many bits can be sent per tick")
    print("  • When n < min(packet_size), some packets cannot be sent")
    print("  • When n ≥ max(packet_size), multiple packets can be sent per tick")
    print("  • Loss rate decreases as n increases (more capacity)")
    print("  • Output rate limited by min(R, arrival_rate)")
    
    print("\n\nExperiment 3: Output Rate R Effect")
    print("-" * 70)
    print("  • Similar to original leaky bucket behavior")
    print("  • When R < arrival_rate: High loss, output = R")
    print("  • When R ≥ arrival_rate: Low loss, output ≈ arrival_rate")
    print("  • Critical threshold around R = λ × average_packet_size")
    
    print("\n\nKey Differences from Original Leaky Bucket:")
    print("-" * 70)
    print("  • Bit-counting allows multiple small packets per tick")
    print("  • More efficient bandwidth utilization for variable packet sizes")
    print("  • Residual bits lost at each tick (slight inefficiency)")
    print("  • Better suited for networks with heterogeneous packet sizes")
    print("="*70)


if __name__ == "__main__":
    print("="*70)
    print("LAB 5 - PART 2: BIT-COUNTING LEAKY BUCKET")
    print("="*70)
    
    # Run experiments
    results_clock = vary_clock_period()
    results_n = vary_n_bits()
    results_rate = vary_output_rate()
    
    # Analyze results
    analyze_results()
    
    print("\n" + "="*70)
    print("PART 2 COMPLETE!")
    print("Generated files:")
    print("  - lab5_part2_clock_period.png")
    print("  - lab5_part2_n_bits.png")
    print("  - lab5_part2_output_rate.png")
    print("="*70)
