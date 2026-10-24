import math, sys
sys.stdout.reconfigure(encoding='utf-8')

class AutonomousChurnHazardRatePredictorClient:
    """
    Parametric Weibull hazard and Cox proportional risk calculator for B2B/B2C subscriptions.
    Calculates 30/60/90-day survival probability, expected churn half-life, and triggers retention plays.
    """
    def __init__(self, base_lambda=0.015, weibull_beta=1.25):
        self.base_lambda = base_lambda # baseline scale parameter
        self.beta = weibull_beta       # shape parameter (>1 implies aging hazard)

    def calculate_hazard_covariates(self, metrics):
        # Coefficients for proportional risk multiplier
        weights = {
            "login_frequency_drop_pct": 0.018, # e.g. 50% drop -> 0.90
            "support_tickets_open_p1": 0.45,   # each open blocker ticket -> +45%
            "nps_detractor_flag": 0.55,        # detractor -> +55%
            "payment_failure_count": 0.35,     # failed billing charges
            "feature_adoption_ratio": -0.60    # high adoption reduces hazard
        }
        log_risk = 0.0
        log_risk += metrics.get("login_frequency_drop_pct", 0) * weights["login_frequency_drop_pct"]
        log_risk += metrics.get("support_tickets_open_p1", 0) * weights["support_tickets_open_p1"]
        log_risk += (1.0 if metrics.get("nps_detractor_flag", False) else 0.0) * weights["nps_detractor_flag"]
        log_risk += metrics.get("payment_failure_count", 0) * weights["payment_failure_count"]
        log_risk += metrics.get("feature_adoption_ratio", 0.5) * weights["feature_adoption_ratio"]
        
        return math.exp(max(-2.0, min(3.0, log_risk)))

    def weibull_survival(self, t, effective_lambda):
        # S(t) = exp(-(effective_lambda * t)^beta)
        val = (effective_lambda * t) ** self.beta
        return math.exp(-val)

    def predict_churn_hazard(self, customer_id, tenure_months, mrr, behavioral_metrics):
        risk_multiplier = self.calculate_hazard_covariates(behavioral_metrics)
        effective_lambda = self.base_lambda * risk_multiplier

        s_30 = self.weibull_survival(1.0, effective_lambda) # 1 month ahead
        s_60 = self.weibull_survival(2.0, effective_lambda)
        s_90 = self.weibull_survival(3.0, effective_lambda)

        churn_risk_30d = 1.0 - s_30
        churn_risk_90d = 1.0 - s_90
        
        # Expected half-life: t_half = (ln(2))^(1/beta) / lambda
        half_life_months = round((math.log(2) ** (1.0 / self.beta)) / max(1e-4, effective_lambda), 1)
        expected_annual_ltv_loss = round(mrr * 12.0 * churn_risk_90d, 2)

        # Automated playbook trigger
        if churn_risk_30d >= 0.45:
            action = "EMERGENCY_EXECUTIVE_INTERVENTION"
            offer = "20% Discount for 3 months + Dedicated Solutions Architect"
            est_saved_ltv = round(expected_annual_ltv_loss * 0.45, 2)
        elif churn_risk_30d >= 0.25:
            action = "PROACTIVE_CUSTOMER_SUCCESS_AUDIT"
            offer = "Free feature onboarding training + extended billing grace period"
            est_saved_ltv = round(expected_annual_ltv_loss * 0.30, 2)
        elif churn_risk_90d >= 0.20:
            action = "NURTURE_PRODUCT_RE_ENGAGEMENT"
            offer = "Personalized feature webinar & quarterly business review invite"
            est_saved_ltv = round(expected_annual_ltv_loss * 0.15, 2)
        else:
            action = "HEALTHY_EXPANSION_UPSELL"
            offer = "Annual contract renewal discount (15% annual savings)"
            est_saved_ltv = 0.0

        return {
            "status": "success",
            "customer_id": customer_id,
            "monthly_recurring_revenue": mrr,
            "tenure_months": tenure_months,
            "risk_proportional_multiplier": round(risk_multiplier, 3),
            "survival_probability_30d": round(s_30, 4),
            "survival_probability_90d": round(s_90, 4),
            "churn_probability_30d": round(churn_risk_30d, 4),
            "churn_probability_90d": round(churn_risk_90d, 4),
            "projected_half_life_months": half_life_months,
            "projected_ltv_at_risk": expected_annual_ltv_loss,
            "recommended_retention_action": action,
            "recommended_retention_offer": offer,
            "estimated_retained_ltv": est_saved_ltv
        }
