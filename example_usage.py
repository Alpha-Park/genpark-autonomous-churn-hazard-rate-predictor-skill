from client import AutonomousChurnHazardRatePredictorClient
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

def main():
    client = AutonomousChurnHazardRatePredictorClient()
    print("=== AUTONOMOUS CHURN HAZARD RATE PREDICTOR ===")
    
    customers = [
        {
            "id": "CUST-ENTERPRISE-01", "tenure": 14, "mrr": 4500.0,
            "metrics": {"login_frequency_drop_pct": 65, "support_tickets_open_p1": 2, "nps_detractor_flag": True, "payment_failure_count": 1, "feature_adoption_ratio": 0.25}
        },
        {
            "id": "CUST-MIDMARKET-02", "tenure": 8, "mrr": 1200.0,
            "metrics": {"login_frequency_drop_pct": 20, "support_tickets_open_p1": 0, "nps_detractor_flag": False, "payment_failure_count": 0, "feature_adoption_ratio": 0.85}
        }
    ]
    
    for c in customers:
        res = client.predict_churn_hazard(c["id"], c["tenure"], c["mrr"], c["metrics"])
        print()
        print(f"Account: {res['customer_id']} (MRR: ${res['monthly_recurring_revenue']:,.2f})")
        print(f"  - 30-Day Churn Risk: {res['churn_probability_30d']*100:.1f}% | 90-Day Churn Risk: {res['churn_probability_90d']*100:.1f}%")
        print(f"  - LTV at Risk: ${res['projected_ltv_at_risk']:,.2f} | Half-life: {res['projected_half_life_months']} months")
        print(f"  - Action Playbook: {res['recommended_retention_action']}")
        print(f"  - Offer: {res['recommended_retention_offer']}")

if __name__ == "__main__":
    main()
