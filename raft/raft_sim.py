from raft_node import RaftNode
import subprocess
import time

# Function to create a new tmux session with a given name and command
def create_tmux_session(session_name, window_name, command):
    tmux_command = f"tmux new-session -d -s {session_name} -n {window_name} '{command}'"
    subprocess.run(tmux_command, shell=True)

def simulate_leader_election(node):
    # Simulate leader election
    node.start_election()
    time.sleep(5)  # Wait for leader election to complete

    # Check if this node became the leader
    if node.state == 'leader':
        # Print the state of the node and the current leader
        print(f"Node {node.node_id} state: {node.state}")
        print(f"Node {node.node_id} current leader: {node.node_id}")
    else:
        # Print the state of the node and that it's not the leader
        print(f"Node {node.node_id} state: {node.state}")
        print(f"Node {node.node_id} is not the leader")

    # Check if any other node became the leader
    for peer in node.peers:
        if peer.current_leader and peer.current_leader != node.node_id:
            # Another node became the leader, print the information
            print(f"Node {node.node_id} current leader: {peer.current_leader}")
            break
    else:
        # No other node became the leader, print the information
        print(f"Node {node.node_id} current leader: {node.node_id}")


# Create Raft nodes
node1 = RaftNode(node_id=1, peers=[])
node2 = RaftNode(node_id=2, peers=[])
node3 = RaftNode(node_id=3, peers=[])

# Configure peers for each node
node1.peers = [node2, node3]
node2.peers = [node1, node3]
node3.peers = [node1, node2]

# Start a separate tmux session for each node
create_tmux_session("Node1Session", "Node 1", f"python3 raft_node.py 1")
create_tmux_session("Node2Session", "Node 2", f"python3 raft_node.py 2")
create_tmux_session("Node3Session", "Node 3", f"python3 raft_node.py 3")

# Simulate leader election for each node
simulate_leader_election(node1)
simulate_leader_election(node2)
simulate_leader_election(node3)
