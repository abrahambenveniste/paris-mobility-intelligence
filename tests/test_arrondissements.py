import unittest
from prepare_public import validate_areas


class ArrondissementTests(unittest.TestCase):
    def test_requires_all_twenty_distinct_areas_and_valid_geometry(self):
        ring = [[2.3, 48.8], [2.4, 48.8], [2.4, 48.9], [2.3, 48.8]]
        rows = [{'c_ar': i, 'l_aroff': str(i), 'geom': {'geometry': {'type': 'Polygon', 'coordinates': [ring]}}} for i in range(1, 21)]
        self.assertEqual(len(validate_areas({'total_count': 20, 'results': rows})), 20)
        with self.assertRaises(ValueError):
            validate_areas({'total_count': 20, 'results': rows[:-1]})
