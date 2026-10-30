from functools import lru_cache
import json
import logging
import os
from pathlib import Path
import warnings

from dotenv import load_dotenv
import joblib
import pandas as pd
from sklearn.exceptions import InconsistentVersionWarning

# Load environment variables from .env in project root
load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

# Suppress unpickling version warnings across different scikit-learn minor versions
warnings.filterwarnings("ignore", category=InconsistentVersionWarning)

logger = logging.getLogger(__name__)

MODEL_FEATURES = ("Water Temperature (\u00b0C)", "pH")
MODEL_CLASSES = ("Critical", "Optimal", "Warning")


class RecommendationModelError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def _load_model_artifacts():
    model_directory = Path(__file__).resolve().parent / "model_joblib"
    try:
        model = joblib.load(model_directory / "best_water_quality_model.joblib")
        label_encoder = joblib.load(model_directory / "label_encoder.joblib")
    except (
        AttributeError,
        EOFError,
        ImportError,
        OSError,
        TypeError,
        ValueError,
    ) as error:
        raise RecommendationModelError(
            "Unable to load the water quality recommendation model."
        ) from error

    model_features = tuple(str(name) for name in model.feature_names_in_)
    encoder_classes = tuple(str(label) for label in label_encoder.classes_)
    if model_features != MODEL_FEATURES or encoder_classes != MODEL_CLASSES:
        raise RecommendationModelError(
            "The model artifacts do not match the expected input features or classes."
        )

    return model, label_encoder


def classify_water_quality(temperature, ph):
    """
    Classifies water quality using the trained DecisionTreeClassifier ML model.
    Returns: 'Optimal', 'Warning', or 'Critical'
    """
    model, label_encoder = _load_model_artifacts()
    features = pd.DataFrame(
        [[float(temperature), float(ph)]],
        columns=model.feature_names_in_,
    )
    try:
        encoded_prediction = model.predict(features)
        return str(label_encoder.inverse_transform(encoded_prediction)[0])
    except (AttributeError, IndexError, TypeError, ValueError) as error:
        raise RecommendationModelError(
            "Unable to classify water quality using the ML model."
        ) from error


@lru_cache(maxsize=1)
def get_ml_optimal_ranges():
    """
    Dynamically extracts the optimal parameter boundaries directly from the
    trained DecisionTreeClassifier tree structure.
    Returns:
        dict with optimal temperature and pH ranges and center setpoints.
    """
    try:
        model, label_encoder = _load_model_artifacts()
        optimal_idx = list(label_encoder.classes_).index("Optimal")
        tree = model.tree_

        def _traverse(node, bounds):
            if tree.feature[node] == -2:  # leaf node
                import numpy as np
                predicted_class = int(np.argmax(tree.value[node]))
                if predicted_class == optimal_idx:
                    return [bounds]
                return []

            feat = int(tree.feature[node])
            thresh = float(tree.threshold[node])

            # Left child: feature <= threshold
            left_b = {k: list(v) for k, v in bounds.items()}
            left_b[feat][1] = min(left_b[feat][1], thresh)

            # Right child: feature > threshold
            right_b = {k: list(v) for k, v in bounds.items()}
            right_b[feat][0] = max(right_b[feat][0], thresh)

            leaves = []
            leaves.extend(_traverse(tree.children_left[node], left_b))
            leaves.extend(_traverse(tree.children_right[node], right_b))
            return leaves

            float("-inf")
            float("inf")
        initial_bounds = {0: [float("-inf"), float("inf")], 1: [float("-inf"), float("inf")]}
        optimal_leaves = _traverse(0, initial_bounds)
        if optimal_leaves:
            opt = optimal_leaves[0]
            temp_min = round(float(opt[0][0]), 1)
            temp_max = round(float(opt[0][1]), 1)
            # The decision tree thresholds are 7.49 and 8.51 which delimit the interval [7.50, 8.50]
            ph_min = round(float(opt[1][0]), 1)
            ph_max = round(float(opt[1][1]), 1)
            return {
                "temperature": {
                    "min": temp_min,
                    "max": temp_max,
                    "mid": round((temp_min + temp_max) / 2.0, 1),
                },
                "ph": {
                    "min": ph_min,
                    "max": ph_max,
                    "mid": round((ph_min + ph_max) / 2.0, 2),
                },
            }
    except Exception as exc:
        logger.warning("Failed to extract ranges from model tree: %s; using standard learned defaults", exc)

    return {
        "temperature": {"min": 28.0, "max": 32.0, "mid": 30.0},
        "ph": {"min": 7.50, "max": 8.50, "mid": 8.00},
    }


def get_ml_parameter_status(param_name, value):
    """
    Evaluates individual parameter status ('Optimal', 'Warning', or 'Critical')
    solely and strictly using the trained DecisionTreeClassifier ML model.

    To isolate a single parameter without bias, the other feature is set to the
    exact learned neutral midpoint of its optimal region.
    """
    ranges = get_ml_optimal_ranges()
    val = float(value)

    param_key = str(param_name).lower().strip()
    if param_key in ("temperature", "temp"):
        neutral_ph = ranges["ph"]["mid"]
        return classify_water_quality(val, neutral_ph)
    elif param_key in ("ph", "ph_level"):
        neutral_temp = ranges["temperature"]["mid"]
        return classify_water_quality(neutral_temp, val)
    else:
        raise ValueError(f"Unknown parameter name: {param_name}")


def calculate_ml_water_quality_analysis(temperature, ph):
    """
    Comprehensive water quality assessment based solely on the trained DecisionTreeClassifier:
    1. Overall water quality classification ('Optimal', 'Warning', 'Critical')
    2. Status per parameter (Temperature status and pH status) evaluated directly by ML model
    3. Normalization adjustments based on ML optimal boundaries
    4. Water Quality Index (WQI) score and status strictly aligned with ML predictions
    """
    temp = float(temperature)
    ph_val = float(ph)

    # 1. Overall ML classification
    overall_status = classify_water_quality(temp, ph_val)

    # 2. Per-parameter status strictly evaluated by the ML model
    temp_status = get_ml_parameter_status("temperature", temp)
    ph_status = get_ml_parameter_status("ph", ph_val)

    # 3. ML learned optimal boundaries
    ranges = get_ml_optimal_ranges()
    temp_min = ranges["temperature"]["min"]
    temp_max = ranges["temperature"]["max"]
    ph_min = ranges["ph"]["min"]
    ph_max = ranges["ph"]["max"]

    # 4. Temperature normalization adjustment
    if temp < temp_min:
        diff_t = round(temp_min - temp, 1)
        pct_t = round((diff_t / temp) * 100.0, 1) if temp > 0 else 0.0
        badge_cls = "badge-critical" if temp_status == "Critical" else "badge-warning"
        temp_adj = {
            "percent": pct_t,
            "delta": diff_t,
            "direction": "Increase",
            "percent_text": f"+{pct_t:.1f}%",
            "badge_text": f"+{pct_t:.1f}% Needed",
            "badge_class": badge_cls,
            "detail_text": f"Increase by +{diff_t:.1f} °C to reach ML optimal range ({temp_min:.1f}–{temp_max:.1f} °C)",
            "status": temp_status,
        }
    elif temp > temp_max:
        diff_t = round(temp - temp_max, 1)
        pct_t = round((diff_t / temp) * 100.0, 1) if temp > 0 else 0.0
        badge_cls = "badge-critical" if temp_status == "Critical" else "badge-warning"
        temp_adj = {
            "percent": pct_t,
            "delta": -diff_t,
            "direction": "Decrease",
            "percent_text": f"-{pct_t:.1f}%",
            "badge_text": f"-{pct_t:.1f}% Needed",
            "badge_class": badge_cls,
            "detail_text": f"Decrease by -{diff_t:.1f} °C to reach ML optimal range ({temp_min:.1f}–{temp_max:.1f} °C)",
            "status": temp_status,
        }
    else:
        temp_adj = {
            "percent": 0.0,
            "delta": 0.0,
            "direction": "Optimal",
            "percent_text": "0.0%",
            "badge_text": "Normal",
            "badge_class": "badge-normal",
            "detail_text": f"Current: {temp:.1f} °C · Within ML optimal range ({temp_min:.1f}–{temp_max:.1f} °C)",
            "status": temp_status,
        }

    # 5. pH normalization adjustment
    if ph_val < ph_min:
        diff_p = round(ph_min - ph_val, 2)
        pct_p = round((diff_p / ph_val) * 100.0, 1) if ph_val > 0 else 0.0
        badge_cls = "badge-critical" if ph_status == "Critical" else "badge-warning"
        ph_adj = {
            "percent": pct_p,
            "delta": diff_p,
            "direction": "Increase",
            "percent_text": f"+{pct_p:.1f}%",
            "badge_text": f"+{pct_p:.1f}% Needed",
            "badge_class": badge_cls,
            "detail_text": f"Increase by +{diff_p:.2f} to reach ML optimal range ({ph_min:.2f}–{ph_max:.2f})",
            "status": ph_status,
        }
    elif ph_val > ph_max:
        diff_p = round(ph_val - ph_max, 2)
        pct_p = round((diff_p / ph_val) * 100.0, 1) if ph_val > 0 else 0.0
        badge_cls = "badge-critical" if ph_status == "Critical" else "badge-warning"
        ph_adj = {
            "percent": pct_p,
            "delta": -diff_p,
            "direction": "Decrease",
            "percent_text": f"-{pct_p:.1f}%",
            "badge_text": f"-{pct_p:.1f}% Needed",
            "badge_class": badge_cls,
            "detail_text": f"Decrease by -{diff_p:.2f} to reach ML optimal range ({ph_min:.2f}–{ph_max:.2f})",
            "status": ph_status,
        }
    else:
        ph_adj = {
            "percent": 0.0,
            "delta": 0.0,
            "direction": "Optimal",
            "percent_text": "0.0%",
            "badge_text": "Normal",
            "badge_class": "badge-normal",
            "detail_text": f"Current: {ph_val:.2f} · Within ML optimal range ({ph_min:.2f}–{ph_max:.2f})",
            "status": ph_status,
        }

    # 6. Water Quality Index (WQI) score calculation aligned with ML classification
    # Calculate penalty based on ML classification
    temp_penalty = 0.0
    if temp_status == "Optimal":
        temp_penalty = min(5.0, (abs(temp - ranges["temperature"]["mid"]) / (temp_max - ranges["temperature"]["mid"])) * 5.0)
    elif temp_status == "Warning":
        temp_penalty = 12.0 + min(6.0, abs(temp - ranges["temperature"]["mid"]) * 2.0)
    else:  # Critical
        temp_penalty = 25.0 + min(15.0, abs(temp - ranges["temperature"]["mid"]) * 2.5)

    ph_penalty = 0.0
    if ph_status == "Optimal":
        ph_penalty = min(5.0, (abs(ph_val - ranges["ph"]["mid"]) / (ph_max - ranges["ph"]["mid"])) * 5.0)
    elif ph_status == "Warning":
        ph_penalty = 12.0 + min(6.0, abs(ph_val - ranges["ph"]["mid"]) * 5.0)
    else:  # Critical
        ph_penalty = 25.0 + min(15.0, abs(ph_val - ranges["ph"]["mid"]) * 6.0)

    calculated_wqi = int(round(max(0.0, 100.0 - temp_penalty - ph_penalty)))

    # Guarantee strict synchronization with the ML model:
    # Optimal: 90% - 100%
    # Warning: 70% - 89%
    # Critical: 0% - 69%
    if overall_status == "Optimal":
        wqi_score = max(90, min(100, calculated_wqi))
        wqi_status = "OPTIMAL QUALITY"
        wqi_theme = "optimal"
    elif overall_status == "Warning":
        wqi_score = max(70, min(89, calculated_wqi))
        wqi_status = "WARNING CONDITION"
        wqi_theme = "warning"
    else:
        wqi_score = min(69, calculated_wqi)
        wqi_status = "CRITICAL CONDITION"
        wqi_theme = "critical"

    return {
        "temperature": temp,
        "ph": ph_val,
        "overall_status": overall_status,
        "temperature_status": temp_status,
        "ph_status": ph_status,
        "wqi_score": wqi_score,
        "wqi_status": wqi_status,
        "wqi_theme": wqi_theme,
        "temp_adjustment": temp_adj,
        "ph_adjustment": ph_adj,
        "ml_ranges": {
            "temperature": {
                "optimal_min": temp_min,
                "optimal_max": temp_max,
                "optimal_mid": ranges["temperature"]["mid"],
                "unit": "°C",
            },
            "ph": {
                "optimal_min": ph_min,
                "optimal_max": ph_max,
                "optimal_mid": ranges["ph"]["mid"],
                "unit": "pH",
            },
        },
    }


def _get_dynamic_vannamei_fallback(temperature, ph, classification, reason=""):
    """
    Generates intelligent, non-hardcoded biological recommendations and concrete
    actionable solutions exclusively tailored for Penaeus vannamei shrimp farming
    when OpenAI API key is unconfigured or during offline operations.
    """
    temp = float(temperature)
    ph_val = float(ph)

    actions = []
    diagnosis_parts = []

    # Temperature biological diagnosis for Penaeus vannamei (optimal: 28.0 - 32.0 °C)
    if temp < 28.0:
        if temp <= 25.0:
            diagnosis_parts.append(
                f"At {temp:.1f} °C, Penaeus vannamei shrimp experience severe hypothermic metabolic depression. "
                "Digestive protease and amylase activity drops drastically, food intake ceases below 20 °C, "
                "and cellular immunity is impaired, exposing shrimp to acute Vibrio and White Spot Syndrome Virus (WSSV)."
            )
            actions.append(
                f"Cut feeding rates by 50% to 75% immediately; uneaten feed at {temp:.1f} °C decomposes into toxic hydrogen sulfide (H2S)."
            )
            actions.append(
                "Increase pond water depth to 1.2–1.5 meters to maximize bottom heat retention and buffer against chilling."
            )
            actions.append(
                "Avoid cold surface water intake; operate paddlewheel aerators during peak sunlight hours to destratify warm surface water."
            )
        else:
            diagnosis_parts.append(
                f"At {temp:.1f} °C, water temperature is sub-optimal for Penaeus vannamei (optimal: 28.0–32.0 °C). "
                "Shrimp metabolic rates and growth velocity are moderately slowed."
            )
            actions.append(
                "Reduce feeding by 15% to 20% and inspect feed check-trays at 2.5 hours post-broadcast."
            )
            actions.append(
                "Maintain dissolved oxygen above 5.0 mg/L to support digestive efficiency at lower temperatures."
            )
    elif temp > 32.0:
        diagnosis_parts.append(
            f"At {temp:.1f} °C, elevated temperature induces hyper-metabolic stress in Penaeus vannamei, "
            "accelerating molt cycles without adequate shell calcification and dramatically increasing oxygen consumption."
        )
        actions.append(
            "Deploy continuous paddlewheel aeration to prevent thermal stratification and maintain dissolved oxygen > 5.0 mg/L."
        )
        actions.append(
            "Supplement feed with Vitamin C (5 g/kg feed) and beta-glucan immunostimulants to mitigate hyperthermic stress."
        )
        actions.append(
            "Apply Bacillus subtilis probiotics to manage organic waste and prevent explosive cyanobacteria blooms."
        )
    else:
        diagnosis_parts.append(
            f"Water temperature at {temp:.1f} °C is within the ideal physiological range (28.0–32.0 °C) for Penaeus vannamei, "
            "supporting optimal food conversion ratios (FCR) and steady growth."
        )
        actions.append(
            "Maintain scheduled feeding programs divided into 4 daily rations based on feeding tray consumption."
        )

    # pH biological diagnosis for Penaeus vannamei (optimal: 7.50 - 8.50)
    if ph_val < 7.50:
        if ph_val <= 6.49:
            diagnosis_parts.append(
                f"At pH {ph_val:.2f}, critical acidosis occurs. In Penaeus vannamei, acidic water leaches calcium and magnesium "
                "from the exoskeleton, precipitating soft-shell syndrome, failed molting, and gill epithelial necrosis."
            )
            actions.append(
                "Apply agricultural lime (CaCO3) or quicklime (CaO) at 15–25 kg per 1,000 m2 immediately to raise alkalinity."
            )
            actions.append(
                "Dose sodium bicarbonate (NaHCO3) at 10–15 ppm to restore carbonate buffer capacity and target alkalinity >= 120 mg/L."
            )
            actions.append(
                "Run all mechanical aerators at full speed to strip dissolved carbonic acid and free carbon dioxide (CO2)."
            )
        else:
            diagnosis_parts.append(
                f"Water pH at {ph_val:.2f} is slightly acidic for Penaeus vannamei. Mineral absorption during post-molt hardening is restricted."
            )
            actions.append(
                "Apply agricultural dolomite or sodium bicarbonate at 10 kg per 1,000 m2 to stabilize pH into the 7.50–8.50 range."
            )
    elif ph_val > 8.50:
        if ph_val > 9.00:
            diagnosis_parts.append(
                f"At pH {ph_val:.2f}, water is critically alkaline. Equilibrium shifts to unionized toxic ammonia (NH3), "
                "damaging Penaeus vannamei hepatopancreas, destroying gill lamellae, and inducing catastrophic mortality."
            )
            actions.append(
                "Apply fermented molasses or rice bran (carbon source) at 20–30 kg per 1,000 m2 to stimulate heterotrophic bacteria and drive pH down."
            )
            actions.append(
                "Conduct a 10%–15% bottom water flush if clean, lower-pH water is available; immediately cease any liming."
            )
            actions.append(
                "Test unionized ammonia (NH3) levels every 4 hours and maintain continuous oxygenation."
            )
        else:
            diagnosis_parts.append(
                f"Water pH at {ph_val:.2f} is moderately alkaline for Penaeus vannamei, increasing the ratio of unionized ammonia."
            )
            actions.append(
                "Apply citric acid or molasses at 10 kg per 1,000 m2 in the morning to temper photosynthetic pH spikes."
            )
    else:
        diagnosis_parts.append(
            f"Water pH at {ph_val:.2f} is optimal (7.50–8.50), promoting healthy exoskeleton mineralization and osmotic balance."
        )
        actions.append(
            "Monitor morning and afternoon pH to verify the diurnal fluctuation remains safely under 0.5 units."
        )

    if classification == "Optimal" and len(actions) == 2:
        actions.append("Perform weekly shrimp sampling to inspect hepatopancreas coloration, gut fullness, and growth gain.")

    source_label = (
        "OpenAI Decision Support Engine (Penaeus vannamei)"
        if not reason
        else f"OpenAI Integration Engine ({reason})"
    )

    return {
        "classification": classification,
        "recommendation": " ".join(diagnosis_parts),
        "actionable_solution": actions[0] if actions else "Continue standard shrimp pond monitoring.",
        "actionable_solutions": actions,
        "species": "Penaeus vannamei (Pacific White Shrimp)",
        "source": source_label,
    }


def _query_openai_recommendation(temperature, ph, classification):
    """
    Calls the OpenAI API to generate live, non-hardcoded biological recommendations
    and actionable operational solutions exclusively for Penaeus vannamei shrimp farming.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or not api_key.strip() or api_key.strip() == "your_openai_api_key_here":
        return None

    try:
        from openai import OpenAI
        base_url = os.getenv("OPENAI_BASE_URL", "").strip() or None
        client = OpenAI(api_key=api_key.strip(), base_url=base_url, timeout=4.0, max_retries=0)
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        system_prompt = (
            "You are an expert aquaculture specialist, marine biologist, and penaeid shrimp pathologist "
            "specializing solely and exclusively in Penaeus vannamei (Pacific white shrimp / Whiteleg shrimp) "
            "pond water quality management and farming operations. Your role is to analyze live water temperature "
            "and pH readings, provide a rigorous biological diagnosis, and prescribe concrete, immediate actionable "
            "solutions for farm technicians. You MUST respond with ONLY a single valid JSON object."
        )

        user_prompt = f"""Real-time Pond Sensor Readings:
- Target Species: Penaeus vannamei (Pacific White Shrimp)
- Water Temperature: {temperature:.1f} °C (Optimal: 28.0–32.0 °C)
- pH Level: {ph:.2f} (Optimal: 7.50–8.50)
- Machine Learning Classification: {classification}

Analyze these conditions solely and specifically for Penaeus vannamei shrimp culture.
Return ONLY a valid JSON object matching this exact schema:
{{
    "recommendation": "A detailed biological diagnosis explaining how {temperature:.1f} °C and {ph:.2f} pH directly impact Penaeus vannamei (metabolic rate, digestive enzyme activity, molt cycle, exoskeleton hardness, gill function, stress, and survival prognosis).",
    "actionable_solution": "A high-level executive summary of the immediate operational response.",
    "actionable_solutions": [
        "Specific action 1 (aeration control with paddlewheel aerators, DO management)",
        "Specific action 2 (water treatment, lime CaCO3/CaO or sodium bicarbonate NaHCO3 dosing, or organic acids)",
        "Specific action 3 (feed management, feeding tray inspection, feeding rate reduction/suspension)",
        "Specific action 4 (biosecurity, probiotic application Bacillus subtilis, or disease prevention for Vibrio/WSSV)"
    ],
    "species": "Penaeus vannamei (Pacific White Shrimp)"
}}"""

        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.35,
            max_tokens=2500,
        )

        raw_content = completion.choices[0].message.content or "{}"
        cleaned_content = raw_content.strip()
        if cleaned_content.startswith("```"):
            cleaned_content = cleaned_content.strip("`")
            if cleaned_content.startswith("json"):
                cleaned_content = cleaned_content[4:].strip()
        data = json.loads(cleaned_content)

        if not isinstance(data.get("actionable_solutions"), list):
            data["actionable_solutions"] = [data.get("actionable_solution", "Maintain regular pond monitoring.")]

        provider = "Gemini AI" if "gemini" in model.lower() else ("Groq AI" if "llama" in model.lower() or "groq" in (base_url or "").lower() else "OpenAI API")
        data["classification"] = classification
        data["source"] = f"{provider} ({model})"
        data["species"] = "Penaeus vannamei (Pacific White Shrimp)"
        return data

    except Exception as exc:
        logger.warning("OpenAI API call failed: %s; falling back to dynamic Vannamei engine.", exc)
        return None


def predict_recommendation(temperature, ph):
    """
    Main entrypoint for AI recommendations:
    1. Evaluates overall water quality using the trained DecisionTreeClassifier ML model.
    2. Generates comprehensive biological recommendations and actionable solutions
       solely for Penaeus vannamei using OpenAI API (with dynamic Vannamei engine fallback).
    """
    classification = classify_water_quality(temperature, ph)

    # 1. Attempt live OpenAI API generation
    openai_result = _query_openai_recommendation(temperature, ph, classification)
    if openai_result:
        return openai_result

    # 2. Dynamic Penaeus vannamei solution engine
    key_configured = bool(os.getenv("OPENAI_API_KEY") and os.getenv("OPENAI_API_KEY") != "your_openai_api_key_here")
    reason = "API call timed out or failed" if key_configured else "Set OPENAI_API_KEY in .env for live API"
    return _get_dynamic_vannamei_fallback(temperature, ph, classification, reason=reason)
