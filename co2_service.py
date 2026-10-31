"""
co2_service.py - Calculation of Free Carbon Dioxide (CO2)
Based on Tucker (1984) "Factors for calculating carbon dioxide concentrations
in water with known pH, temperature and alkalinity measurements."
"""

from typing import Dict, Any, Tuple

# Tucker (1984) Reference Matrix Columns and Rows:
TUCKER_TEMPS = [5, 10, 15, 20, 25, 30, 35]
TUCKER_PH_LEVELS = [6.0, 6.2, 6.4, 6.6, 6.8, 7.0, 7.2, 7.4, 7.6, 7.8, 8.0, 8.2, 8.4]

# Table 2. Tucker (1984) Factors
TUCKER_TABLE: Dict[float, list] = {
    6.0: [2.915, 2.539, 2.315, 2.112, 1.970, 1.882, 1.839],
    6.2: [1.839, 1.602, 1.460, 1.333, 1.244, 1.187, 1.160],
    6.4: [1.160, 1.010, 0.921, 0.841, 0.784, 0.749, 0.732],
    6.6: [0.732, 0.637, 0.582, 0.531, 0.495, 0.473, 0.462],
    6.8: [0.462, 0.402, 0.367, 0.335, 0.313, 0.298, 0.291],
    7.0: [0.291, 0.254, 0.232, 0.211, 0.197, 0.188, 0.184],
    7.2: [0.184, 0.160, 0.146, 0.133, 0.124, 0.119, 0.116],
    7.4: [0.116, 0.101, 0.092, 0.084, 0.078, 0.075, 0.073],
    7.6: [0.073, 0.064, 0.058, 0.053, 0.050, 0.047, 0.046],
    7.8: [0.046, 0.040, 0.037, 0.034, 0.031, 0.030, 0.030],
    8.0: [0.029, 0.025, 0.023, 0.021, 0.020, 0.019, 0.018],
    8.2: [0.018, 0.016, 0.015, 0.013, 0.012, 0.012, 0.011],
    8.4: [0.012, 0.010, 0.009, 0.008, 0.008, 0.008, 0.007],
}

# Penaeus vannamei physiological thresholds for free CO2
CO2_SAFE_THRESHOLD = 10.0      # mg/L (ppm) - optimal range < 10 mg/L
CO2_CRITICAL_THRESHOLD = 20.0  # mg/L (ppm) - severe stress / Bohr effect > 20 mg/L


def get_closest_tucker_indices(temp: float, ph: float) -> Tuple[int, float, int, float]:
    """Finds closest grid temperature and pH row/col for table highlighting."""
    closest_t_idx = min(range(len(TUCKER_TEMPS)), key=lambda i: abs(TUCKER_TEMPS[i] - temp))
    closest_p_idx = min(range(len(TUCKER_PH_LEVELS)), key=lambda i: abs(TUCKER_PH_LEVELS[i] - ph))
    return closest_t_idx, TUCKER_TEMPS[closest_t_idx], closest_p_idx, TUCKER_PH_LEVELS[closest_p_idx]


def get_tucker_factor(temp: float, ph: float) -> float:
    """
    Computes the Tucker (1984) multiplication factor via 2D bilinear interpolation.
    For pH > 8.4, free CO2 is negligible (approaching ~0).
    """
    temp_val = float(temp)
    ph_val = float(ph)

    if ph_val >= 8.5:
        # Above pH 8.4, carbonate equilibrium converts CO2 into bicarbonate (HCO3-) and carbonate (CO3(2-))
        return 0.001

    t_clamped = max(5.0, min(35.0, temp_val))
    p_clamped = max(6.0, min(8.4, ph_val))

    # Find temperature interval
    t_idx = 0
    while t_idx < len(TUCKER_TEMPS) - 1 and TUCKER_TEMPS[t_idx + 1] <= t_clamped:
        t_idx += 1
    t1 = TUCKER_TEMPS[t_idx]
    t2_idx = min(t_idx + 1, len(TUCKER_TEMPS) - 1)
    t2 = TUCKER_TEMPS[t2_idx]
    u = 0.0 if t1 == t2 else (t_clamped - t1) / (t2 - t1)

    # Find pH interval
    p_idx = 0
    while p_idx < len(TUCKER_PH_LEVELS) - 1 and TUCKER_PH_LEVELS[p_idx + 1] <= p_clamped:
        p_idx += 1
    p1 = TUCKER_PH_LEVELS[p_idx]
    p2_idx = min(p_idx + 1, len(TUCKER_PH_LEVELS) - 1)
    p2 = TUCKER_PH_LEVELS[p2_idx]
    v = 0.0 if p1 == p2 else (p_clamped - p1) / (p2 - p1)

    f11 = TUCKER_TABLE[p1][t_idx]
    f21 = TUCKER_TABLE[p1][t2_idx]
    f12 = TUCKER_TABLE[p2][t_idx]
    f22 = TUCKER_TABLE[p2][t2_idx]

    factor = (1 - u) * (1 - v) * f11 + u * (1 - v) * f21 + (1 - u) * v * f12 + u * v * f22
    return round(factor, 4)


def calculate_free_co2(alkalinity: float, temp: float, ph: float) -> Dict[str, Any]:
    """
    Calculates free carbon dioxide (CO2 in mg/L or ppm) from Total Alkalinity (mg/L CaCO3),
    water temperature (°C), and pH level based on Tucker (1984).
    """
    alk_val = max(0.0, float(alkalinity))
    temp_val = float(temp)
    ph_val = float(ph)

    factor = get_tucker_factor(temp_val, ph_val)
    co2_mg_l = round(alk_val * factor, 3)

    if ph_val > 8.4:
        status = "Negligible (< 1.0 mg/L)"
        badge_class = "badge-optimal"
        assessment = (
            f"At pH {ph_val:.2f} (> 8.4), free carbon dioxide is negligible ({co2_mg_l:.3f} mg/L). "
            "In alkaline water, carbonate equilibrium shifts completely to bicarbonate (HCO₃⁻) and carbonate (CO₃²⁻)."
        )
    elif co2_mg_l < CO2_SAFE_THRESHOLD:
        status = "Safe (< 10.0 mg/L)"
        badge_class = "badge-optimal"
        assessment = (
            f"Free CO₂ ({co2_mg_l:.3f} mg/L) is within the safe zootechnical range (< 10.0 mg/L) "
            "for Penaeus vannamei. Shrimp respiration and hemocyanin oxygen affinity remain optimal."
        )
    elif co2_mg_l <= CO2_CRITICAL_THRESHOLD:
        status = "Elevated (10.0–20.0 mg/L)"
        badge_class = "badge-warning"
        assessment = (
            f"WARNING: Free CO₂ ({co2_mg_l:.3f} mg/L) is elevated (10.0–20.0 mg/L). "
            "This induces mild respiratory stress and slight hemolymph acidification. "
            "Engage paddlewheel aerators to agitate the water surface and strip excess CO₂."
        )
    else:
        status = "Critical Stress (> 20.0 mg/L)"
        badge_class = "badge-critical"
        assessment = (
            f"CRITICAL HAZARD: Free CO₂ ({co2_mg_l:.3f} mg/L) exceeds the dangerous threshold (> 20.0 mg/L). "
            "High CO₂ causes Bohr-Root hemocyanin hypoxia and severe acidosis, preventing shrimp from absorbing "
            "oxygen even if DO is adequate. Activate all emergency aerators and consider agricultural liming."
        )

    closest_t_idx, closest_t, closest_p_idx, closest_p = get_closest_tucker_indices(temp_val, ph_val)

    return {
        "alkalinity": alk_val,
        "temperature": temp_val,
        "ph": ph_val,
        "factor": factor,
        "co2_mg_l": co2_mg_l,
        "status": status,
        "badge_class": badge_class,
        "assessment": assessment,
        "closest_temp": closest_t,
        "closest_ph": closest_p,
    }

