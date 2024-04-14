# CS765-Discrete-Event-Simulator

## Team Members 
| Name | Roll Number |
| --- | --- |
|Guramrit Singh | 210050061|
|Isha Arora | 210050070|
|Karan Godara | 210050082|

## Running instructions
- The simulator and analyser are written in Python3

### Simulator
- The simulator is run by run.py
- To see the usage of the simulator, run the following command:
```python3 run.py --help```
- The above command will display the following:
```
usage: run.py [-h] [--info] [--n N] [--z0 Z0] [--z1 Z1] [--T_tx T_TX] [--I I] [--T_sim T_SIM] [--zeta1 ZETA1] [--zeta2 ZETA2] [--output_dir OUTPUT_DIR]

Simulation of a P2P Cryptocurrency Network

options:
  -h, --help                  show this help message and exit
  --info                      Generate info
  --n N                       Number of peers in the network
  --z0 Z0                     Percentage of slow honest peers
  --z1 Z1                     Percentage of honest peers with Low CPU
  --T_tx T_TX                 Mean interarrival time between transactions (in ms)
  --I I                       Mean interarrival time between blocks (in s)
  --T_sim T_SIM               Simulation time (in s)
  --zeta1 ZETA1               Percentage of mining power of adversary-1
  --zeta2 ZETA2               Percentage of mining power of adversary-2
  --output_dir OUTPUT_DIR     Output directory
```
- Options are given default values, so if you want to run the simulator with the default values, you can simply run:
```python3 run.py```
- The default values are:
    - n: 100
    - z0: 50
    - z1: 100
    - T_tx: 10
    - I: 0.5
    - T_sim: 10
    - zeta1: 40
    - zeta2: 30
    - output_dir: output
- The output of the simulator will be stored in the output directory. The following files will be generated:
    - blockchain_{i}.txt: The blockchain of the i-th miner, 1<=i<=n
    - info.txt: The info about the miners if --info flag is used, this file is required for the analyser

### Analyser
- The analysis of simulator is done by analyser.py
- To see the usage of the analyser, run the following command:
```python3 analyser.py --help```
- The above command will display the following:
```
usage: analyser.py [-h] [--blkchain BLKCHAIN] [--info_file INFO_FILE] [--only_plot] [--output_dir OUTPUT_DIR] [--show_private] [--color_same] [--color_miner COLOR_MINER]

Analyser for the blockchain

options:
  -h, --help                  show this help message and exit
  --blkchain BLKCHAIN         File containing the blockchain
  --info_file INFO_FILE       File containing info about miners
  --only_plot                 Only plot blockchain tree and exit
  --output_dir OUTPUT_DIR     Output directory
  --show_private              Show private chain as well in the plot
  --color_same                Color all nodes same regardless of attacker or honest miner
  --color_miner COLOR_MINER   Color distinctly the blocks mined by the miner with this ID, works only if --color-same is not given

```
- Options are given default values, so if you want to run the analyser with the default values, you can simply run:
```python3 analyser.py```
- The default values are:
  - blkchain: output/blockchain_1.txt
  - info_file: output/info.txt
  - output_dir: output
  - color_miner: -1 (Colors distinctly the blocks mined by Attacker-1, Attacker-2 and honest miners)
- The output of the simulator will be stored in the output directory. The following files will be generated:
    - blockchain.png: The blockchain tree corresponding to the blockchain file
    - final_stats.txt: The final stats of the blockchain if --only_plot flag is not used

## Directory Structure
- This directory contains the following files:
    - [run.py](run.py): The main file to run the simulator
    - [analyser.py](analyser.py): The analyser for the blockchain
    - [README.md](README.md): This README file
    - [Report.pdf](Report.pdf): The report of this assignment
    - [Design_Document.pdf](Design_Document.pdf): The design document of this assignment
    - [simulator.py](simulator.py): The simulator class
    - [peer.py](peer.py): The peer class denoting each peer (miner) in the network
    - [attacker.py](attacker.py): The attacker class denoting the attacker in the network
    - [honest.py](honest.py): The honest class denoting the honest peers in the network
    - [peer_link.py](peer_link.py): The peer link class denoting the link between two peers
    - [block.py](block.py): The blocks class denoting the blocks in the blockchain
    - [transaction.py](transaction.py): The transaction class denoting the transactions in the blockchain
    - [tree.py](tree.py): The tree class denoting the blockchain tree
    - [results](results): This directory contains the results of the simulation and analysis that we have used in the report
 
## Libraries used and their versions
- networkx (3.2)
- matplotlib (3.8.0)
- pydot (2.0.0)
- numpy (1.26.1)
- simpy (4.1.1)
