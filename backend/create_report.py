import csv
from pathlib import Path

results = [
    {
        "Model": "Logistic Regression",
        "Accuracy": 0.8300,
        "Balanced Accuracy": 0.8269,
        "Macro Precision": 0.6700,
        "Macro Recall": 0.8300,
        "Macro F1": 0.7000,
    },
    {
        "Model": "Random Forest",
        "Accuracy": 0.9300,
        "Balanced Accuracy": 0.7266,
        "Macro Precision": 0.8700,
        "Macro Recall": 0.7300,
        "Macro F1": 0.7800,
    },
    {
        "Model": "SVM",
        "Accuracy": 0.9200,
        "Balanced Accuracy": 0.8413,
        "Macro Precision": 0.7900,
        "Macro Recall": 0.8450,
        "Macro F1": 0.8150,
    },
]

report_path = Path("model_evaluation_report.csv")

with report_path.open("w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)

print("Evaluation report created:", report_path.resolve())