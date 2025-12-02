import numpy as np
import heapq
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Optional, List
import csv

# Event types
EVENT_PACKET_ARRIVAL = "PACKET_ARRIVAL"
EVENT_PACKET_DEPARTURE = "PACKET_DEPARTURE"

@dataclass
class Event:
    time: float
    event_type: str
    packet: Optional['Packet'] = None
    
    def __lt__(self, other):
        return self.time < other.time

@dataclass
class Packet:
    arrival_time: float
    size: float  # in bits
    start_service_time: Optional[float] = None
    departure_time: Optional[float] = None

class PacketSwitchSimulator:
    def __init__(self, arrival_rate, mean_packet_size, link_rate, run_length, random_seed=None):
        """
        arrival_rate: packets per second (lambda)
        mean_packet_size: average packet size in bits (1/mu for exponential)
        link_rate: transmission rate in bits per second (C)
        run_length: number of packets to process
        """
        self.arrival_rate = arrival_rate
        self.mean_packet_size = mean_packet_size
        self.link_rate = link_rate
        self.run_length = run_length
        
        if random_seed is not None:
            np.random.seed(random_seed)
        
        # Simulation state
        self.current_time = 0.0
        self.event_queue = []
        self.packet_queue = []  # FIFO queue
        self.server_busy = False
        self.packet_in_service = None
        
        # Statistics
        self.packets_arrived = 0
        self.packets_departed = 0
        self.total_delay = 0.0
        self.total_queue_delay = 0.0
        self.total_service_time = 0.0
        
        # For tracking queue length over time
        self.queue_length_history = []
        self.time_history = []
        
    def generate_exponential(self, mean):
        """Generate exponentially distributed random variable"""
        return np.random.exponential(mean)
    
    def schedule_event(self, event):
        """Add event to priority queue"""
        heapq.heappush(self.event_queue, event)
    
    def packet_arrival_event(self, packet):
        """Handle packet arrival"""
        self.packets_arrived += 1
        
        # Add to queue
        self.packet_queue.append(packet)
        
        # Record queue length
        self.queue_length_history.append(len(self.packet_queue))
        self.time_history.append(self.current_time)
        
        # If server is idle, start service immediately
        if not self.server_busy:
            self.start_service()
        
        # Schedule next arrival
        if self.packets_departed < self.run_length:
            next_arrival_time = self.current_time + self.generate_exponential(1.0 / self.arrival_rate)
            new_packet = Packet(arrival_time=next_arrival_time, 
                               size=self.generate_exponential(self.mean_packet_size))
            self.schedule_event(Event(next_arrival_time, EVENT_PACKET_ARRIVAL, new_packet))
    
    def start_service(self):
        """Start serving the next packet in queue"""
        if len(self.packet_queue) == 0:
            return
        
        # Get packet from queue
        packet = self.packet_queue.pop(0)
        self.server_busy = True
        self.packet_in_service = packet
        
        # Record when service starts
        packet.start_service_time = self.current_time
        
        # Calculate service time (transmission time = packet_size / link_rate)
        service_time = packet.size / self.link_rate
        
        # Schedule departure
        departure_time = self.current_time + service_time
        self.schedule_event(Event(departure_time, EVENT_PACKET_DEPARTURE, packet))
        
        # Record queue length after dequeue
        self.queue_length_history.append(len(self.packet_queue))
        self.time_history.append(self.current_time)
    
    def packet_departure_event(self, packet):
        """Handle packet departure"""
        self.packets_departed += 1
        
        # Record departure time
        packet.departure_time = self.current_time
        
        # Calculate statistics
        total_time_in_system = packet.departure_time - packet.arrival_time
        queue_delay = packet.start_service_time - packet.arrival_time
        service_time = packet.departure_time - packet.start_service_time
        
        self.total_delay += total_time_in_system
        self.total_queue_delay += queue_delay
        self.total_service_time += service_time
        
        # Server becomes idle
        self.server_busy = False
        self.packet_in_service = None
        
        # Start serving next packet if available
        if len(self.packet_queue) > 0:
            self.start_service()
        
        # Progress indicator
        if self.packets_departed % 10000 == 0:
            print(f"Progress: {self.packets_departed}/{self.run_length} packets processed")
    
    def run(self):
        """Run the simulation"""
        print(f"Starting simulation...")
        print(f"  Arrival rate (λ): {self.arrival_rate} packets/sec")
        print(f"  Mean packet size: {self.mean_packet_size} bits")
        print(f"  Link rate (C): {self.link_rate} bits/sec")
        print(f"  Utilization (ρ): {(self.arrival_rate * self.mean_packet_size) / self.link_rate:.4f}")
        print(f"  Target packets: {self.run_length}")
        print()
        
        # Schedule first arrival
        first_arrival_time = self.generate_exponential(1.0 / self.arrival_rate)
        first_packet = Packet(arrival_time=first_arrival_time, 
                            size=self.generate_exponential(self.mean_packet_size))
        self.schedule_event(Event(first_arrival_time, EVENT_PACKET_ARRIVAL, first_packet))
        
        # Event loop
        while self.packets_departed < self.run_length and len(self.event_queue) > 0:
            # Get next event
            event = heapq.heappop(self.event_queue)
            self.current_time = event.time
            
            # Process event
            if event.event_type == EVENT_PACKET_ARRIVAL:
                self.packet_arrival_event(event.packet)
            elif event.event_type == EVENT_PACKET_DEPARTURE:
                self.packet_departure_event(event.packet)
        
        print(f"\nSimulation complete!")
        print(f"Final time: {self.current_time:.2f} seconds")
    
    def get_results(self):
        """Calculate and return simulation results"""
        avg_delay = self.total_delay / self.packets_departed
        avg_queue_delay = self.total_queue_delay / self.packets_departed
        avg_service_time = self.total_service_time / self.packets_departed
        
        return {
            'packets_arrived': self.packets_arrived,
            'packets_departed': self.packets_departed,
            'avg_delay': avg_delay,
            'avg_queue_delay': avg_queue_delay,
            'avg_service_time': avg_service_time,
            'simulation_time': self.current_time
        }
    
    def print_results(self):
        """Print simulation results"""
        results = self.get_results()
        
        print("\n" + "="*60)
        print("SIMULATION RESULTS")
        print("="*60)
        print(f"Packets arrived:        {results['packets_arrived']}")
        print(f"Packets departed:       {results['packets_departed']}")
        print(f"Simulation time:        {results['simulation_time']:.2f} sec")
        print(f"\nAverage delay (W):      {results['avg_delay']:.6f} sec")
        print(f"Average queue delay:    {results['avg_queue_delay']:.6f} sec")
        print(f"Average service time:   {results['avg_service_time']:.6f} sec")
        print("="*60)


def mm1_theoretical(arrival_rate, mean_packet_size, link_rate):
    """
    Calculate M/M/1 theoretical values
    For M/M/1: W = 1/(mu - lambda) where mu = C/L (service rate)
    """
    rho = (arrival_rate * mean_packet_size) / link_rate
    service_rate = link_rate / mean_packet_size  # mu
    
    if rho >= 1.0:
        return None  # Unstable system
    
    avg_delay = 1.0 / (service_rate - arrival_rate)
    avg_queue_delay = rho / (service_rate - arrival_rate)
    avg_service_time = 1.0 / service_rate
    
    return {
        'avg_delay': avg_delay,
        'avg_queue_delay': avg_queue_delay,
        'avg_service_time': avg_service_time,
        'utilization': rho
    }


def run_experiment_sweep():
    """
    Run simulations across a range of utilizations and compare with M/M/1 theory
    """
    # Parameters
    link_rate = 1e6  # 1 Mbps
    mean_packet_size = 1000  # bits
    run_length = 100000  # packets
    
    # Vary arrival rate to get different utilizations
    utilizations = np.arange(0.1, 0.95, 0.05)
    
    results = []
    
    for rho in utilizations:
        # Calculate arrival rate for this utilization
        # rho = lambda * L / C, so lambda = rho * C / L
        arrival_rate = rho * link_rate / mean_packet_size
        
        print(f"\n{'='*60}")
        print(f"Running simulation for ρ = {rho:.2f}")
        print(f"{'='*60}")
        
        # Run simulation
        sim = PacketSwitchSimulator(
            arrival_rate=arrival_rate,
            mean_packet_size=mean_packet_size,
            link_rate=link_rate,
            run_length=run_length,
            random_seed=12345
        )
        sim.run()
        sim_results = sim.get_results()
        
        # Calculate theoretical values
        theory = mm1_theoretical(arrival_rate, mean_packet_size, link_rate)
        
        results.append({
            'utilization': rho,
            'sim_delay': sim_results['avg_delay'],
            'theory_delay': theory['avg_delay'],
            'sim_queue_delay': sim_results['avg_queue_delay'],
            'theory_queue_delay': theory['avg_queue_delay']
        })
        
        print(f"\nResults for ρ = {rho:.2f}:")
        print(f"  Simulation W = {sim_results['avg_delay']:.6f} sec")
        print(f"  Theoretical W = {theory['avg_delay']:.6f} sec")
        print(f"  Error = {abs(sim_results['avg_delay'] - theory['avg_delay']) / theory['avg_delay'] * 100:.2f}%")
    
    return results


def plot_results(results):
    """Plot simulation vs theoretical results"""
    utilizations = [r['utilization'] for r in results]
    sim_delays = [r['sim_delay'] for r in results]
    theory_delays = [r['theory_delay'] for r in results]
    
    plt.figure(figsize=(10, 6))
    plt.plot(utilizations, theory_delays, 'b-', linewidth=2, label='M/M/1 Theory')
    plt.plot(utilizations, sim_delays, 'ro', markersize=6, label='Simulation')
    plt.xlabel('Utilization (ρ)', fontsize=12)
    plt.ylabel('Average Delay (seconds)', fontsize=12)
    plt.title('M/M/1 Queue: Average Packet Delay vs Utilization', fontsize=14)
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.xlim(0, 1)
    plt.tight_layout()
    plt.savefig('part1_results.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("\nPlot saved as 'lab4_part1_results.png'")


if __name__ == "__main__":
    # Example: Run a single simulation
    print("Example: Single simulation run")
    print("="*60)
    
    sim = PacketSwitchSimulator(
        arrival_rate=400,      # packets/sec
        mean_packet_size=1000, # bits
        link_rate=1e6,         # 1 Mbps
        run_length=50000,
        random_seed=12345
    )
    
    sim.run()
    sim.print_results()
    
    # Compare with M/M/1 theory
    theory = mm1_theoretical(400, 1000, 1e6)
    print(f"\nM/M/1 Theoretical W = {theory['avg_delay']:.6f} sec")
    print(f"Utilization ρ = {theory['utilization']:.4f}")
    
    # Run full experiment sweep
    print("\n\n" + "="*60)
    print("Running full utilization sweep...")
    print("="*60)
    
    results = run_experiment_sweep()
    plot_results(results)
