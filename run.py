import argparse
import simpy
import os

from simulator import Simulator

def main():
    # Creating ArgumentParser object
    parser = argparse.ArgumentParser(description='Simulation of a P2P Cryptocurrency Network')

    # Adding arguments
    parser.add_argument('--info', action="store_true", help='Generate info')
    parser.add_argument('--n', type=int, default=100, help='Number of peers in the network')
    parser.add_argument('--z0', type=int, default=50, help='Percentage of slow honest peers')
    parser.add_argument('--z1', type=int, default=100, help='Percentage of honest peers with Low CPU')
    parser.add_argument('--T_tx', type=int, default=10, help='Mean interarrival time between transactions (in ms)')
    parser.add_argument('--I', type=float, default=0.5, help='Mean interarrival time between blocks (in s)')
    parser.add_argument('--T_sim', type=int, default=10, help='Simulation time (in s)')
    parser.add_argument('--zeta1', type=int, default=40, help='Percentage of mining power of adversary-1')
    parser.add_argument('--zeta2', type=int, default=30, help='Percentage of mining power of adversary-2')
    parser.add_argument('--output_dir', type=str, default="output", help='Output directory')
    # note I is in secs

    # Parse the command-line arguments
    args = parser.parse_args()

    # Sanity checks
    if args.n < 2:
        print("Number of peers in the network should be at least 2")
        exit(1)
    if args.z0 < 0 or args.z0 > 100:
        print("Percentage of slow peers should be between 0 and 100")
        exit(1)
    if args.z1 < 0 or args.z1 > 100:
        print("Percentage of peers with Low CPU should be between 0 and 100")
        exit(1)
    if args.T_tx <= 0:
        print("Mean interarrival time between transactions should be positive")
        exit(1)
    if args.I <= 0:
        print("Mean interarrival time between blocks should be positive")
        exit(1)
    if args.T_sim <= 0:
        print("Simulation time should be positive")
        exit(1)
    if args.zeta1 < 0 or args.zeta1 > 100:
        print("Percentage of mining power of adversary-1 should be between 0 and 100")
        exit(1)
    if args.zeta2 < 0 or args.zeta2 > 100:
        print("Percentage of mining power of adversary-2 should be between 0 and 100")
        exit(1)
    if args.zeta1 + args.zeta2 > 100:
        print("Sum of the percentage of mining power of adversary-1 and adversary-2 should be at most 100")
        exit(1)

    # env = simpy.Environment(factor=0.001)
    env = simpy.Environment()

    # Simulating the network
    sim = Simulator(args.n, args.z0, args.z1, args.zeta1, args.zeta2, args.T_tx, args.I, args.T_sim, env)
    
    # Setting simulation entities
    sim.start_simulation()

    # Starting simulation
    env.run(until=args.T_sim * 1000)

    print("Simulation finished")

    # Make output directory if it doesn't exist
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    # Printing the blockchain of all peers
    sim.print_blockchain(args.output_dir)

    # Generating miner info and simulation's parameters
    if args.info:
        sim.generate_info(f"{args.output_dir}/info.txt")

if __name__ == "__main__":
    main()
