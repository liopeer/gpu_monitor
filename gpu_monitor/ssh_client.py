"""Module for handling SSH connections and GPU metrics collection."""
import os
import paramiko
from paramiko import config
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class GPUMetrics:
    """Store GPU metrics for a single GPU."""
    index: int
    memory_used: int
    memory_total: int
    gpu_utilization: int

class SSHClient:
    """Handle SSH connections and command execution."""
    
    def __init__(self, hostname: str):
        self.hostname = hostname
        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Load SSH config
        self.ssh_config = paramiko.SSHConfig()
        user_config_file = os.path.expanduser("~/.ssh/config")
        if os.path.exists(user_config_file):
            with open(user_config_file) as f:
                self.ssh_config.parse(f)

    def get_connection_params(self) -> Dict:
        """Get connection parameters from SSH config."""
        config = self.ssh_config.lookup(self.hostname)
        return {
            'hostname': config.get('hostname', self.hostname),
            'username': config.get('user'),
            'port': int(config.get('port', 22)),
            'key_filename': config.get('identityfile', [None])[0],
        }

    def get_gpu_metrics(self) -> List[GPUMetrics]:
        """Connect to host and get GPU metrics using nvidia-smi."""
        try:
            # Use config-based connection
            conn_params = self.get_connection_params()
            self.client.connect(**{k: v for k, v in conn_params.items() if v is not None})
            
            cmd = "nvidia-smi --query-gpu=index,memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits"
            stdin, stdout, stderr = self.client.exec_command(cmd)
            
            metrics = []
            for line in stdout:
                idx, mem_used, mem_total, util = map(int, line.strip().split(', '))
                metrics.append(GPUMetrics(idx, mem_used, mem_total, util))
            
            return metrics
            
        except Exception as e:
            print(f"Error connecting to {self.hostname}: {str(e)}")
            return []
        finally:
            self.client.close()
