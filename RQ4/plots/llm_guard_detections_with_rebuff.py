import matplotlib.pyplot as plt
import numpy as np


bar_color0 = "#C0C0C0"
bar_color1 = "#7BC8F6"
bar_color2 = "#EF4026"

# Data
models = ['gpt-3.5-turbo-1106', 'gpt-4-1106-preview']
versions = ['Results Only', 'Question + Results', 'Question + \nResults + Thought', 'Rebuff']

# Detection percentages
detections = {
    'gpt-3.5-turbo-1106': [0.55, 0.8833333333333333, 1.0, 0.7833333333333333],
    'gpt-4-1106-preview': [0.9833333333333333, 0.95, 0.9333333333333333, 0.8]  # None for the last version as it's not tested
}

# Creating a bar chart
fig, ax = plt.subplots(figsize=(6,3.4))

# Setting the positions and width for the bars
pos = np.arange(len(versions))
bar_width = 0.35

# Plotting the bars for each model, handling None values
for i, model in enumerate(models):
    model_detections = [detection if detection is not None else 0 for detection in detections[model]]
    if model == 'gpt-3.5-turbo-1106':
        ax.bar(pos + i * bar_width, model_detections, bar_width, label=model, color=bar_color0)
    elif model == 'gpt-4-1106-preview':
        ax.bar(pos + i * bar_width, model_detections, bar_width, label=model, color=bar_color1, hatch='///', edgecolor="Blue")

# Adding labels, title, and legend
ax.set_xlabel('LLM Guard Prompt Configuration', labelpad=8)
# plt.label_params(pad=-20)
ax.set_ylabel('Attack Detection Percentage')
ax.set_xticks(pos + bar_width / 2)
ax.set_xticklabels(versions)
# ax.legend()
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.35), ncol=2)
ax.spines[['right', 'top']].set_visible(False)

# Adding percentage labels on bars
for i in range(len(versions)):
    for j in range(len(models)):
        detection = detections[models[j]][i]
        if detection is not None:
            ax.text(i + j * bar_width, detection + 0.02, f'{detection:.0%}', rotation=0, ha='center')

# Show the plot
plt.xticks(rotation=0, ha="center")
# plt.tick_params(pad=-20)

fig.tight_layout()
plt.subplots_adjust(wspace=0.12,
                    hspace=0.12)
plt.margins(x=0.01, y=0.06)
#plt.show()
plt.savefig("llm_guard_detections_with_rebuff.pdf")
