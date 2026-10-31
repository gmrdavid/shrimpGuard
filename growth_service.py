"""
Shrimp Growth & Zootechnical Performance Calculator Service
Implements standard scientific aquaculture equations (Eqs. 1-8) for Penaeus vannamei:
- Eq. 1: Survival Rate (SR) = (LHC / IS) * 100
- Eq. 2: Final Average Body Weight (FABW) = BW / LHC
- Eq. 3: Average Daily Weight Gain (ADWG) = (FABW - IBW) / DOC
- Eq. 4: Specific Growth Rate (SGR) = ((ln FABW - ln IBW) / DOC) * 100
- Eq. 5: Initial Biomass (IB) = IS * IBW
- Eq. 6: Final Biomass (FB) = LHC * FABW
- Eq. 7: Feed Conversion Ratio (FCR) = TFG / (FB - IB)
- Eq. 8: Fulton's Condition Factor (K) = (FABW / TL^3) * 100
"""

import math

def calculate_survival_rate(initial_stocking, live_harvest_count):
    """
    Eq. 1: Survival Rate (SR) = (LHC / IS) * 100
    """
    is_count = float(initial_stocking)
    lhc_count = float(live_harvest_count)
    if is_count <= 0:
        return {"error": "Initial stocking count (IS) must be greater than zero."}
    
    sr = (lhc_count / is_count) * 100.0
    mortality_count = max(0.0, is_count - lhc_count)
    mortality_pct = max(0.0, 100.0 - sr)

    if sr >= 80.0:
        badge = "Optimal"
        badge_class = "badge-optimal"
        rating = "Excellent survival rate exceeding typical commercial benchmark (>=80%)."
    elif sr >= 65.0:
        badge = "Acceptable"
        badge_class = "badge-warning"
        rating = "Moderate survival rate (65%-79%). Consider checking water quality and stocking density."
    else:
        badge = "Suboptimal"
        badge_class = "badge-critical"
        rating = "Low survival rate (<65%). Investigate potential disease, hypoxia, or predation stress."

    return {
        "equation": "Eq. 1",
        "name": "Survival Rate",
        "symbol": "SR",
        "sr_percent": round(sr, 2),
        "mortality_count": int(round(mortality_count)),
        "mortality_percent": round(mortality_pct, 2),
        "badge": badge,
        "badge_class": badge_class,
        "rating": rating,
        "formula": "SR = (LHC / IS) × 100",
        "substitution": f"({lhc_count:,.0f} / {is_count:,.0f}) × 100 = {sr:.2f}%"
    }


def calculate_final_avg_body_weight(bulk_weight, live_harvest_count, bulk_weight_unit="kg"):
    """
    Eq. 2: Final Average Body Weight (FABW) = BW / LHC
    """
    bw_val = float(bulk_weight)
    lhc_count = float(live_harvest_count)
    if lhc_count <= 0:
        return {"error": "Live harvest count (LHC) must be greater than zero."}
    
    bw_grams = bw_val * 1000.0 if bulk_weight_unit.lower() == "kg" else bw_val
    fabw = bw_grams / lhc_count
    count_per_kg = 1000.0 / fabw if fabw > 0 else 0.0

    return {
        "equation": "Eq. 2",
        "name": "Final Average Body Weight",
        "symbol": "FABW",
        "fabw_grams": round(fabw, 2),
        "bulk_weight_grams": round(bw_grams, 2),
        "bulk_weight_kg": round(bw_grams / 1000.0, 3),
        "count_per_kg": round(count_per_kg, 1),
        "formula": "FABW = BW / LHC",
        "substitution": f"{bw_grams:,.1f} g / {lhc_count:,.0f} shrimp = {fabw:.2f} g"
    }


def calculate_daily_gain_and_sgr(initial_body_weight, final_avg_body_weight, days_of_culture):
    """
    Eq. 3: ADWG = (FABW - IBW) / DOC
    Eq. 4: SGR = ((ln FABW - ln IBW) / DOC) * 100
    """
    ibw = float(initial_body_weight)
    fabw = float(final_avg_body_weight)
    doc = float(days_of_culture)

    if doc <= 0:
        return {"error": "Days of culture (DOC) must be greater than zero."}
    if ibw <= 0:
        return {"error": "Initial body weight (IBW) must be positive and greater than zero."}
    if fabw <= 0:
        return {"error": "Final body weight (FABW) must be positive."}

    adwg = (fabw - ibw) / doc
    weekly_gain = adwg * 7.0

    # Specific Growth Rate
    sgr = ((math.log(fabw) - math.log(ibw)) / doc) * 100.0

    if adwg >= 0.25:
        adwg_badge = "Fast Growth"
        adwg_class = "badge-optimal"
    elif adwg >= 0.18:
        adwg_badge = "Optimal Growth"
        adwg_class = "badge-optimal"
    else:
        adwg_badge = "Slow Growth"
        adwg_class = "badge-warning"

    return {
        "equations": ["Eq. 3", "Eq. 4"],
        "adwg_g_day": round(adwg, 4),
        "weekly_gain_g": round(weekly_gain, 3),
        "sgr_percent_day": round(sgr, 3),
        "adwg_badge": adwg_badge,
        "adwg_class": adwg_class,
        "adwg_formula": "ADWG = (FABW - IBW) / DOC",
        "adwg_substitution": f"({fabw:.2f} - {ibw:.3f}) / {doc:.0f} = {adwg:.4f} g/day",
        "sgr_formula": "SGR = [(ln FABW - ln IBW) / DOC] × 100",
        "sgr_substitution": f"[(ln {fabw:.2f} - ln {ibw:.3f}) / {doc:.0f}] × 100 = {sgr:.3f}%/day"
    }


def calculate_biomasses(initial_stocking, initial_body_weight, live_harvest_count, final_avg_body_weight):
    """
    Eq. 5: Initial Biomass (IB) = IS * IBW
    Eq. 6: Final Biomass (FB) = LHC * FABW
    """
    is_count = float(initial_stocking)
    ibw = float(initial_body_weight)
    lhc_count = float(live_harvest_count)
    fabw = float(final_avg_body_weight)

    ib_grams = is_count * ibw
    ib_kg = ib_grams / 1000.0

    fb_grams = lhc_count * fabw
    fb_kg = fb_grams / 1000.0

    net_yield_grams = max(0.0, fb_grams - ib_grams)
    net_yield_kg = net_yield_grams / 1000.0

    return {
        "equations": ["Eq. 5", "Eq. 6"],
        "ib_grams": round(ib_grams, 2),
        "ib_kg": round(ib_kg, 3),
        "fb_grams": round(fb_grams, 2),
        "fb_kg": round(fb_kg, 3),
        "net_gain_kg": round(net_yield_kg, 3),
        "ib_formula": "IB = IS × IBW",
        "ib_substitution": f"{is_count:,.0f} × {ibw:.3f} g = {ib_grams:,.1f} g ({ib_kg:.2f} kg)",
        "fb_formula": "FB = LHC × FABW",
        "fb_substitution": f"{lhc_count:,.0f} × {fabw:.2f} g = {fb_grams:,.1f} g ({fb_kg:.2f} kg)"
    }


def calculate_fcr(total_feed_given, final_biomass, initial_biomass, feed_unit="kg", biomass_unit="kg"):
    """
    Eq. 7: FCR = TFG / (FB - IB)
    """
    tfg_raw = float(total_feed_given)
    fb_raw = float(final_biomass)
    ib_raw = float(initial_biomass)

    tfg_kg = tfg_raw if feed_unit.lower() == "kg" else tfg_raw / 1000.0
    fb_kg = fb_raw if biomass_unit.lower() == "kg" else fb_raw / 1000.0
    ib_kg = ib_raw if biomass_unit.lower() == "kg" else ib_raw / 1000.0

    biomass_gain_kg = fb_kg - ib_kg
    if biomass_gain_kg <= 0:
        return {"error": "Final biomass (FB) must be greater than initial biomass (IB) to compute FCR."}

    fcr = tfg_kg / biomass_gain_kg
    feed_efficiency = (1.0 / fcr) * 100.0 if fcr > 0 else 0.0

    if fcr < 1.20:
        badge = "Exceptional"
        badge_class = "badge-optimal"
        rating = "Outstanding feed efficiency (<1.20). Minimal feed wastage with excellent assimilation."
    elif fcr <= 1.50:
        badge = "Optimal"
        badge_class = "badge-optimal"
        rating = "Standard target commercial FCR (1.20-1.50) for Penaeus vannamei."
    elif fcr <= 1.80:
        badge = "Acceptable"
        badge_class = "badge-warning"
        rating = "Moderate efficiency (1.51-1.80). Check feed tray consumption and avoid overfeeding."
    else:
        badge = "Suboptimal"
        badge_class = "badge-critical"
        rating = "High FCR (>1.80). Indicates feed wastage, biological stress, or unconsumed pellets."

    return {
        "equation": "Eq. 7",
        "name": "Feed Conversion Ratio",
        "symbol": "FCR",
        "fcr": round(fcr, 3),
        "feed_efficiency_percent": round(feed_efficiency, 2),
        "tfg_kg": round(tfg_kg, 2),
        "biomass_gain_kg": round(biomass_gain_kg, 2),
        "badge": badge,
        "badge_class": badge_class,
        "rating": rating,
        "formula": "FCR = TFG / (FB - IB)",
        "substitution": f"{tfg_kg:,.1f} kg feed / ({fb_kg:,.1f} - {ib_kg:,.1f}) kg gain = {fcr:.3f}"
    }


def calculate_fulton_condition(final_avg_body_weight, total_length_cm):
    """
    Eq. 8: Fulton's Body Condition Factor (K) = (FABW / TL^3) * 100
    """
    fabw = float(final_avg_body_weight)
    tl = float(total_length_cm)

    if tl <= 0:
        return {"error": "Total length (TL) must be greater than zero."}
    if fabw <= 0:
        return {"error": "Final body weight (FABW) must be greater than zero."}

    k = (fabw / (tl ** 3)) * 100.0

    if 0.80 <= k <= 1.15:
        badge = "Optimal Condition"
        badge_class = "badge-optimal"
        rating = "Well-proportioned, robust body condition characteristic of healthy Penaeus vannamei."
    elif k < 0.80:
        badge = "Slender / Lean"
        badge_class = "badge-warning"
        rating = "Slender body profile (K < 0.80). Shrimp may be undernourished or recovering from molt."
    else:
        badge = "Heavy / Plump"
        badge_class = "badge-optimal"
        rating = "High muscle density and robust carapace girth (K > 1.15)."

    return {
        "equation": "Eq. 8",
        "name": "Fulton's Condition Factor",
        "symbol": "K",
        "k_factor": round(k, 4),
        "badge": badge,
        "badge_class": badge_class,
        "rating": rating,
        "formula": "K = (FABW / TL³) × 100",
        "substitution": f"({fabw:.2f} g / {tl:.1f}³ cm³) × 100 = {k:.4f}"
    }


def calculate_full_growth_suite(
    initial_stocking,
    live_harvest_count,
    days_of_culture,
    initial_body_weight,
    bulk_weight=None,
    final_avg_body_weight=None,
    total_feed_given=None,
    total_length=None,
    bulk_weight_unit="kg",
    feed_unit="kg"
):
    """
    Master unified calculation engine for all 8 growth and production performance equations.
    """
    is_count = float(initial_stocking)
    lhc_count = float(live_harvest_count)
    doc = float(days_of_culture)
    ibw = float(initial_body_weight)

    # 1. Determine FABW and Bulk Weight
    if bulk_weight is not None and float(bulk_weight) > 0:
        bw_val = float(bulk_weight)
        bw_grams = bw_val * 1000.0 if bulk_weight_unit.lower() == "kg" else bw_val
        fabw = bw_grams / lhc_count if lhc_count > 0 else 0.0
    elif final_avg_body_weight is not None and float(final_avg_body_weight) > 0:
        fabw = float(final_avg_body_weight)
        bw_grams = lhc_count * fabw
    else:
        fabw = 20.0
        bw_grams = lhc_count * fabw

    # Eq. 1: Survival Rate
    sr_res = calculate_survival_rate(is_count, lhc_count)

    # Eq. 2: FABW
    fabw_res = calculate_final_avg_body_weight(bw_grams, lhc_count, bulk_weight_unit="g")

    # Eq. 3 & Eq. 4: ADWG & SGR
    growth_res = calculate_daily_gain_and_sgr(ibw, fabw, doc)

    # Eq. 5 & Eq. 6: Biomass
    biomass_res = calculate_biomasses(is_count, ibw, lhc_count, fabw)

    # Eq. 7: FCR
    if total_feed_given is not None and float(total_feed_given) > 0:
        tfg_val = float(total_feed_given)
        fcr_res = calculate_fcr(tfg_val, biomass_res["fb_kg"], biomass_res["ib_kg"], feed_unit=feed_unit, biomass_unit="kg")
    else:
        fcr_res = None

    # Eq. 8: Fulton's K
    if total_length is not None and float(total_length) > 0:
        k_res = calculate_fulton_condition(fabw, float(total_length))
    else:
        k_res = None

    return {
        "success": True,
        "survival_rate": sr_res,
        "fabw": fabw_res,
        "daily_gain_and_sgr": growth_res,
        "biomass": biomass_res,
        "fcr": fcr_res,
        "fulton_k": k_res
    }

