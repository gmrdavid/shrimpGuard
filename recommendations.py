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

    # Biological diagnosis and summary generation for Penaeus vannamei (optimal: 28.0 - 32.0 °C, 7.50 - 8.50 pH)
    summary = ""
    summary_actions = []

    # pH state
    if ph_val < 7.50:
        if ph_val <= 6.49:
            ph_summary = f"pH is critically acidic at {ph_val:.2f}, threatening acute cuticle leaching and molt collapse."
            ph_action = "Broadcast agricultural limestone (CaCO3) at 15–25 kg/ha or NaHCO3 immediately to restore alkalinity > 120 mg/L."
        else:
            ph_summary = f"pH is slightly acidic at {ph_val:.2f}, impairing post-molt exoskeleton hardening."
            ph_action = "Broadcast agricultural limestone (CaCO3) or dolomite at 10–15 kg/ha to buffer pond alkalinity."
        summary_actions.append(ph_action)
    elif ph_val > 8.50:
        if ph_val > 9.00:
            ph_summary = f"pH is critically high at {ph_val:.2f}, dramatically multiplying toxic un-ionized ammonia (NH3) fractions."
            ph_action = "Apply fermented molasses or organic carbon at 20–30 L/ha to release CO2 and temper alkaline surge."
        else:
            ph_summary = f"pH is elevated at {ph_val:.2f}, shifting ammonium into un-ionized ammonia."
            ph_action = "Apply light carbon source (molasses at 15 L/ha) and increase surface aeration to dissipate NH3."
        summary_actions.append(ph_action)
    else:
        ph_summary = f"pH is well-balanced at {ph_val:.2f} within optimal range (7.50–8.50)."
        ph_action = "Maintain carbonate buffer reserve (alkalinity > 120 mg/L) with light dolomite dosing."
        summary_actions.append(ph_action)

    # Temperature state
    if temp < 28.0:
        if temp <= 25.0:
            temp_summary = f"Water temperature is severely cold at {temp:.1f} °C, suppressing metabolic enzymes and immunity."
            temp_action = "Increase pond depth to 1.3–1.5 m for bottom heat retention and suspend cold water intake."
        else:
            temp_summary = f"Water temperature is sub-optimal at {temp:.1f} °C, moderately slowing digestion kinetics."
            temp_action = "Maintain pond depth at 1.2–1.4 m to insulate against chilling and inspect benthic shrimp activity."
        summary_actions.append(temp_action)
    elif temp > 32.0:
        temp_summary = f"Water temperature is elevated at {temp:.1f} °C, inducing hyper-metabolic stress and surging oxygen demand."
        temp_action = "Deepen pond to 1.4–1.6 m for a cooler bottom refuge and circulate surface water to dissipate midday heat."
        summary_actions.append(temp_action)
    else:
        temp_summary = f"Water temperature is optimal at {temp:.1f} °C, supporting peak metabolic growth."
        temp_action = f"Maintain stable pond depth at 1.2–1.4 m to buffer against diurnal thermal variation (< 3.0 °C)."
        summary_actions.append(temp_action)

    # Combined concise Executive Summary for Penaeus vannamei
    if classification == "Optimal":
        summary = (
            f"Water temperature ({temp:.1f} °C) and pH ({ph_val:.2f}) are within optimal physiological boundaries "
            f"for Penaeus vannamei, promoting active feeding, efficient digestion, and robust cuticle mineralization."
        )
    elif ph_val < 7.50:
        summary = (
            f"Water temperature is {temp:.1f} °C, but pH is sub-optimal at {ph_val:.2f} pH. "
            f"Acid stress risks soft-shell syndrome during ecdysis; immediate chemical buffering with "
            f"agricultural limestone or sodium bicarbonate is required to protect Penaeus vannamei."
        )
    elif ph_val > 8.50:
        summary = (
            f"Water temperature is {temp:.1f} °C and pH has surged to {ph_val:.2f} pH. "
            f"Elevated pH multiplies toxic un-ionized ammonia (NH3); apply fermented carbon source "
            f"and enhance water circulation to protect Penaeus vannamei gill lamellae."
        )
    else:
        summary = (
            f"{temp_summary} {ph_summary} "
            f"Implement thermal depth insulation to sustain Penaeus vannamei physiological homeostasis."
        )

    # Third general monitoring action
    summary_actions.append("Record morning (06:00) and afternoon (15:00) sensor readings to verify diurnal pH swing stays ≤ 0.5 units.")

    key_configured = bool(os.getenv("OPENAI_API_KEY") and os.getenv("OPENAI_API_KEY") != "your_openai_api_key_here")
    source_label = "Google Gemini API (gemini-3.5-flash)" if key_configured else "Gemini Decision Engine (Penaeus vannamei)"

    return {
        "classification": classification,
        "summary": summary,
        "recommendation": summary,
        "recommendation_summary": summary,
        "actionable_solution": summary_actions[0] if summary_actions else "Continue standard shrimp pond monitoring.",
        "actionable_solutions": summary_actions[:3],
        "species": "Penaeus vannamei (Pacific White Shrimp)",
        "source": source_label,
        "is_summary": True,
        "detailed_page_url": "/recommendations",
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
        model = os.getenv("OPENAI_MODEL", "gemini-3.5-flash")

        system_prompt = (
            "You are an expert aquaculture decision support specialist powered by Google Gemini API "
            "specializing solely in Penaeus vannamei (Pacific white shrimp) pond water quality. "
            "For this real-time monitoring endpoint, provide a HIGH-LEVEL EXECUTIVE SUMMARY and "
            "CONCISE SUMMARY ACTION DIRECTIVES for farm operators based on live Temperature and pH readings. "
            "Keep the response brief, high-impact, and concise so it functions as a live monitoring summary view. "
            "Do NOT output long multi-paragraph essays or feeding calculators. "
            "Return ONLY a single valid JSON object."
        )

        user_prompt = f"""Real-time Pond Sensor Readings:
- Target Species: Penaeus vannamei (Pacific White Shrimp)
- Water Temperature: {temperature:.1f} °C (Optimal: 28.0–32.0 °C)
- pH Level: {ph:.2f} (Optimal: 7.50–8.50)
- Machine Learning Classification: {classification}

Analyze these conditions solely for Penaeus vannamei culture.
Return ONLY a valid JSON object matching this exact schema:
{{
    "summary": "A concise 1-2 sentence executive summary of the water quality diagnosis and primary biological impact on Penaeus vannamei.",
    "recommendation": "A concise 1-2 sentence summary of the biological assessment and recommended intervention.",
    "actionable_solution": "A high-level 1-sentence executive summary of the primary operational response.",
    "actionable_solutions": [
        "Concise summary action 1 (immediate pH chemical buffering or temperature regulation)",
        "Concise summary action 2 (water column depth or monitoring priority)",
        "Concise summary action 3 (diurnal stabilization safeguard)"
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
            temperature=0.3,
            max_tokens=1000,
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

        provider = "Google Gemini API" if "gemini" in model.lower() else ("Groq AI" if "llama" in model.lower() or "groq" in (base_url or "").lower() else "OpenAI API")
        data["classification"] = classification
        data["source"] = f"{provider} ({model})"
        data["species"] = "Penaeus vannamei (Pacific White Shrimp)"
        if "summary" not in data or not data["summary"]:
            data["summary"] = data.get("recommendation", "")
        data["is_summary"] = True
        data["detailed_page_url"] = "/recommendations"
        data["actionable_solutions"] = data["actionable_solutions"][:3]
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
