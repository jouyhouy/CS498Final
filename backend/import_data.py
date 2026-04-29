import kagglehub

# Download latest version
path = kagglehub.dataset_download("patrickjoan/twitter-data-from-2018-eurovision-final")

print("Path to dataset files:", path)