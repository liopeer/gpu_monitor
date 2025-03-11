"""Main dashboard application using Dash."""
import yaml
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from .ssh_client import SSHClient
import pandas as pd
from statistics import mean

# Load instance configuration
with open("instances.yaml") as f:
    config = yaml.safe_load(f)
    INSTANCES = config["instances"]

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

def calculate_mean_metrics(metrics_dict):
    """Calculate mean GPU metrics across all instances."""
    all_memory_used = []
    all_memory_total = []
    all_utilization = []
    
    for instance, metrics in metrics_dict.items():
        for gpu in metrics:
            all_memory_used.append(gpu.memory_used)
            all_memory_total.append(gpu.memory_total)
            all_utilization.append(gpu.gpu_utilization)
    
    if not all_memory_used:
        return None
    
    return {
        'mean_memory_used': mean(all_memory_used),
        'mean_memory_total': mean(all_memory_total),
        'mean_utilization': mean(all_utilization)
    }

def create_gpu_charts(title, memory_used, memory_total, utilization):
    """Create memory and utilization pie charts with consistent styling."""
    charts = []
    
    # Memory usage pie chart
    mem_fig = go.Figure(data=[go.Pie(
        labels=['Used', 'Free'],
        values=[memory_used, memory_total - memory_used],
        hole=.3
    )])
    mem_fig.update_layout(
        title=f"{title} - Memory Usage",
        height=300
    )
    
    # Utilization pie chart
    util_fig = go.Figure(data=[go.Pie(
        labels=['Used', 'Free'],
        values=[utilization, 100 - utilization],
        hole=.3
    )])
    util_fig.update_layout(
        title=f"{title} - GPU Utilization",
        height=300
    )
    
    return [mem_fig, util_fig]

def get_idle_gpus(metrics_dict, threshold=5):
    """Get GPUs with memory utilization below threshold."""
    idle_gpus = []
    for instance, metrics in metrics_dict.items():
        if not metrics:
            continue
        idle_count = sum(1 for gpu in metrics if (gpu.memory_used / gpu.memory_total * 100) < threshold)
        if idle_count > 0:
            total_gpus = len(metrics)
            model = metrics[0].model  # Assuming all GPUs on one instance are same model
            idle_gpus.append({
                'instance': instance,
                'idle_ratio': f"{idle_count}/{total_gpus}",
                'model': model
            })
    return idle_gpus

# Create tabs for each instance
tabs = [dbc.Tab(label="Overview", tab_id="overview")]
tabs.extend([
    dbc.Tab(label=instance, tab_id=instance)
    for instance in INSTANCES
])

app.layout = dbc.Container([
    html.H1("GPU Monitor Dashboard"),
    dbc.Tabs(tabs, id="tabs", active_tab="overview"),
    html.Div(id="tab-content"),
    dcc.Interval(id='interval-component', interval=30*1000)  # 5 second refresh
])

@app.callback(
    Output("tab-content", "children"),
    [Input("tabs", "active_tab"),
     Input("interval-component", "n_intervals")]
)
def render_tab_content(active_tab, n):
    """Update tab content based on selection and interval."""
    metrics_dict = {}
    
    # Collect metrics from all instances
    for instance in INSTANCES:
        try:
            client = SSHClient(instance)
            metrics_dict[instance] = client.get_gpu_metrics()
        except Exception as e:
            print(f"Error connecting to {instance}: {e}")
            metrics_dict[instance] = []

    if active_tab == "overview":
        mean_metrics = calculate_mean_metrics(metrics_dict)
        if not mean_metrics:
            return html.Div("No data available from any instance")
        
        # Create pie charts
        figures = create_gpu_charts(
            "Fleet Average",
            mean_metrics['mean_memory_used'],
            mean_metrics['mean_memory_total'],
            mean_metrics['mean_utilization']
        )
        
        # Get idle GPUs and create table
        idle_gpus = get_idle_gpus(metrics_dict)
        idle_table = dbc.Table([
            html.Thead([
                html.Tr([
                    html.Th("Instance"),
                    html.Th("Idle/Total GPUs"),
                    html.Th("GPU Model")
                ])
            ]),
            html.Tbody([
                html.Tr([
                    html.Td(gpu['instance']),
                    html.Td(gpu['idle_ratio']),
                    html.Td(gpu['model'])
                ]) for gpu in idle_gpus
            ])
        ], bordered=True, dark=True, hover=True)
        
        return dbc.Container([
            dbc.Row([
                dbc.Col(html.H2("Fleet-wide GPU Usage", className="text-center"), width=12)
            ]),
            dbc.Row([
                dbc.Col(dcc.Graph(figure=fig), width=6)
                for fig in figures
            ]),
            dbc.Row([
                dbc.Col(html.H3("Idle GPUs (< 5% Memory Usage)", className="text-center mt-4"), width=12)
            ]),
            dbc.Row([
                dbc.Col(idle_table, width=12)
            ])
        ])
    else:
        # Individual instance view
        instance_metrics = metrics_dict.get(active_tab, [])
        if not instance_metrics:
            return html.Div(f"No data available for {active_tab}")
        
        all_figures = []
        for gpu in instance_metrics:
            figures = create_gpu_charts(
                f"GPU {gpu.index}",
                gpu.memory_used,
                gpu.memory_total,
                gpu.gpu_utilization
            )
            all_figures.extend(figures)
        
        return dbc.Container([
            dbc.Row([
                dbc.Col(html.H2(f"{active_tab} GPU Usage", className="text-center"), width=12)
            ]),
            dbc.Row([
                dbc.Col(dcc.Graph(figure=fig), width=6)
                for fig in all_figures
            ])
        ])

if __name__ == "__main__":
    app.run_server(debug=True)
