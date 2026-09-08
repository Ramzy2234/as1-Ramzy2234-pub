logs = [
    "ERROR Disk failure",
    "INFO User login",
    "WARNING High memory usage",
    "INFO File saved",
    "ERROR Network timeout"
]

counts = {"ERROR": 0, "INFO": 0, "WARNING": 0}

for log in logs:
    for key in counts:
        if log.startswith(key):
            counts[key] += 1

print("Log summary:")
for k, v in counts.items():
    print(k, v)
