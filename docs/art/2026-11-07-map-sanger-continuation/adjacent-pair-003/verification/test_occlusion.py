"""Regression checks for the observed W rooftop obstruction; no files are written."""
import copy
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import build_pair_evidence as builder
import verify_pair as verifier


class OcclusionNavigationTests(unittest.TestCase):
    def marked_graph(self):
        graph = json.loads((HERE / 'actual-pair-graph.json').read_text())
        graph = copy.deepcopy(graph)
        for edge in graph['edges']:
            edge['navigationAllowed'] = edge['id'] != 'W-h-0-2'
        return graph

    def test_observed_rooftop_segment_is_disabled_at_source(self):
        edge = next(e for e in builder.local_graph('W')['edges'] if e['id'] == 'W-h-0-2')
        self.assertIs(edge.get('navigationAllowed'), False)

    def test_reroute_never_uses_disabled_rooftop_segment(self):
        route = builder.route(self.marked_graph(), 'W-n-1-0', 'E-n-1-3', 'W-h-1-2')
        self.assertNotIn('W-h-0-2', route['edgeIds'])
        self.assertNotIn('W-h-1-2', route['edgeIds'])

    def test_independent_shortest_path_honours_navigation_exclusion(self):
        graph = self.marked_graph()
        removed = {**graph, 'edges': [e for e in graph['edges'] if e['navigationAllowed']]}
        actual = verifier.shortest_distance(graph, 'W-n-1-0', 'E-n-1-3', 'W-h-1-2')
        expected = verifier.shortest_distance(removed, 'W-n-1-0', 'E-n-1-3', 'W-h-1-2')
        self.assertAlmostEqual(actual, expected, places=8)

    def test_verifier_rejects_old_route_crossing_rooftop(self):
        old = json.loads((HERE / 'history/before-occlusion-fix/actual-pair-graph.json').read_text())
        with self.assertRaises(AssertionError):
            verifier.check_route(self.marked_graph(), old['routes']['alternative-route'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
