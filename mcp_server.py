import sys, json
from client import AutonomousChurnHazardRatePredictorClient
sys.stdout.reconfigure(encoding='utf-8')

def handle_mcp():
    client = AutonomousChurnHazardRatePredictorClient()
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print(json.dumps({"status": "ready", "skill": "genpark-autonomous-churn-hazard-rate-predictor-skill"}))
        return
    req = json.loads(sys.stdin.read() or "{}")
    cid = req.get("customer_id", "CUST_DEFAULT")
    tenure = req.get("tenure_months", 12)
    mrr = req.get("mrr", 1000.0)
    metrics = req.get("behavioral_metrics", {})
    res = client.predict_churn_hazard(cid, tenure, mrr, metrics)
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    handle_mcp()
