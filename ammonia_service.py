"""
ammonia_service.py - Calculation of Unionized Ammonia (NH3)
Based on Van Wyk et al. (1999) "Water Quality Requirements and Management"
in Farming Marine Shrimp in Recirculating Freshwater Systems.
"""

from typing import Dict, Any, Tuple

# Van Wyk et al. (1999) Reference Table:
# Proportion of Total Ammonia Nitrogen in the Unionized Form as a Function of Temperature and pH
VAN_WYK_TEMPS = [24, 26, 28, 30, 32]
VAN_WYK_PH_LEVELS = [7.0, 7.2, 7.4, 7.6, 7.8, 8.0, 8.2, 8.4, 8.6, 8.8, 9.0, 9.2, 9.4, 9.6, 10.0]

VAN_WYK_TABLE: Dict[float, list] = {
    7.0: [0.005, 0.006, 0.007, 0.008, 0.009],
    7.2: [0.008, 0.010, 0.011, 0.013, 0.015],
    7.4: [0.013, 0.015, 0.018, 0.020, 0.023],
    7.6: [0.021, 0.024, 0.028, 0.031, 0.036],
    7.8: [0.033, 0.038, 0.043, 0.049, 0.056],
    8.0: [0.051, 0.058, 0.066, 0.075, 0.085],
    8.2: [0.078, 0.089, 0.101, 0.114, 0.129],
    8.4: [0.119, 0.134, 0.151, 0.170, 0.190],
    8.6: [0.176, 0.197, 0.220, 0.245, 0.271],
    8.8: [0.253, 0.281, 0.309, 0.340, 0.371],
    9.0: [0.349, 0.382, 0.415, 0.449, 0.483],
    9.2: [0.460, 0.495, 0.530, 0.564, 0.597],
    9.4: [0.574, 0.608, 0.641, 0.672, 0.701],
    9.6: [0.681, 0.711, 0.739, 0.764, 0.788],
    10.0: [0.843, 0.861, 0.877, 0.891, 0.903],
}

# Acceptable safety limit for Penaeus vannamei shrimp culture (Van Wyk et al., 1999)
AMMONIA_SAFE_THRESHOLD = 0.03  # ppm (mg/L)


def get_closest_grid_indices(temp: float, ph: float) -> Tuple[int, float, int, float]:
    """Finds closest grid temperature and pH row/col for table highlighting."""
    closest_t_idx = min(range(len(VAN_WYK_TEMPS)), key=lambda i: abs(VAN_WYK_TEMPS[i] - temp))
    closest_p_idx = min(range(len(VAN_WYK_PH_LEVELS)), key=lambda i: abs(VAN_WYK_PH_LEVELS[i] - ph))
    return closest_t_idx, VAN_WYK_TEMPS[closest_t_idx], closest_p_idx, VAN_WYK_PH_LEVELS[closest_p_idx]


def get_unionized_fraction(temp: float, ph: float) -> float:
    """
    Computes the proportion of Total Ammonia Nitrogen in the unionized form
    via 2D bilinear interpolation from the Van Wyk et al. (1999) reference table.
    """
    t_clamped = max(24.0, min(32.0, float(temp)))
    p_clamped = max(7.0, min(10.0, float(ph)))

    # Find temperature interval
    t_idx = 0
    while t_idx < len(VAN_WYK_TEMPS) - 1 and VAN_WYK_TEMPS[t_idx + 1] <= t_clamped:
        t_idx += 1
    t1 = VAN_WYK_TEMPS[t_idx]
    t2_idx = min(t_idx + 1, len(VAN_WYK_TEMPS) - 1)
    t2 = VAN_WYK_TEMPS[t2_idx]
    u = 0.0 if t1 == t2 else (t_clamped - t1) / (t2 - t1)

    # Find pH interval
    p_idx = 0
    while p_idx < len(VAN_WYK_PH_LEVELS) - 1 and VAN_WYK_PH_LEVELS[p_idx + 1] <= p_clamped:
        p_idx += 1
    p1 = VAN_WYK_PH_LEVELS[p_idx]
    p2_idx = min(p_idx + 1, len(VAN_WYK_PH_LEVELS) - 1)
    p2 = VAN_WYK_PH_LEVELS[p2_idx]
    v = 0.0 if p1 == p2 else (p_clamped - p1) / (p2 - p1)

    f11 = VAN_WYK_TABLE[p1][t_idx]
    f21 = VAN_WYK_TABLE[p1][t2_idx]
    f12 = VAN_WYK_TABLE[p2][t_idx]
    f22 = VAN_WYK_TABLE[p2][t2_idx]

    fraction = (1 - u) * (1 - v) * f11 + u * (1 - v) * f21 + (1 - u) * v * f12 + u * v * f22
    return round(fraction, 4)


def calculate_unionized_ammonia(tan: float, temp: float, ph: float) -> Dict[str, Any]:
    """
    Calculates unionized ammonia (NH3) concentration from Total Ammonia Nitrogen (TAN),
    water temperature, and pH level.
    """
    tan_val = max(0.0, float(tan))
    temp_val = float(temp)
    ph_val = float(ph)

    fraction = get_unionized_fraction(temp_val, ph_val)
    nh3_ppm = round(tan_val * fraction, 4)

    is_safe = nh3_ppm < AMMONIA_SAFE_THRESHOLD
    status = "Safe" if is_safe else "Action Required"

    closest_t_idx, closest_t, closest_p_idx, closest_p = get_closest_grid_indices(temp_val, ph_val)

    if is_safe:
        assessment = (
            f"This level ({nh3_ppm:.4f} ppm) is lower than the acceptable toxicity threshold "
            f"(< {AMMONIA_SAFE_THRESHOLD} ppm), hence no corrective action would need to be taken."
        )
        actions = [
            "Maintain regular pond monitoring and dissolved oxygen above 5.0 ppm.",
            "Continue scheduled shrimp feeding protocol for Penaeus vannamei."
        ]
    else:
        assessment = (
            f"This level ({nh3_ppm:.4f} ppm) exceeds the acceptable threshold "
            f"(>= {AMMONIA_SAFE_THRESHOLD} ppm). Unionized ammonia is toxic to Penaeus vannamei, "
            "and corrective measures must be taken immediately."
        )
        actions = [
            "Maximize surface and submerged mechanical aeration to strip ammonia gas.",
            "Conduct a 15–20% pond water exchange if supply water is conditioned.",
            "Temporarily reduce feeding volume by 30–50% to decrease nitrogen input.",
            "Apply approved organic acid treatments or molasses to stabilize pH and stimulate biofloc."
        ]

    return {
        "tan_ppm": tan_val,
        "temperature": temp_val,
        "ph": ph_val,
        "fraction": fraction,
        "unionized_ammonia_ppm": nh3_ppm,
        "threshold_ppm": AMMONIA_SAFE_THRESHOLD,
        "status": status,
        "is_safe": is_safe,
        "assessment": assessment,
        "corrective_actions": actions,
        "closest_grid": {
            "temperature": closest_t,
            "ph": closest_p,
            "table_factor": VAN_WYK_TABLE[closest_p][closest_t_idx]
        },
        "reference": "Van Wyk et al., 1999"
    }
