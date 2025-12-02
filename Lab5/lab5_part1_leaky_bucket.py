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

class LeakyBucketSimulator:
    def __init__(self, bucket_size, output_rate, arrival_rate, run_time, random_seed=None):
        """
        bucket_size: B, maximum queue size in packets
        output_rate: R, output rate in packets per second
        arrival_rate: lambda, arrival rate in packets per second (Poisson)
        run_time: simulation duration in seconds
        """
        self.bucket_size = bucket_size
        self.output_rate = output_rate
        self.arrival_rate = arrival_rate
        self.run_time = run_time
        
        if random_seed is not None:
            np.random.seed(random_seed)
        
        # Simulation state
        self.current_time = 0.0
        self.event_queue = []
        self.packet_queue = deque()  # The "bucket"
        
        # Clock tick period (X = 1/R seconds)
        self.tick_period = 1.0 / output_rate
        
        # Statistics
        self.packets_arrived = 0
        self.packets_dropped = 0
        self.packets_transmitted = 0
        self.total_queue_occupancy = 0.0
        self.last_event_time = 0.0
        
    def schedule_event(self, event):
        """Add event to priority queue"""
        heapq.heappush(self.event_queue, event)
    
    def generate_exponential(self, mean):
        """Generate exponentially distributed random variable"""
        return np.random.exponential(mean)
    
    def packet_arrival_event(self):
        """Handle packet arrival"""
        self.packets_arrived += 1
        
        # Check if bucket has space
        if len(self.packet_queue) < self.bucket_size:
            # Add packet to queue
            self.packet_queue.append(self.current_time)
        else:
            # Bucket full - drop packet
            self.packets_dropped += 1
        
        # Schedule next arrival (Poisson process)
        next_arrival_time = self.current_time + self.generate_exponential(1.0 / self.arrival_rate)
        if next_arrival_time < self.run_time:
            self.schedule_event(Event(next_arrival_time, EVENT_PACKET_ARRIVAL))
    
    def clock_tick_event(self):
        """Handle clock tick - transmit one packet if available"""
        # If queue is not empty, transmit one packet
        if len(self.packet_queue) > 0:
            self.packet_queue.popleft()
            self.packets_transmitted += 1
        
        # Schedule next clock tick
        next_tick_time = self.current_time + self.tick_period
        if next_tick_time < self.run_time:
            self.schedule_event(Event(next_tick_time, EVENT_CLOCK_TICK))
    
    def update_statistics(self):
        """Update time-weighted statistics"""
        time_delta = self.current_time - self.last_event_time
        self.total_queue_occupancy += len(self.packet_queue) * time_delta
        self.last_event_time = self.current_time
    
    def run(self):
        """Run the simulation"""
        print(f"Starting Leaky Bucket Simulation...")
        print(f"  Bucket size (B): {self.bucket_size} packets")
        print(f"  Output rate (R): {self.output_rate} packets/sec")
        print(f"  Arrival rate (λ): {self.arrival_rate} packets/sec")
        print(f"  Tick period: {self.tick_period*1000:.3f} ms")
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
        mean_output_rate = self.packets_transmitted / self.run_time
        avg_queue_length = self.total_queue_occupancy / self.run_time
        
        return {
            'packets_arrived': self.packets_arrived,
            'packets_dropped': self.packets_dropped,
            'packets_transmitted': self.packets_transmitted,
            'loss_rate': loss_rate,
            'mean_output_rate': mean_output_rate,
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
        print(f"Loss rate:              {results['loss_rate']:.6f} ({results['loss_rate']*100:.2f}%)")
        print(f"Mean output rate:       {results['mean_output_rate']:.2f} packets/sec")
        print(f"Average queue length:   {results['avg_queue_length']:.2f} packets")
        print("="*60)


def run_part1a():
    """
    Part 1a: Vary bucket size B, plot loss rate and mean output rate
    Fixed parameters: R = 1000 packets/sec, λ = 100 packets/sec
    """
    print("\n" + "="*70)
    print("PART 1a: VARYING BUCKET SIZE B")
    print("="*70)
    
    # Fixed parameters
    output_rate = 1000  # R = 1000 packets/sec
    arrival_rate = 100  # λ = 100 packets/sec
    run_time = 1000     # 1000 seconds simulation
    
    # Vary bucket size
    bucket_sizes = range(1, 21)  # B from 1 to 20 packets
    
    results = []
    
    for B in bucket_sizes:
        print(f"\nRunning simulation with B = {B} packets...")
        
        sim = LeakyBucketSimulator(
            bucket_size=B,
            output_rate=output_rate,
            arrival_rate=arrival_rate,
            run_time=run_time,
            random_seed=12345
        )
        
        sim.run()
        sim_results = sim.get_results()
        
        results.append({
            'bucket_size': B,
            'loss_rate': sim_results['loss_rate'],
            'mean_output_rate': sim_results['mean_output_rate']
        })
        
        print(f"  Loss rate: {sim_results['loss_rate']:.6f}")
        print(f"  Mean output rate: {sim_results['mean_output_rate']:.2f} packets/sec")
    
    # Plot results
    bucket_sizes_list = [r['bucket_size'] for r in results]
    loss_rates = [r['loss_rate'] for r in results]
    output_rates = [r['mean_output_rate'] for r in results]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Plot loss rate
    ax1.plot(bucket_sizes_list, loss_rates, 'bo-', linewidth=2, markersize=6)
    ax1.set_xlabel('Bucket Size B (packets)', fontsize=12)
    ax1.set_ylabel('Packet Loss Rate', fontsize=12)
    ax1.set_title('Loss Rate vs Bucket Size\n(R=1000 pkt/s, λ=100 pkt/s)', fontsize=13)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(0, max(bucket_sizes_list) + 1)
    
    # Plot mean output rate
    ax2.plot(bucket_sizes_list, output_rates, 'ro-', linewidth=2, markersize=6)
    ax2.axhline(y=arrival_rate, color='g', linestyle='--', linewidth=2, 
                label=f'Arrival rate = {arrival_rate} pkt/s')
    ax2.set_xlabel('Bucket Size B (packets)', fontsize=12)
    ax2.set_ylabel('Mean Output Rate (packets/sec)', fontsize=12)
    ax2.set_title('Output Rate vs Bucket Size\n(R=1000 pkt/s, λ=100 pkt/s)', fontsize=13)
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(0, max(bucket_sizes_list) + 1)
    
    plt.tight_layout()
    plt.savefig('lab5_part1a_results.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("\n" + "="*70)
    print("Plot saved as 'lab5_part1a_results.png'")
    print("="*70)
    
    return results


def run_part1b():
    """
    Part 1b: Fix B=3 packets, vary output rate R
    Fixed parameters: B = 3 packets, λ = 100 packets/sec
    """
    print("\n" + "="*70)
    print("PART 1b: VARYING OUTPUT RATE R (B=3 packets)")
    print("="*70)
    
    # Fixed parameters
    bucket_size = 3     # B = 3 packets
    arrival_rate = 100  # λ = 100 packets/sec
    run_time = 1000     # 1000 seconds simulation
    
    # Vary output rate from 50 to 200 packets/sec
    output_rates = np.arange(50, 201, 10)
    
    results = []
    
    for R in output_rates:
        print(f"\nRunning simulation with R = {R} packets/sec...")
        
        sim = LeakyBucketSimulator(
            bucket_size=bucket_size,
            output_rate=R,
            arrival_rate=arrival_rate,
            run_time=run_time,
            random_seed=12345
        )
        
        sim.run()
        sim_results = sim.get_results()
        
        results.append({
            'output_rate': R,
            'loss_rate': sim_results['loss_rate'],
            'mean_output_rate': sim_results['mean_output_rate']
        })
        
        print(f"  Loss rate: {sim_results['loss_rate']:.6f}")
        print(f"  Mean output rate: {sim_results['mean_output_rate']:.2f} packets/sec")
    
    # Plot results
    output_rates_list = [r['output_rate'] for r in results]
    loss_rates = [r['loss_rate'] for r in results]
    mean_output_rates = [r['mean_output_rate'] for r in results]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Plot loss rate
    ax1.plot(output_rates_list, loss_rates, 'bo-', linewidth=2, markersize=6)
    ax1.axvline(x=arrival_rate, color='g', linestyle='--', linewidth=2, 
                label=f'Arrival rate = {arrival_rate} pkt/s')
    ax1.set_xlabel('Output Rate R (packets/sec)', fontsize=12)
    ax1.set_ylabel('Packet Loss Rate', fontsize=12)
    ax1.set_title('Loss Rate vs Output Rate\n(B=3 packets, λ=100 pkt/s)', fontsize=13)
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # Plot mean output rate
    ax2.plot(output_rates_list, mean_output_rates, 'ro-', linewidth=2, markersize=6)
    ax2.plot(output_rates_list, output_rates_list, 'k--', linewidth=1, 
             label='Configured rate R')
    ax2.axhline(y=arrival_rate, color='g', linestyle='--', linewidth=2, 
                label=f'Arrival rate = {arrival_rate} pkt/s')
    ax2.set_xlabel('Output Rate R (packets/sec)', fontsize=12)
    ax2.set_ylabel('Mean Output Rate (packets/sec)', fontsize=12)
    ax2.set_title('Output Rate vs Configured Rate\n(B=3 packets, λ=100 pkt/s)', fontsize=13)
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('lab5_part1b_results.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("\n" + "="*70)
    print("Plot saved as 'lab5_part1b_results.png'")
    print("="*70)
    
    return results


def analyze_results():
    """
    Analyze and explain the observations from both experiments
    """
    print("\n" + "="*70)
    print("ANALYSIS AND OBSERVATIONS")
    print("="*70)
    
    print("\nPart 1a Observations (Varying Bucket Size B):")
    print("-" * 70)
    print("1. Loss Rate:")
    print("   - When B is very small (1-2 packets), loss rate is high due to")
    print("     limited buffering capacity for burst arrivals")
    print("   - As B increases, loss rate decreases exponentially")
    print("   - Beyond a certain B, loss rate approaches zero because the bucket")
    print("     can absorb all arrival bursts (λ < R, so system is stable)")
    print("\n2. Mean Output Rate:")
    print("   - Starts below arrival rate when B is very small (packets are lost)")
    print("   - Quickly converges to the arrival rate (100 pkt/s) as B increases")
    print("   - Stabilizes at 100 pkt/s (= λ) since R >> λ, the leaky bucket")
    print("     can always drain faster than packets arrive")
    
    print("\n\nPart 1b Observations (Varying Output Rate R, B=3):")
    print("-" * 70)
    print("1. Loss Rate:")
    print("   - High when R < λ (R < 100): System is unstable, queue always full")
    print("   - Drops sharply around R = λ: Critical transition point")
    print("   - Approaches zero when R > λ: System can drain faster than arrivals")
    print("   - Small buffer (B=3) means less tolerance for temporary bursts")
    print("\n2. Mean Output Rate:")
    print("   - When R < λ: Output rate = R (limited by service capacity)")
    print("   - When R >= λ: Output rate ≈ λ (limited by arrival rate)")
    print("   - The output rate is min(R, λ) in steady state")
    print("   - Cannot exceed arrival rate in long run (no packets to send!)")
    
    print("\n\nKey Insight:")
    print("-" * 70)
    print("The leaky bucket acts as a traffic shaper by:")
    print("  • Smoothing bursty traffic (constant output rate)")
    print("  • Dropping excess packets when buffer fills")
    print("  • Output rate = min(configured_rate, arrival_rate)")
    print("  • Larger buffers reduce loss but add delay")
    print("  • System stability requires R >= λ")
    print("="*70)


if __name__ == "__main__":
    # Run Part 1a
    results_1a = run_part1a()
    
    # Run Part 1b
    results_1b = run_part1b()
    
    # Analyze results
    analyze_results()
    
    print("\n" + "="*70)
    print("SIMULATION COMPLETE!")
    print("Generated files:")
    print("  - lab5_part1a_results.png")
    print("  - lab5_part1b_results.png")
    print("="*70)
