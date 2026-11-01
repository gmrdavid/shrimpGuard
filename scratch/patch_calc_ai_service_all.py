import json

with open("calculator_ai_service.py", "r", encoding="utf-8") as f:
    text = f.read()

def normalize(s):
    return s.replace("\r\n", "\n")

text_norm = normalize(text)

prompt_all_code = '''    elif module == "all":
        feeding = data.get("feeding", {})
        growth = data.get("growth", {})
        remediation = data.get("remediation", {})
        ammonia = data.get("ammonia", {})
        co2 = data.get("co2", {})

        return f"""Penaeus vannamei Comprehensive Master Pond Evaluation (All 5 Calculation Modules):

[1. Feeding Management]:
- Stocking Density: {feeding.get('density', 60)} PL/m² (Pond Area: {feeding.get('area', 1000)} m², Depth: {feeding.get('depth', 1.2)} m)
- Estimated Standing Biomass: {feeding.get('biomass_kg', 765.0):.1f} kg (ABW: {feeding.get('abw', 15.0):.1f} g, Survival: {feeding.get('survival', 85)}%)
- Adjusted Daily Feed: {feeding.get('adjusted_feed_kg', 24.5):.1f} kg/day ({feeding.get('meals', 4)} meals/day, Temp Factor: {feeding.get('temp_factor', 1.0):.2f}×)

[2. Growth & Zootechnical Performance]:
- DOC: {growth.get('doc', 90)} days (Initial Stocking: {growth.get('initial_stocking', 100000):,} -> Live Harvest: {growth.get('live_count', 85000):,})
- Final ABW: {growth.get('fabw', 20.0):.2f} g | ADWG: {growth.get('adwg', 0.22):.3f} g/day | SGR: {growth.get('sgr', 8.44):.2f}%/day
- FCR: {growth.get('fcr', 1.25):.2f} | Fulton's Condition Factor (K): {growth.get('k_factor', 0.85):.2f} | Final Biomass: {growth.get('final_biomass', 1700.0):.1f} kg

[3. Water Remediation & Dosing]:
- Liming Dosage: {remediation.get('lime_kg', 54.0):.1f} kg (Current pH {remediation.get('lime_ph', 7.2):.2f} -> Target {remediation.get('lime_target', 8.0):.2f})
- Biofloc Organic Carbon: {remediation.get('molasses_kg', 18.4):.1f} kg/day (Source: {remediation.get('carbon_source', 'cane_molasses')}, Target C:N {remediation.get('target_cn', 15)}:1)
- Aerator Sizing: {remediation.get('aerator_hp', 2.0):.1f} HP (Target DO: {remediation.get('target_do', 5.0):.1f} mg/L)

[4. Unionized Ammonia (NH3) Toxicity]:
- TAN: {ammonia.get('tan', 0.80):.2f} ppm | Temp: {ammonia.get('temp', 28.0):.1f} °C | pH: {ammonia.get('ph', 7.60):.2f} | Salinity: {ammonia.get('salinity', 20.0):.1f} ppt
- Toxic Unionized NH3: {ammonia.get('nh3_ppm', 0.0224):.4f} ppm (Van Wyk fraction: {ammonia.get('factor', 0.0280)*100:.2f}%)

[5. Free Carbon Dioxide (CO2)]:
- Total Alkalinity: {co2.get('alkalinity', 140.0):.1f} mg/L | Temp: {co2.get('temp', 28.0):.1f} °C | pH: {co2.get('ph', 7.60):.2f}
- Free CO2 Concentration: {co2.get('co2_ppm', 6.75):.3f} mg/L (Tucker factor: {co2.get('factor', 0.0482):.4f})

Provide a comprehensive, authoritative master biological diagnosis synthesizing all 5 domains for commercial intensive Penaeus vannamei culture.
Synthesize systemic interactions: how feed input impacts TAN, biofloc respiration impacts nocturnal DO, and carbonate buffering stabilizes ammonia toxicity.
Prescribe prioritized, step-by-step operational directives across feeding, water quality, and biofloc management.
Return a valid JSON object matching this schema:
{{
    "status": "Optimal" or "Warning" or "Critical",
    "evaluation": "Comprehensive systemic biological evaluation connecting feeding load, zootechnical growth velocity, nitrogen excretion, and gas balance.",
    "recommendation": "Executive master operational summary for whole-pond management.",
    "action_items": [
        "Priority 1: Water Quality & Gas Balance (Aeration degassing for CO2, NH3 mitigation)",
        "Priority 2: Feeding & Nutrition Management (Tray verification, protein load control)",
        "Priority 3: Chemical & Biofloc Remediation (Lime buffering application, molasses C:N dosing)",
        "Priority 4: Zootechnical Growth & Carrying Capacity (Harvest planning, biomass thinning)"
    ],
    "module_ratings": {{
        "feeding": "Optimal",
        "growth": "Optimal",
        "remediation": "Optimal",
        "ammonia": "Safe",
        "co2": "Safe"
    }}
}}"""'''

target_prompt_else = '    else:\n        return f"Analyze the following Penaeus vannamei calculator data and provide recommendations: {json.dumps(data)}"'

replacement_prompt_else = prompt_all_code + "\n\n" + target_prompt_else

assert normalize(target_prompt_else) in text_norm, "target_prompt_else not found"
text_norm = text_norm.replace(normalize(target_prompt_else), normalize(replacement_prompt_else), 1)

# Now update _generate_fallback_insight to handle module == "all"
fallback_all_code = '''    elif module == "all":
        feeding = data.get("feeding", {})
        growth = data.get("growth", {})
        remediation = data.get("remediation", {})
        ammonia = data.get("ammonia", {})
        co2 = data.get("co2", {})

        biomass = float(feeding.get("biomass_kg", 765.0))
        feed = float(feeding.get("adjusted_feed_kg", 24.5))
        fcr = float(growth.get("fcr", 1.25))
        adwg = float(growth.get("adwg", 0.222))
        nh3 = float(ammonia.get("nh3_ppm", 0.0224))
        co2_val = float(co2.get("co2_ppm", 6.75))
        lime_kg = float(remediation.get("lime_kg", 54.0))
        molasses_kg = float(remediation.get("molasses_kg", 18.4))
        aero_hp = float(remediation.get("aerator_hp", 2.0))

        # Determine overall master status
        if nh3 >= 0.08 or co2_val > 20.0 or fcr > 1.7:
            status = "Critical"
        elif nh3 >= 0.03 or co2_val >= 10.0 or fcr > 1.5 or adwg < 0.15:
            status = "Warning"
        else:
            status = "Optimal"

        eval_text = (
            f"SYSTEMIC POND MASTER DIAGNOSIS: Standing biomass ({biomass:.1f} kg) and daily feed input ({feed:.1f} kg/day) "
            f"are in steady equilibrium. Zootechnical performance reflects efficient feed utilization (FCR: {fcr:.2f}, "
            f"ADWG: {adwg:.3f} g/day). Water chemistry parameters indicate toxic NH3 ({nh3:.4f} ppm) and free CO2 ({co2_val:.2f} mg/L) "
            f"are well within physiological safety margins. Buffering reserves ({lime_kg:.1f} kg lime) and microbial carbon ({molasses_kg:.1f} kg molasses) "
            f"adequately support biofloc heterotrophic assimilation under {aero_hp:.1f} HP aerator power."
        )

        rec_text = (
            "All 5 production and water quality modules operate within acceptable biological tolerances. "
            "Synchronize feeding tray audits with morning alkalinity maintenance and nocturnal paddlewheel schedules."
        )

        actions = [
            f"Priority 1 (Gas & Respiration): Run all {aero_hp:.1f} HP aerators throughout 22:00–07:00 to degas pre-dawn CO2 and preserve DO >5.0 mg/L.",
            f"Priority 2 (Feed & Nitrogen): Maintain {feed:.1f} kg/day feeding schedule; verify clean trays within 1.5–2 hours to prevent ammonia spikes.",
            f"Priority 3 (Biofloc & Carbonate): Broadcast {lime_kg:.1f} kg lime slurry in early morning and ferment {molasses_kg:.1f} kg molasses to sustain C:N 15:1.",
            f"Priority 4 (Growth & Harvest): Continue weekly ABW sampling; FCR ({fcr:.2f}) indicates robust conversion velocity toward target harvest biomass."
        ]

        module_ratings = {
            "feeding": "Optimal" if feed <= biomass * 0.045 else "Warning",
            "growth": "Optimal" if fcr <= 1.5 else "Warning",
            "remediation": "Optimal",
            "ammonia": "Safe" if nh3 < 0.03 else ("Warning" if nh3 < 0.08 else "Critical"),
            "co2": "Safe" if co2_val < 10.0 else ("Warning" if co2_val < 20.0 else "Critical")
        }

        return {
            "status": status,
            "evaluation": eval_text,
            "recommendation": rec_text,
            "action_items": actions,
            "module_ratings": module_ratings,
            "source": "ShrimpGuard Aquaculture Dynamic Engine (Fallback)",
            "cached": False,
            "module": "all"
        }
'''

target_fallback_else = """    else:  # remediation"""
replacement_fallback_else = fallback_all_code + "\n    else:  # remediation"

assert normalize(target_fallback_else) in text_norm, "target_fallback_else not found"
text_norm = text_norm.replace(normalize(target_fallback_else), normalize(replacement_fallback_else), 1)

with open("calculator_ai_service.py", "w", encoding="utf-8") as f:
    f.write(text_norm)

print("Updated calculator_ai_service.py with module='all' support successfully!")
