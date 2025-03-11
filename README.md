# GPU Monitor

A dashboard for monitoring GPU utilization across multiple compute instances.

## Prerequisites

- Python 3.10 or higher
- `uv` package manager
- SSH access to your GPU instances configured in `~/.ssh/config`
- NVIDIA GPUs on the target machines

## Installation

1. Clone the repository:
```bash
git clone https://github.com/lionelpeer/gpu_monitor.git
cd gpu_monitor
```

2. Install dependencies using Make:
```bash
make install
```

## Configuration

1. Create an `instances.yaml` file in the project root:
```yaml
instances:
  - gpu-server-1
  - gpu-server-2
  - cloud-instance-1
```

2. Ensure your `~/.ssh/config` contains the corresponding host entries:
```
Host gpu-server-1
    HostName 192.168.1.100
    User username
    IdentityFile ~/.ssh/id_rsa

Host gpu-server-2
    HostName gpu2.example.com
    User username
    IdentityFile ~/.ssh/id_rsa

Host cloud-instance-1
    HostName 34.123.45.67
    User ubuntu
    IdentityFile ~/.ssh/cloud-key.pem
```

The instances listed in `instances.yaml` must match the `Host` names in your SSH config.

## Usage

Start the dashboard:
```bash
make run
```

Access the dashboard at http://localhost:8050

The dashboard will:
- Refresh every 5 seconds
- Show fleet-wide average GPU usage in the `Overview` tab
- Provide detailed metrics for each instance in separate tabs