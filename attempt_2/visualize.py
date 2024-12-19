import matplotlib
matplotlib.use('TkAgg')  # Use interactive backend

import matplotlib.pyplot as plt
import pickle
import neat
import os

def draw_net(genome, config, node_names=None, show_disabled=True):
    inputs = config.genome_config.input_keys
    outputs = config.genome_config.output_keys

    if node_names is None:
        node_names = {}

    # Enable interactive mode
    plt.ion()

    # Define node positions
    positions = {}
    max_nodes = max(len(inputs), len(outputs))

    # Dynamic figure size calculation
    fig_height = max(6, max_nodes * 1.2)
    fig_width = 10

    # Assign input node positions
    for i, node in enumerate(inputs):
        positions[node] = (0, -i)

    # Assign output node positions
    for i, node in enumerate(outputs):
        positions[node] = (fig_width - 2, -i)

    # Assign hidden nodes
    hidden_nodes = set(genome.nodes.keys()) - set(inputs) - set(outputs)
    for i, node in enumerate(hidden_nodes):
        layer_x = fig_width / 2  # Middle of the figure
        positions[node] = (layer_x, -i - max_nodes)

    # Draw the network using matplotlib
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.set_title("Worst Bird Neural Network")
    ax.axis("off")

    # Auto-adjust axis limits
    ax.set_xlim(-1, fig_width + 1)
    ax.set_ylim(-fig_height - 1, 1)

    # Draw nodes
    for node, (x, y) in positions.items():
        color = (
            'lightblue' if node in inputs else
            'lightgreen' if node in outputs else
            'lightcoral'
        )
        ax.text(x, y, node_names.get(node, str(node)), 
                fontsize=12, ha='center', va='center',
                bbox=dict(facecolor=color, edgecolor='black'))

    # Draw straight connections
    for cg in genome.connections.values():
        input_node, output_node = cg.key
        if cg.enabled or show_disabled:
            input_pos = positions[input_node]
            output_pos = positions[output_node]
            style = 'solid' if cg.enabled else 'dashed'
            color = 'black' if cg.enabled else 'red'
            
            # Draw connection (straight line)
            ax.annotate(
                '', 
                xy=output_pos, xytext=input_pos,
                arrowprops=dict(
                    arrowstyle="->", color=color,
                    lw=2, linestyle=style
                )
            )

            # Display weights (moved up by 0.2 units)
            mid_x = (input_pos[0] + output_pos[0]) / 2
            mid_y = (input_pos[1] + output_pos[1]) / 2 + 0.2
            ax.text(mid_x, mid_y, f'{cg.weight:.2f}', fontsize=8, color="red")

    # Show the plot and keep it interactive
    fig.canvas.draw()
    fig.canvas.flush_events()
    plt.show(block=True)


# Load the best bird's genome
with open("best_bird.pkl", "rb") as f:
    best_data = pickle.load(f)

best_genome = best_data['genome']
node_names = {
    -1: "Bird Y", 
    -2: "Top Pipe Y", 
    -3: "Bottom Pipe Y", 
    0: "Jump Output"
}

# Load the configuration file
local_directory = os.path.dirname(__file__)
config_file = os.path.join(local_directory, "config-feedforward.txt")
config = neat.config.Config(
    neat.DefaultGenome, neat.DefaultReproduction, 
    neat.DefaultSpeciesSet, neat.DefaultStagnation, 
    config_file
)

# Visualize the neural network
draw_net(best_genome, config, node_names=node_names)
