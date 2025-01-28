import matplotlib.pyplot as plt
import numpy as np
import os
import json

bar_color0 = "#C0C0C0"
bar_color1 = "#7BC8F6"
bar_color2 = "#EF4026"

# Data
methods = ["Without\nDeBERTa", "With DeBERTa\nEntire Results", "With DeBERTa\nRow-wise"]
# total_llm_guard_time = [147.20827627182007, 64.11212468147278, 60.29994535446167]
# total_classifier_time = [0, 3.346440315246582, 3.779470205307007]
# total_exec_time = [147.30424880981445, 67.52971458435059, 64.1471016407013]
# llm_guard_hits = [60, 26, 22]

file_paths = [
    "question_results_thought_stats_gpt-3.5-turbo-1106.json",
    "question_results_thought_deberta_full_stats_gpt-3.5-turbo-1106.json",
    "question_results_thought_deberta_row_stats_gpt-3.5-turbo-1106.json"
]
base_path = '/app/output'

# Function to read JSON files and extract values
def read_json_values(file_name):
    file_path = os.path.join(base_path, file_name)
    with open(file_path, 'r') as file:
        return json.load(file)

# Read values from JSON files
data = [read_json_values(file_path) for file_path in file_paths]

# Extract values
total_llm_guard_time = [d["total_llm_guard_time_taken"] for d in data]
total_classifier_time = [d["total_classifier_time_taken"] for d in data]
total_exec_time = [d["total_time_taken"] for d in data]
llm_guard_hits = [d["llm_guard_hits"] for d in data]

bar_width = 0.35
bar_positions = np.arange(len(methods))

fig, ax = plt.subplots(figsize=(5,2.8))
ax2 = ax.twinx()

y_max = max(total_exec_time) * 1.15  # X% more than the max value

ax.set_ylim(0, y_max)
ax.spines[['top']].set_visible(False)
ax2.spines[['top']].set_visible(False)

# Line for LLM Guard Hits
line2, = ax2.plot(methods, llm_guard_hits, label='LLM Calls', color=bar_color2, zorder=1, marker='.')
ax2.set_ylim(bottom=0)

# Bars for LLM Guard Time and Classifier Time
bar_llm_guard = ax.bar(bar_positions, total_llm_guard_time, bar_width, label='Total LLM Guard Time (s)', color=bar_color0)
bar_classifier = ax.bar(bar_positions, total_classifier_time, bar_width, bottom=total_llm_guard_time,
                        label='Total DeBERTa Time (s)', color=bar_color1, )#hatch='///', edgecolor="Blue")

ax.legend(fontsize=10)
ax2.legend(fontsize=10, loc='upper right', bbox_to_anchor=(1, 0.75), ncol=2)


# Adding total time taken above each bar
for idx, rect in enumerate(bar_llm_guard):
    height = total_exec_time[idx]
    ax.text(rect.get_x() + rect.get_width()/2., 1.01*height, f'{height:.2f}', zorder=2, ha='center', va='bottom')



# Making the graph more readable
ax.set_xlabel('Optimization Method', labelpad=10)
ax.set_ylabel('Total Time (s)')
ax.set_xticks(bar_positions)
ax.set_xticklabels(methods)
ax2.set_ylabel('LLM Calls')


fig.tight_layout()
plt.subplots_adjust(wspace=0.12,
                    hspace=0.12)
plt.margins(x=0.01, y=0.06)
#plt.show()



file_path = os.path.join(base_path, "llm_guard_deberta_hits.pdf")
plt.savefig(file_path)
