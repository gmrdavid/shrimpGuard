import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from co2_service import (
    TUCKER_TEMPS,
    TUCKER_PH_LEVELS,
    TUCKER_TABLE,
    get_tucker_factor,
    calculate_free_co2
)
from app import AQUACULTURE_EXPORT_CATEGORIES, AquacultureCalculation

class TestCo2Integration(unittest.TestCase):

    def test_tucker_table_nodes(self):
        # Verify specific nodes from the uploaded Tucker (1984) Table 2 image
        self.assertEqual(TUCKER_TABLE[6.0][0], 2.915)  # 5 C
        self.assertEqual(TUCKER_TABLE[6.0][6], 1.839)  # 35 C
        self.assertEqual(TUCKER_TABLE[7.0][4], 0.197)  # 25 C
        self.assertEqual(TUCKER_TABLE[7.6][4], 0.050)  # 25 C
        self.assertEqual(TUCKER_TABLE[7.6][5], 0.047)  # 30 C
        self.assertEqual(TUCKER_TABLE[8.4][6], 0.007)  # 35 C

    def test_interpolation_and_calculation(self):
        # 28 C and pH 7.60
        # 28 C is 60% between 25 C (0.050) and 30 C (0.047)
        # 0.050 + 0.6 * (0.047 - 0.050) = 0.0482
        factor = get_tucker_factor(28.0, 7.60)
        self.assertAlmostEqual(factor, 0.0482, places=4)

        result = calculate_free_co2(alkalinity=140.0, temp=28.0, ph=7.60)
        self.assertEqual(result["status"], "Safe (< 10.0 mg/L)")
        self.assertEqual(result["badge_class"], "badge-optimal")
        self.assertAlmostEqual(result["co2_mg_l"], 6.748, places=3)

    def test_high_co2_warning_and_critical(self):
        # High alkalinity and lower pH (e.g. pH 6.8 at 28 C, factor ~ 0.304)
        # Alk = 100 mg/L -> CO2 ~ 30.4 mg/L -> Critical
        result_crit = calculate_free_co2(alkalinity=100.0, temp=28.0, ph=6.8)
        self.assertEqual(result_crit["status"], "Critical Stress (> 20.0 mg/L)")
        self.assertEqual(result_crit["badge_class"], "badge-critical")

        # Elevated range (e.g. 15 mg/L)
        result_elev = calculate_free_co2(alkalinity=50.0, temp=28.0, ph=6.8)
        self.assertEqual(result_elev["status"], "Elevated (10.0–20.0 mg/L)")
        self.assertEqual(result_elev["badge_class"], "badge-warning")

    def test_alkaline_negligible(self):
        result_alk = calculate_free_co2(alkalinity=140.0, temp=28.0, ph=8.6)
        self.assertIn("Negligible", result_alk["status"])

    def test_app_export_categories_and_model(self):
        self.assertIn("co2", AQUACULTURE_EXPORT_CATEGORIES)
        co2_cat = AQUACULTURE_EXPORT_CATEGORIES["co2"]
        self.assertEqual(co2_cat["title"], "Free Carbon Dioxide (CO2) Concentration")
        col_attrs = [c[1] for c in co2_cat["columns"]]
        self.assertIn("co2_alkalinity_mg_l", col_attrs)
        self.assertIn("co2_temp_c", col_attrs)
        self.assertIn("co2_ph", col_attrs)
        self.assertIn("co2_factor", col_attrs)
        self.assertIn("co2_concentration_mg_l", col_attrs)
        self.assertIn("co2_status", col_attrs)

        # Check model columns exist
        for attr in col_attrs:
            self.assertTrue(hasattr(AquacultureCalculation, attr), f"Missing model attribute {attr}")

    def test_html_template_elements(self):
        template_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates", "calculators.html"))
        with open(template_path, "r", encoding="utf-8") as f:
            html = f.read()

        # Section exists below ammonia
        self.assertIn('id="tools-co2-section"', html)
        self.assertIn('id="tools-co2-alkalinity"', html)
        self.assertIn('id="tools-co2-result"', html)
        self.assertIn('id="tools-co2-badge"', html)
        self.assertIn('id="tools-co2-live-temp"', html)
        self.assertIn('id="tools-co2-live-ph"', html)
        self.assertIn('id="tools-co2-override-cb"', html)
        self.assertIn('id="tools-co2-custom-temp"', html)
        self.assertIn('id="tools-co2-custom-ph"', html)
        self.assertIn('id="open-tools-tucker"', html)

        # Tucker modal exists
        self.assertIn('id="tools-tucker-modal"', html)
        self.assertIn('id="tools-tucker-matrix"', html)
        self.assertIn('data-temp="35"', html)
        self.assertIn('data-ph="8.4"', html)

        # Save snapshot & Export modal
        self.assertIn('id="save-preview-co2"', html)
        self.assertIn('id="card-cat-co2"', html)
        self.assertIn('value="co2"', html)

if __name__ == "__main__":
    unittest.main()
