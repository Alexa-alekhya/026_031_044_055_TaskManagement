import random
import threading

class RaftNode:
    def __init__(self, node_id, peers):
        self.node_id = node_id
        self.peers = peers
        self.current_term = 0
        self.voted_for = None
        self.log = []
        self.commit_index = 0
        self.last_applied = 0
        self.state = 'follower'
        self.timeout = self.generate_random_timeout()
        self.current_leader = None  # Initialize current_leader attribute

    def generate_random_timeout(self):
        return random.uniform(0.15, 0.3)  # Randomize timeout between 150ms and 300ms

    def reset_timeout(self):
        self.timeout = self.generate_random_timeout()

    def start_timer(self):
        self.timer = threading.Timer(self.timeout, self.handle_timeout)
        self.timer.start()

    def stop_timer(self):
        self.timer.cancel()

    def handle_timeout(self):
        if self.state == 'follower':
            self.start_election()

    def request_vote(self, candidate_id, term, last_log_index, last_log_term):
        if term < self.current_term:
            return False
        if (self.voted_for is None or self.voted_for == candidate_id) and \
                (last_log_index >= len(self.log) - 1 or last_log_term == self.log[last_log_index]['term']):
            self.voted_for = candidate_id
            self.reset_timeout()
            return True
        return False

    def append_entries(self, leader_id, term, prev_log_index, prev_log_term, entries, leader_commit):
        if term < self.current_term:
            return False
        if prev_log_index > len(self.log) - 1 or self.log[prev_log_index]['term'] != prev_log_term:
            return False
        # Append new entries to the log
        self.log.extend(entries)
        self.commit_index = min(leader_commit, len(self.log) - 1)
        self.reset_timeout()
        return True

    def start_election(self):
        self.current_term += 1
        self.state = 'candidate'
        self.voted_for = self.node_id
        # Request votes from other nodes
        votes_received = 1  # Vote for self
        if self.log:
            last_log_index = len(self.log) - 1
            last_log_term = self.log[-1]['term']
        else:
            last_log_index = -1
            last_log_term = -1
        for peer in self.peers:
            if peer.request_vote(self.node_id, self.current_term, last_log_index, last_log_term):
                votes_received += 1
                if votes_received > len(self.peers) // 2:
                    # Check if another node already claimed leadership
                    for other_peer in self.peers:
                        if other_peer.current_leader and other_peer.current_leader != self.node_id:
                            # Another node has become leader, exit election
                            self.state = 'follower'
                            return
                    # No other node claimed leadership, become leader
                    self.state = 'leader'
                    self.current_leader = self.node_id
                    break
        else:
            self.state = 'follower'
        self.reset_timeout()
        self.start_timer()

    def handle_rpc(self, sender_id, rpc_type, **kwargs):
        pass  # Handle RPCs between nodes

    def send_rpc(self, receiver_id, rpc_type, **kwargs):
        pass  # Simulate network communication between nodes
