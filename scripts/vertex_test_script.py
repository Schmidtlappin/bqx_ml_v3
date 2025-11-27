
import sys
import json
from datetime import datetime

print("Vertex AI Training Job Started")
print(f"Arguments: {sys.argv}")
print(f"Timestamp: {datetime.now().isoformat()}")

# For now, just test the job submission
pair = sys.argv[1] if len(sys.argv) > 1 else "eurusd"
window = sys.argv[2] if len(sys.argv) > 2 else "45"

print(f"Training model for {pair} with window {window}")
print("Job completed successfully (test mode)")

# Save a test result
result = {
    "pair": pair,
    "window": window,
    "status": "test_complete",
    "timestamp": datetime.now().isoformat()
}

print(json.dumps(result, indent=2))
