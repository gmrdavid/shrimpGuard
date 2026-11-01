import os
import json
import time
import hashlib
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("shrimpguard.ai_calculators")

# In-memory cache for calculator AI insights (5-minute TTL)
# Key: md5 hash of module + sorted parameters, Value: (timestamp, result_dict)
_AI_INSIGHT_CACHE: Dict[str, tuple[float, Dict[str, Any]]] = {}
_CACHE_TTL_SECONDS = 300.0  # 5 minutes


def _get_cache_key(module: str, data: Dict[str, Any]) -> str:
    raw = f"{module}:" + json.dumps(data, sort_keys=True)
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def _get_cached_insight(cache_key: str) -> Optional[Dict[str, Any]]:
    now = time.time()
    if cache_key in _AI_INSIGHT_CACHE:
        ts, result = _AI_INSIGHT_CACHE[cache_key]
        if (now - ts) < _CACHE_TTL_SECONDS:
            cached_copy = dict(result)
            cached_copy["cached"] = True
            return cached_copy
        else:
            del _AI_INSIGHT_CACHE[cache_key]
    return None


def _set_cached_insight(cache_key: str, result: Dict[str, Any]) -> None:
    now = time.time()
    # Evict expired keys if cache grows large
    if len(_AI_INSIGHT_CACHE) > 100:
        expired = [k for k, (ts, _) in _AI_INSIGHT_CACHE.items() if (now - ts) >= _CACHE_TTL_SECONDS]
        for k in expired:
            _AI_INSIGHT_CACHE.pop(k, None)
    _AI_INSIGHT_CACHE[cache_key] = (now, result)


def _build_system_prompt() -> str:
    return (
        "You are an expert aquaculture specialist, marine biologist, and penaeid shrimp pathologist "
        "specializing solely and exclusively in Penaeus vannamei (Pacific white shrimp / Whiteleg shrimp) "
        "pond management, zootechnical performance, biofloc water chemistry, and pathology. "
        "Your role is to analyze exact numerical calculation outputs, provide an authoritative biological diagnosis "
        "on shrimp physiology (metabolism, hepatopancreas, gills, molting, FCR), and prescribe concrete, "
        "step-by-step operational instructions for commercial pond technicians. "
        "You MUST respond ONLY with a single valid JSON object."
    )


def _build_module_prompt(module: str, data: Dict[str, Any]) -> str:
    if module == "feeding":
        area = data.get("area", 1000)
        depth = data.get("depth", 1.2)
        density = data.get("density", 60)
        survival = data.get("survival", 85)
        abw = data.get("abw", 15.0)
        base_rate = data.get("base_rate", 3.2)
        meals = data.get("meals", 4)
        temp = data.get("temp", 29.5)
        biomass_kg = data.get("biomass_kg", 765.0)
        adjusted_feed_kg = data.get("adjusted_feed_kg", 24.5)
        temp_factor = data.get("temp_factor", 1.00)

        return f"""Penaeus vannamei Feeding Management Parameters:
- Pond Surface Area: {area} m² (Depth: {depth} m, Water Volume: {area * depth:.1f} m³)
- Stocking Density: {density} PL/m²
- Estimated Survival: {survival}%
- Average Body Weight (ABW): {abw} grams
- Estimated Standing Biomass: {biomass_kg:.1f} kg
- Base Feeding Rate: {base_rate}% of biomass
- Water Temperature: {temp:.1f} °C (Temperature Feed Factor: {temp_factor:.2f}×)
- Adjusted Daily Feed: {adjusted_feed_kg:.1f} kg/day ({meals} meals/day, {adjusted_feed_kg/max(1, meals):.2f} kg/meal)

Provide an expert biological evaluation of this feeding regimen for Penaeus vannamei.
Analyze metabolic digestion rate at {temp:.1f} °C, feed tray inspection protocol, and risks of overfeeding or biomass fouling.
Return a valid JSON object matching this schema:
{{
    "status": "Optimal" or "Warning" or "Critical",
    "evaluation": "Comprehensive biological diagnosis on shrimp metabolic rate, gastric evacuation time, and feeding response at {temp:.1f} °C.",
    "recommendation": "Executive operational recommendation for the daily feeding schedule.",
    "action_items": [
        "Action 1 (feeding tray check timing and percentage adjustment)",
        "Action 2 (aeration support during feeding to avoid bottom anoxia)",
        "Action 3 (feed quality, pellet size, or protein ration adjustments)"
    ]
}}"""

    elif module == "growth":
        eq = data.get("eq")  # optional specific equation
        doc = data.get("doc", 90)
        initial_stocking = data.get("initial_stocking", 100000)
        live_count = data.get("live_count", 85000)
        survival_rate = data.get("survival_rate", 85.0)
        fabw = data.get("fabw", 20.0)
        adwg = data.get("adwg", 0.22)
        sgr = data.get("sgr", 8.44)
        final_biomass = data.get("final_biomass", 1700.0)
        fcr = data.get("fcr", 1.25)
        k_factor = data.get("k_factor", 0.85)

        eq_context = f"\nFocused on Equation: {eq}" if eq else ""

        return f"""Penaeus vannamei Growth & Zootechnical Performance Metrics:
- Days of Culture (DOC): {doc} days
- Initial Stocking: {initial_stocking:,} PL -> Live Harvest: {live_count:,} shrimp
- Eq 1 Survival Rate (SR): {survival_rate:.2f}% (Commercial Benchmark: 70–85%)
- Eq 2 Final Average Body Weight (FABW): {fabw:.2f} g (Market Count: {1000.0/max(0.1, fabw):.1f} pcs/kg)
- Eq 3 Average Daily Weight Gain (ADWG): {adwg:.3f} g/day (Optimal: 0.20–0.30 g/day)
- Eq 4 Specific Growth Rate (SGR): {sgr:.2f}%/day
- Eq 6 Final Harvest Biomass (FB): {final_biomass:.1f} kg
- Eq 7 Feed Conversion Ratio (FCR): {fcr:.2f} (Target: 1.1–1.4)
- Eq 8 Fulton's Condition Factor (K): {k_factor:.2f} (Plumpness Target: >0.80){eq_context}

Provide a rigorous zootechnical and physiological evaluation for Penaeus vannamei.
Evaluate whether growth velocity and feed efficiency meet top-tier commercial benchmarks, identify any bottlenecks, and recommend harvest readiness or ration tweaks.
Return a valid JSON object matching this schema:
{{
    "status": "Optimal" or "Warning" or "Critical",
    "evaluation": "Detailed evaluation comparing these zootechnical indices against global Penaeus vannamei standards.",
    "recommendation": "Strategic recommendation for feeding, harvest timing, or partial harvest thinning.",
    "action_items": [
        "Action 1 (FCR and dietary optimization)",
        "Action 2 (Pond carrying capacity and harvest planning)",
        "Action 3 (Water parameter stability to preserve growth rate)"
    ]
}}"""

    elif module == "remediation":
        sub = data.get("sub", "all")
        # Liming
        lime_ph = data.get("lime_ph", 7.2)
        lime_target = data.get("lime_target", 8.0)
        pond_volume = data.get("pond_volume", 1200)
        lime_kg = data.get("lime_kg", 54.0)
        lime_type = data.get("lime_type", "Agricultural Limestone (CaCO3)")
        # Molasses
        daily_feed = data.get("daily_feed", 25.0)
        protein_pct = data.get("protein_pct", 35)
        target_cn = data.get("target_cn", 15)
        carbon_source = data.get("carbon_source", "Cane Molasses (~40% Carbon)")
        molasses_kg = data.get("molasses_kg", 18.4)
        # Aerator
        biomass_aero = data.get("biomass_aero", 1000.0)
        target_do = data.get("target_do", 5.0)
        temp_aero = data.get("temp_aero", 29.5)
        aerator_hp = data.get("aerator_hp", 3.0)

        return f"""Penaeus vannamei Water Remediation & Dosing Parameters:
[1. Liming Buffer]:
- Current pH: {lime_ph:.2f} -> Target pH: {lime_target:.2f} (Pond Volume: {pond_volume} m³)
- Compound: {lime_type}
- Calculated Dosage: {lime_kg:.1f} kg

[2. Biofloc Organic Carbon Dosing]:
- Daily Feed: {daily_feed:.1f} kg/day ({protein_pct}% Crude Protein)
- Target C:N Ratio: {target_cn}:1
- Carbon Source: {carbon_source}
- Calculated Carbon Dose: {molasses_kg:.1f} kg/day

[3. Aerator Power Sizing]:
- Standing Biomass: {biomass_aero:.1f} kg at {temp_aero:.1f} °C
- Target DO: {target_do:.1f} mg/L
- Minimum Required Aerator Power: {aerator_hp:.1f} HP

Provide a comprehensive chemical and microbial remediation protocol for this Penaeus vannamei pond.
Detail application timing, slurry dissolving procedures, microbial assimilation of TAN, and aeration placement.
Return a valid JSON object matching this schema:
{{
    "status": "Optimal" or "Warning" or "Critical",
    "evaluation": "Scientific explanation of the carbonate buffering dynamics, heterotrophic biofloc TAN assimilation, and nocturnal oxygen demand.",
    "recommendation": "Executive operational instructions for applying lime, carbon, and aerator runtimes.",
    "action_items": [
        "Action 1 (Liming preparation and application timing to prevent sudden pH shock)",
        "Action 2 (Carbon source pre-fermentation with probiotics and broadcasting protocol)",
        "Action 3 (Aerator placement and nocturnal duty-cycle configuration)"
    ]
}}"""

    elif module == "ammonia":
        tan = data.get("tan", 0.80)
        temp = data.get("temp", 28.0)
        ph = data.get("ph", 7.60)
        salinity = data.get("salinity", 20.0)
        nh3_ppm = data.get("nh3_ppm", 0.0224)
        factor = data.get("factor", 0.0280)

        return f"""Penaeus vannamei Unionized Ammonia (NH3) Toxicity Parameters:
- Total Ammonia Nitrogen (TAN): {tan:.2f} mg/L (ppm)
- Water Temperature: {temp:.1f} °C
- pH Level: {ph:.2f}
- Salinity: {salinity:.1f} ppt
- Van Wyk (1999) Equilibrium Factor: {factor:.4f} ({factor*100:.2f}%)
- Unionized Toxic NH3 Concentration: {nh3_ppm:.4f} mg/L (ppm)
- Thresholds for P. vannamei: Safe < 0.030 ppm, Stress: 0.030–0.080 ppm, Critical: > 0.080 ppm

Analyze the toxicological risk of this NH3 level on Penaeus vannamei shrimp.
Evaluate gill tissue permeability, osmoregulatory stress, molting mortality risk, and immediate remedial interventions.
Return a valid JSON object matching this schema:
{{
    "status": "Safe" or "Warning" or "Critical",
    "evaluation": "Pathophysiological diagnosis of how {nh3_ppm:.4f} ppm NH3 affects Penaeus vannamei gill epithelium, blood pH, and excretion.",
    "recommendation": "Immediate farm remediation directives to prevent ammonia toxicity.",
    "action_items": [
        "Action 1 (Emergency water management: flushing, probiotic application, or pH suppression)",
        "Action 2 (Feeding adjustments to eliminate unconsumed protein decomposition)",
        "Action 3 (Aeration and biofloc C:N stimulation to sequester TAN)"
    ]
}}"""

    elif module == "co2":
        alk = data.get("alkalinity", 140.0)
        temp = data.get("temp", 28.0)
        ph = data.get("ph", 7.60)
        co2_ppm = data.get("co2_ppm", 6.75)
        factor = data.get("factor", 0.0482)

        return f"""Penaeus vannamei Free Carbon Dioxide (CO2) Parameters:
- Total Alkalinity: {alk:.1f} mg/L as CaCO3
- Water Temperature: {temp:.1f} °C
- pH Level: {ph:.2f}
- Tucker (1984) Equilibrium Factor: {factor:.4f}
- Calculated Free CO2 Concentration: {co2_ppm:.3f} mg/L (ppm)
- Thresholds for P. vannamei: Safe < 10.0 mg/L, Mild Stress: 10.0–20.0 mg/L, High Toxicity: > 20.0 mg/L

Analyze the hypercapnia risk and carbonate equilibrium for Penaeus vannamei.
Evaluate nocturnal respiration peaks, Root/Bohr effect on hemocyanin oxygen-binding capacity, and daytime stripping.
Return a valid JSON object matching this schema:
{{
    "status": "Safe" or "Warning" or "Critical",
    "evaluation": "Biological evaluation of how {co2_ppm:.3f} mg/L free CO2 influences Penaeus vannamei respiration, hemolymph pH, and calcification.",
    "recommendation": "Operational recommendations for mechanical degassing and diurnal alkalinity balancing.",
    "action_items": [
        "Action 1 (Aeration degassing to strip nocturnal CO2 before dawn)",
        "Action 2 (Alkalinity supplementation or hydrated lime application if pH dips)",
        "Action 3 (Plankton density management to prevent excessive respiratory respiration)"
    ]
}}"""

    else:
        return f"Analyze the following Penaeus vannamei calculator data and provide recommendations: {json.dumps(data)}"


def _generate_fallback_insight(module: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Intelligent dynamic rule-based aquaculture engine that produces expert-grade
    evaluations when the OpenAI/Gemini API is unconfigured, rate-limited, or offline.
    """
    if module == "feeding":
        temp = float(data.get("temp", 29.5))
        biomass = float(data.get("biomass_kg", 765.0))
        feed = float(data.get("adjusted_feed_kg", 24.5))
        meals = int(data.get("meals", 4))

        if temp < 25.0:
            status = "Warning"
            eval_text = (
                f"At {temp:.1f} °C, water temperature is below the thermal optimum (28.0–32.0 °C) for Penaeus vannamei. "
                f"Shrimp gastric evacuation slows significantly, reducing feed intake capacity by 30–50%. "
                f"Current adjusted ration of {feed:.1f} kg/day prevents uneaten pellet accumulation on pond bottoms."
            )
            rec_text = "Cut standard feed rations by 30–40% and increase feeding tray check intervals to 2.5 hours."
            actions = [
                "Inspect check trays 2.5 hours after feeding; adjust next meal downward if >10% remains.",
                "Concentrate feeding rations during the warmest diurnal window (12:00 PM – 3:00 PM).",
                "Maintain dissolved oxygen >5.0 mg/L using paddlewheels to assist digestive metabolism."
            ]
        elif temp > 32.5:
            status = "Warning"
            eval_text = (
                f"At {temp:.1f} °C, elevated temperature accelerates shrimp basal metabolism while oxygen solubility drops. "
                f"Although digestive transit is fast, severe heat stress increases vulnerability to Vibrio infections. "
                f"Feeding must be carefully controlled to prevent catastrophic oxygen crashes."
            )
            rec_text = "Split daily feed into smaller, more frequent meals and run maximum aeration during digestion."
            actions = [
                f"Increase feeding frequency from {meals} to {min(6, meals + 2)} smaller meals per day.",
                "Verify DO levels remain above 4.5 mg/L in feeding zones 1 hour post-feeding.",
                "Apply vitamin C and immunostimulants to mitigate high-temperature oxidative stress."
            ]
        else:
            status = "Optimal"
            eval_text = (
                f"At {temp:.1f} °C, water temperature is in the prime metabolic window (28.0–32.0 °C) for Penaeus vannamei. "
                f"Protease and amylase enzyme activities are maximized. Standing biomass of {biomass:.1f} kg is supported "
                f"efficiently by {feed:.1f} kg/day across {meals} meals."
            )
            rec_text = "Maintain scheduled feeding distribution and confirm clean trays within 1.5–2.0 hours."
            actions = [
                "Verify tray clearance at 1.5–2 hours post-feed; if trays are clean, increase by 5% increments.",
                "Distribute feed evenly across the peripheral feeding track outside the central sludge zone.",
                "Perform weekly ABW sampling to adjust feeding percentages according to active biomass growth."
            ]

    elif module == "growth":
        fcr = float(data.get("fcr", 1.25))
        adwg = float(data.get("adwg", 0.22))
        sr = float(data.get("survival_rate", 85.0))

        if fcr > 1.6 or adwg < 0.15:
            status = "Warning"
            eval_text = (
                f"FCR of {fcr:.2f} and ADWG of {adwg:.3f} g/day indicate sub-optimal zootechnical conversion. "
                f"Feed is likely being wasted or environmental stressors (sub-optimal DO, fluctuating pH, or high TAN) "
                f"are shifting energy allocation from growth to physiological homeostasis."
            )
            rec_text = "Audit feeding tray protocols immediately and run biofloc/water remediation diagnostics."
            actions = [
                "Reduce daily feed allowance by 15% to eliminate unconsumed feed waste.",
                "Test morning DO and nighttime ammonia; verify DO does not fall below 4.0 mg/L.",
                "Examine shrimp hepatopancreas for lipid vacuolization and gut fullness."
            ]
        else:
            status = "Optimal"
            eval_text = (
                f"Survival rate ({sr:.1f}%), ADWG ({adwg:.3f} g/day), and FCR ({fcr:.2f}) align with top-tier "
                f"commercial Penaeus vannamei intensive culture standards. Feed utilization efficiency is excellent."
            )
            rec_text = "Maintain current dietary management and prepare harvest logistics based on biomass trajectory."
            actions = [
                "Continue weekly cast-net sampling to verify uniform weight distribution and shell hardness.",
                "Plan partial harvesting (thinning) if standing biomass approaches pond carrying capacity.",
                "Maintain biosecurity and probiotic consortium dosing to sustain zootechnical velocity."
            ]

    elif module == "ammonia":
        nh3 = float(data.get("nh3_ppm", 0.0224))
        if nh3 >= 0.08:
            status = "Critical"
            eval_text = (
                f"CRITICAL HAZARD: Toxic NH3 concentration ({nh3:.4f} ppm) exceeds the lethal threshold (>0.080 ppm) "
                f"for Penaeus vannamei. Ammonia diffuses freely across gill membranes, inducing severe gill gill necrosis, "
                f"hemolymph alkalosis, and acute mortality during molting."
            )
            rec_text = "Initiate emergency remediation immediately: suspend feeding and maximize paddlewheel aeration."
            actions = [
                "Immediately stop feeding to halt further nitrogen input.",
                "Exchange 20–30% bottom pond water if biosecure discharge is available.",
                "Apply cane molasses at 20:1 C:N ratio to stimulate heterotrophic ammonia assimilation."
            ]
        elif nh3 >= 0.03:
            status = "Warning"
            eval_text = (
                f"ELEVATED RISK: Toxic NH3 concentration ({nh3:.4f} ppm) is in the chronic stress range (0.030–0.080 ppm). "
                f"While not acutely lethal, shrimp exhibit lethargy, reduced feed consumption, and impaired immunity against Vibrio."
            )
            rec_text = "Reduce feeding by 30% and dose organic carbon (molasses) to stimulate bacterial TAN uptake."
            actions = [
                "Cut daily feed input by 25–30% until TAN drops below 0.50 ppm.",
                "Dose biofloc carbon source (molasses or sugar) to achieve a 15:1 C:N ratio.",
                "Monitor afternoon pH spikes, which drastically amplify toxic NH3 percentage."
            ]
        else:
            status = "Safe"
            eval_text = (
                f"OPTIMAL: Toxic unionized NH3 ({nh3:.4f} ppm) is well within the safe zootechnical limit (<0.030 ppm) "
                f"for Penaeus vannamei. Gill epithelium and osmoregulatory mechanisms remain fully protected."
            )
            rec_text = "Maintain routine water quality surveillance and standard biofloc carbon supplementation."
            actions = [
                "Continue twice-weekly TAN and pH monitoring to anticipate diurnal ammonia shifts.",
                "Preserve adequate alkalinity (>120 ppm) to buffer nitrifying bacteria activity.",
                "Ensure aerators maintain a clean peripheral feeding track."
            ]

    elif module == "co2":
        co2 = float(data.get("co2_ppm", 6.75))
        if co2 > 20.0:
            status = "Critical"
            eval_text = (
                f"CRITICAL HYPERCAPNIA: Free CO2 ({co2:.2f} mg/L) exceeds the toxicity threshold (>20.0 mg/L). "
                f"High carbon dioxide severely inhibits shrimp hemocyanin oxygen-binding affinity (Bohr effect), "
                f"causing suffocation even when dissolved oxygen levels appear adequate."
            )
            rec_text = "Run all aerators at maximum speed to strip CO2 and apply hydrated lime to neutralize carbonic acid."
            actions = [
                "Activate 100% of paddlewheel and aspirator aerators to mechanically degas CO2.",
                "Apply hydrated lime [Ca(OH)2] at 5–10 ppm to immediately precipitate free CO2 as CaCO3.",
                "Temporarily reduce feeding to minimize shrimp and microbial respiration rates."
            ]
        elif co2 >= 10.0:
            status = "Warning"
            eval_text = (
                f"ELEVATED CO2: Free CO2 ({co2:.2f} mg/L) is in the physiological stress bracket (10.0–20.0 mg/L). "
                f"Shrimp experience mild acidosis and sluggish feed response, particularly during pre-dawn hours."
            )
            rec_text = "Increase pre-dawn aeration hours and verify pond total alkalinity is above 120 mg/L."
            actions = [
                "Start supplemental aerators 2 hours before midnight to prevent dawn CO2 peaks.",
                "Supplement agricultural limestone (CaCO3) to elevate bicarbonate buffering capacity.",
                "Inspect phytoplankton density to prevent excessive nocturnal algal respiration."
            ]
        else:
            status = "Safe"
            eval_text = (
                f"OPTIMAL: Free CO2 ({co2:.2f} mg/L) is within the ideal range (<10.0 mg/L) for Penaeus vannamei. "
                f"Respiratory gas exchange and hemocyanin oxygen affinity remain completely unimpaired."
            )
            rec_text = "Maintain normal aeration schedules and balanced phytoplankton blooms."
            actions = [
                "Monitor pre-dawn pH and alkalinity to observe natural diurnal respiration cycles.",
                "Maintain total alkalinity between 120–160 mg/L as CaCO3.",
                "Ensure aerators create adequate surface agitation to prevent localized gas stratification."
            ]

    else:  # remediation
        lime_kg = float(data.get("lime_kg", 54.0))
        molasses_kg = float(data.get("molasses_kg", 18.4))
        aero_hp = float(data.get("aerator_hp", 3.0))

        status = "Optimal"
        eval_text = (
            f"Water remediation dosing balances carbonate buffering ({lime_kg:.1f} kg lime), "
            f"heterotrophic TAN assimilation ({molasses_kg:.1f} kg carbon), and nocturnal respiration ({aero_hp:.1f} HP aerator power) "
            f"for intensive Penaeus vannamei culture."
        )
        rec_text = "Apply chemical and biological treatments at appropriate diurnal windows for maximum bioavailability."
        actions = [
            f"Apply {lime_kg:.1f} kg lime slurry across aerator flow in early morning (7:00–9:00 AM).",
            f"Ferment {molasses_kg:.1f} kg molasses with probiotics for 4 hours; broadcast during morning aeration.",
            f"Run all {aero_hp:.1f} HP aerators continuously from 10:00 PM to 7:00 AM to cover nocturnal peak respiration."
        ]

    return {
        "status": status,
        "evaluation": eval_text,
        "recommendation": rec_text,
        "action_items": actions,
        "source": "ShrimpGuard Aquaculture Dynamic Engine (Fallback)",
        "cached": False,
        "module": module
    }


def get_calculator_ai_insight(module: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entry point:
    1. Checks in-memory cache for recent identical request (0ms, 0 API quota).
    2. Calls Google Gemini (via OpenAI-compatible endpoint configured in .env).
    3. Seamlessly falls back to dynamic Vannamei rule engine if offline or rate-limited.
    """
    cache_key = _get_cache_key(module, data)
    cached = _get_cached_insight(cache_key)
    if cached:
        return cached

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    base_url = os.getenv("OPENAI_BASE_URL", "").strip() or None
    model = os.getenv("OPENAI_MODEL", "gemini-3.5-flash").strip()

    # If key is unconfigured or dummy, return dynamic fallback immediately
    if not api_key or api_key == "your_openai_api_key_here":
        return _generate_fallback_insight(module, data)

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url=base_url, timeout=9.0, max_retries=1)

        system_prompt = _build_system_prompt()
        user_prompt = _build_module_prompt(module, data)

        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.35,
            max_tokens=2000,
        )

        raw_content = completion.choices[0].message.content or "{}"
        cleaned = raw_content.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            if cleaned.startswith("json"):
                cleaned = cleaned[4:].strip()

        result_json = json.loads(cleaned)

        provider_name = (
            "Google Gemini AI"
            if ("gemini" in model.lower() or "generativelanguage" in (base_url or "").lower())
            else "OpenAI API"
        )

        formatted_result = {
            "status": result_json.get("status", "Optimal"),
            "evaluation": result_json.get("evaluation", "Biological evaluation complete."),
            "recommendation": result_json.get("recommendation", "Continue routine monitoring."),
            "action_items": result_json.get("action_items", [result_json.get("recommendation", "Maintain monitoring.")]),
            "source": f"{provider_name} ({model})",
            "module": module,
            "cached": False
        }

        # Cache valid response
        _set_cached_insight(cache_key, formatted_result)
        return formatted_result

    except Exception as exc:
        logger.warning("Gemini AI API call failed for module '%s': %s; using dynamic Vannamei fallback.", module, exc)
        fallback = _generate_fallback_insight(module, data)
        fallback["error_note"] = str(exc)
        return fallback

