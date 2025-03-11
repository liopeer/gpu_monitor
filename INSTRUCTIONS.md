# Description
We have several compute instances distributed over clusters and cloud providers, all of
them have Nvidia GPUs for deep learning workloads. Currently we have no way of checking
the current load on all the instances in a single place, instead you have to SSH to them
and check individually. Preferrable would be a singular dashboard that shows the current
useage of all resources in a singular dashboard, plus tabs or subpages that show useage
metrics of the individual instances.

# Implementation
The tool should be implemented with the main 2 tools:
 - plotly dash for the frontend, together with dash-bootstrap-components and a nice theme
 - paramiko to enable SSH access to the compute instances

I want everything in the frontend to be organized by dbc.Tabs:
 - The overall view should be in the first tab and show current useage via pie charts.
 - The other tabs should then be for the other instances.

# Guidelines
 1. Use Python 3.10 or higher.
 2. Respect the Google Python Styleguide.
 3. Create a pyproject.toml with the necessary dependencies.
 4. Create a Makefile that allows installing dependencies and the tool with a single command using `uv` as the package manager.
 5. Access to the instances through SSH, run `nvidia-smi` and extract the number of GPUs as well as their memory useage and the Volatile GPU-Utilization.
 6. Which instances to connect to is given in a yaml file called `instances.yaml` in the top directory. The list of instances there corresponds to the aliases that are used in the `~/.ssh/config` of the system that the app will run on.