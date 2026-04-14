import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from config.loader import load_data_config

# =========================================
# HELPERS
# =========================================

def add_noise(value, pct):
    return value * (1 + np.random.uniform(-pct, pct))

def random_in_range(low, high, pct):
    base = np.random.uniform(low, high)
    return add_noise(base, pct)

def compute_hour_factor(hour, config):
    curve = config["traffic_curve"]

    base = curve["base"]

    # Evening peak (circular)
    ep = curve["evening_peak"]
    d = min(abs(hour - ep["center"]), 24 - abs(hour - ep["center"]))
    evening = ep["amplitude"] * np.exp(-(d**2) / ep["spread"])

    # Midday peak
    mp = curve["midday_peak"]
    midday = mp["amplitude"] * np.exp(-((hour - mp["center"])**2) / mp["spread"])

    # Early dip
    ed = curve["early_dip"]
    dip = ed["amplitude"] * np.exp(-((hour - ed["center"])**2) / ed["spread"])

    return base + evening + midday - dip

def apply_hourly_rules(cmd, hour, values, hourly_rules):
    hour_str = str(hour)

    if hour_str in hourly_rules and cmd in hourly_rules[hour_str]:
        rules = hourly_rules[hour_str][cmd]

        for key, multiplier in rules.items():
            field = key.replace("_multiplier", "")

            # 🚨 ONLY allow latency + failure rules
            if field in ["success_rt_avg", "fail_rt_avg", "fail_vol"]:
                if field in values:
                    values[field] *= multiplier

    return values

def apply_load_dynamics(op, values, cfg, config):
    """
    Apply realistic system load behavior:
    Volume → Latency → Failures
    """

    baseline_vol = cfg["success_vol"]

    if baseline_vol <= 0:
        return values

    # ----------------------------
    # 1. Compute load
    # ----------------------------
    load_factor = values["success_vol"] / baseline_vol
    load_delta = load_factor - 1

    # Clamp extreme spikes
    load_delta = min(load_delta, 3)

    latency_factor = config["system_dynamics"]["latency_increase_factor"]
    failure_factor = config["system_dynamics"]["failure_increase_factor"]

    # ----------------------------
    # 2. Apply effects
    # ----------------------------

    # Latency increases with load
    values["success_rt_avg"] *= (1 + latency_factor * load_delta)
    values["fail_rt_avg"] *= (1 + latency_factor * load_delta)

    # Failures increase more aggressively non linearly
    values["fail_vol"] *= (1 + failure_factor * (load_factor ** 1.3 - 1))

    # ----------------------------
    # 3. Safety clamps
    # ----------------------------
    values["success_rt_avg"] = max(values["success_rt_avg"], 1)
    values["fail_rt_avg"] = max(values["fail_rt_avg"], 1)
    values["fail_vol"] = max(values["fail_vol"], 0)

    return values


# =========================================
# ANOMALY FUNCTION
# =========================================
def inject_anomaly(values, config):

    anomaly_cfg = config["anomaly_injection"]

    # ✅ probability check INSIDE function
    if np.random.rand() > anomaly_cfg["probability"]:
        return values, False, None

    rules = anomaly_cfg["rules"]

    anomaly_type = np.random.choice(list(rules.keys()))
    rule = rules[anomaly_type]

    targets = rule["targets"]
    factor_min, factor_max = rule["factor_range"]

    # ✅ realistic intensity variation
    if np.random.rand() < 0.7:
        factor = np.random.uniform(factor_min, (factor_min + factor_max) / 2)
    else:
        factor = np.random.uniform(factor_min, factor_max)

    # ----------------------------
    # APPLY ANOMALY
    # ----------------------------
    for t in targets:

        if t not in values:
            continue

        # latency → only increase
        if t in ["success_rt_avg", "fail_rt_avg"]:
            values[t] *= factor

        # success volume (can go up or down depending on factor)
        elif t == "success_vol":
            values[t] *= factor

        # failure volume → increase
        elif t == "fail_vol":
            values[t] *= factor

    return values, True, anomaly_type


# =========================================
# MAIN GENERATOR
# =========================================
def generate_test_data(start_date, hours, config, seed=None):

    if seed is not None:
        np.random.seed(seed)

    RANDOMNESS = config["noise"]
    operations_config = config["operations"]
    hourly_rules = config["hourly_rules"]

    data = []
    current = start_date

    for _ in range(hours):
        hour = current.hour
        hour_factor = compute_hour_factor(hour, config)

        for op, cfg in operations_config.items():

            base_vol = cfg["success_vol"]

            # ----------------------------
            # TRAFFIC
            # ----------------------------
            success_vol = base_vol * hour_factor

            # ----------------------------
            # NOISE
            # ----------------------------
            values = {
                "success_vol": add_noise(success_vol, RANDOMNESS["success_vol_std_pct"]),
                "fail_vol": add_noise(cfg["fail_vol"], RANDOMNESS["fail_vol_std_pct"]),
                "success_rt_avg": random_in_range(*cfg["success_rt_avg"], RANDOMNESS["latency_std_pct"]),
                "fail_rt_avg": random_in_range(*cfg["fail_rt_avg"], RANDOMNESS["latency_std_pct"])
            }

            # ----------------------------
            # SYSTEM DYNAMICS
            # ----------------------------
            values = apply_load_dynamics(op, values, cfg, config)
            values = apply_hourly_rules(op, hour, values, hourly_rules)

            # ----------------------------
            # ANOMALY INJECTION
            # ----------------------------
            values, is_anomaly, anomaly_type = inject_anomaly(values, config)

            # ----------------------------
            # FINAL OUTPUT
            # ----------------------------
            data.append({
                "timestamp": current,
                "operation": op,
                "success_vol": int(values["success_vol"]),
                "success_rt_avg": round(values["success_rt_avg"], 3),
                "fail_vol": int(values["fail_vol"]),
                "fail_rt_avg": round(values["fail_rt_avg"], 3),
                "is_anomaly": is_anomaly,
                "anomaly_type": anomaly_type
            })

        current += timedelta(hours=1)

    return pd.DataFrame(data)

# =========================================
# MAIN
# =========================================
def main():

    config = load_data_config()

    df = generate_test_data(
        start_date=datetime(2025, 4, 1),
        hours=24 * 7,
        config=config
    )

    print(df.head())
    print("\nAnomaly Rate:", round(df["is_anomaly"].mean(), 3))


# =========================================
# RUN
# =========================================
if __name__ == "__main__":
    main()