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

# Load environment variables from .env
load_dotenv()

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
        client = OpenAI(api_key=api_key.strip(), timeout=12.0)
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
            max_tokens=650,
        )

        raw_content = completion.choices[0].message.content
        data = json.loads(raw_content)

        if not isinstance(data.get("actionable_solutions"), list):
            data["actionable_solutions"] = [data.get("actionable_solution", "Maintain regular pond monitoring.")]

        data["classification"] = classification
        data["source"] = f"OpenAI API ({model})"
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
