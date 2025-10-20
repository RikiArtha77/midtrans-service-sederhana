import subprocess

services = [
    ("main_server", 5000),
    ("entity_service", 5001),
    ("status_service", 5002)
]

processes = []
for service, port in services:
    cmd = f"uvicorn {service}.app:app --port {port} --reload"
    print(f"Starting {service} on port {port}...")
    processes.append(subprocess.Popen(cmd, shell=True))

print("All services running. Press Ctrl+C to stop.")
try:
    for p in processes:
        p.wait()
except KeyboardInterrupt:
    print("Stopping all services...")
    for p in processes:
        p.terminate()
