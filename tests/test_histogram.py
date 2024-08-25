import unittest
import threading
from fastapi import HTTPException
from service.histogram import Histogram

class TestHistogram(unittest.TestCase):

    def setUp(self):
        self.histogram = Histogram()
        self.histogram.add_interval((0.0, 10.0))
        self.histogram.add_interval((10.0, 20.0))
        self.histogram.post_parse_operations()

    def test_add_interval(self):
        # Test adding intervals and ensuring they're stored correctly
        self.histogram.add_interval((20.0, 30.0))
        self.histogram.post_parse_operations()
        metrics = self.histogram.get_metrics()
        self.assertEqual(len(metrics["interval_counts"]), 3)

    def test_insert_sample_within_interval(self):
        # Test that samples within the defined intervals are counted correctly
        self.histogram.insert_samples([5.0, 15.0])
        metrics = self.histogram.get_metrics()
        self.assertEqual(metrics["interval_counts"]["[0.0, 10.0)"], 1)
        self.assertEqual(metrics["interval_counts"]["[10.0, 20.0)"], 1)
        self.assertEqual(metrics["sample_mean"], 10.0)
        self.assertEqual(metrics["sample_variance"], 25.0)
        self.assertEqual(metrics["outliers"], [])

    def test_insert_sample_outside_interval(self):
        # Test that samples outside of all intervals are counted as outliers
        self.histogram.insert_samples([25.0])
        metrics = self.histogram.get_metrics()
        self.assertEqual(metrics["outliers"], [25.0])

    def test_insert_multiple_samples(self):
        # Test that multiple samples are handled and metrics are calculated correctly
        self.histogram.insert_samples([1.0, 5.0, 15.0, 25.0])
        metrics = self.histogram.get_metrics()
        self.assertEqual(metrics["interval_counts"]["[0.0, 10.0)"], 2)
        self.assertEqual(metrics["interval_counts"]["[10.0, 20.0)"], 1)
        self.assertAlmostEqual(metrics["sample_mean"], 7, places=3)
        self.assertAlmostEqual(metrics["sample_variance"], 34.667, places=3)
        self.assertEqual(metrics["outliers"], [25.0])

    def test_no_samples_provided(self):
        # Test that metrics are correct when no samples have been inserted
        metrics = self.histogram.get_metrics()
        self.assertEqual(metrics["sample_mean"], 0)
        self.assertEqual(metrics["sample_variance"], 0)
        self.assertEqual(metrics["outliers"], [])

    def test_invalid_intervals(self):
        # Test handling of invalid intervals
        self.histogram.add_interval((5.0, 2.0))  # Invalid interval
        try:
            self.histogram.insert_samples([5.0])
        except ValueError as e:
            self.assertEqual(e.status_code, 500)
            self.assertEqual(str(e), "Invalid intervals found, please correct the intervals in intervals.txt file.")

    def test_overlapping_intervals(self):
        # Test handling of overlapping intervals
        self.histogram.add_interval((5.0, 15.0))  # Overlapping interval
        try:
            self.histogram.insert_samples([10.0])
        except ValueError as e:
            self.assertEqual(e.status_code, 500)
            self.assertEqual(str(e), "Overlapping intervals found, please correct the intervals in intervals.txt file.")

    def test_post_parse_operations(self):
        # Test that post_parse_operations correctly sorts intervals
        unsorted_intervals = [(20.0, 30.0), (0.0, 10.0), (10.0, 20.0)]
        self.histogram = Histogram()
        for interval in unsorted_intervals:
            self.histogram.add_interval(interval)
        self.histogram.post_parse_operations()
        metrics = self.histogram.get_metrics()
        self.assertEqual(list(metrics["interval_counts"].keys()), ['[0.0, 10.0)', '[10.0, 20.0)', '[20.0, 30.0)'])

    def test_thread_safety(self):
        # Test thread-safety with multiple threads inserting samples
        intervals = [(0, 2), (3, 4.1), (4.3, 4.5), (8.5, 8.7), (31.5, 41.27)]
        self.histogram = Histogram()
        for interval in intervals:
            self.histogram.add_interval(interval)
        
        num_threads = 5
        samples_per_thread = 100
        sample_value = 1.5  # Ensure this sample falls within one of the intervals

        def insert_samples_thread(samples):
            for _ in range(samples):
                self.histogram.insert_samples([sample_value])  # Insert a valid sample

        threads = []
        for _ in range(num_threads):
            thread = threading.Thread(target=insert_samples_thread, args=(samples_per_thread,))
            threads.append(thread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # Check that the total count matches the expected count
        expected_count = num_threads * samples_per_thread
        total_samples = self.histogram.get_total_samples()
        self.assertEqual(total_samples, expected_count)
   

if __name__ == "__main__":
    unittest.main()
