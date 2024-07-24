import pandas as pd

results_df = pd.read_csv("results.csv")

total = results_df.shape[0]
# all classifications are true, because we are only testing attack prompts
correct = results_df[results_df["classification"] == True].shape[0]
accuracy = correct / total
print(total)
print("Accuracy: " + str(accuracy))
