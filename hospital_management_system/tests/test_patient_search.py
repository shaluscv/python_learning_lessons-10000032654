import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch
from uuid import UUID

from src.models.data_populator import populate_user_data
from src.models.operation_manager import OperationManager
from src.models.specialization import Specialization
from src.user_data.patient import Patient


class PatientSearchTests(unittest.TestCase):
    def setUp(self):
        self.app = OperationManager()
        self.first = Specialization("Cardiology")
        self.second = Specialization("Neurology")
        self.app.specs = [self.first, self.second]
        self.alex = self.first.add_new_patient("Alex Smith", 0)
        self.other_alex = self.second.add_new_patient("Alex Smith", 2)

    def test_ids_are_distinct_valid_and_read_only(self):
        self.assertNotEqual(self.alex.patient_id, self.other_alex.patient_id)
        self.assertEqual(UUID(self.alex.patient_id).version, 4)
        original = self.alex.patient_id
        self.alex.name = "Updated"
        self.alex.status = 1
        self.assertEqual(self.alex.patient_id, original)
        with self.assertRaises(AttributeError):
            self.alex.patient_id = "replacement"

    def test_exact_id_search_across_specializations(self):
        result = self.app.search_patients(f" {self.other_alex.patient_id.upper()} ")
        self.assertEqual(result, [(self.second, self.other_alex)])
        self.assertEqual(self.app.search_patients(self.alex.patient_id[:8]), [])
        self.assertEqual(self.app.search_patients("not-an-id"), [])

    def test_partial_name_search_preserves_duplicate_names(self):
        result = self.app.search_patients("  ALEX s  ", "name")
        self.assertEqual(result, [
            (self.first, self.alex), (self.second, self.other_alex)
        ])
        self.assertEqual(self.app.search_patients("missing", "name"), [])

    def test_empty_query_and_invalid_mode(self):
        for mode in ("id", "name"):
            self.assertEqual(self.app.search_patients("  ", mode), [])
        with self.assertRaises(ValueError):
            self.app.search_patients("Alex", "unsupported")

    def test_removal_is_by_id_and_last_patient_returns_success(self):
        with redirect_stdout(io.StringIO()):
            self.assertFalse(self.first.remove_patient("Alex Smith"))
            self.assertTrue(self.first.remove_patient(self.alex.patient_id))
            self.assertFalse(self.first.remove_patient(self.alex.patient_id))
        self.assertEqual(self.first.patient_data_list, [])
        self.assertEqual(self.second.patient_data_list, [self.other_alex])
        self.assertEqual(self.app.search_patients(self.alex.patient_id), [])

    def test_duplicate_names_in_same_queue_can_be_removed_independently(self):
        duplicate = self.first.add_new_patient("Alex Smith", 1)
        with redirect_stdout(io.StringIO()):
            self.assertTrue(self.first.remove_patient(duplicate.patient_id))
        self.assertEqual(self.first.patient_data_list, [self.alex])

    def test_queue_constraints_and_fifo_are_preserved(self):
        with redirect_stdout(io.StringIO()):
            self.assertIsNone(self.first.add_new_patient("Invalid", 99))
            for index in range(9):
                self.first.add_new_patient(f"Patient {index}", 0)
            self.assertIsNone(self.first.add_new_patient("Overflow", 0))
            self.first.get_next_patient()
        self.assertEqual(len(self.first.patient_data_list), 9)
        self.assertEqual(self.app.search_patients(self.alex.patient_id), [])

    def test_populated_patients_receive_unique_ids(self):
        app = OperationManager()
        populate_user_data(app)
        ids = [
            patient.patient_id for spec in app.specs
            for patient in spec.patient_data_list
        ]
        self.assertEqual(len(ids), 30)
        self.assertEqual(len(set(ids)), 30)

    def test_listing_and_next_patient_display_ids(self):
        output = io.StringIO()
        with redirect_stdout(output):
            self.first.print_patients()
            self.first.get_next_patient()
        self.assertEqual(output.getvalue().count(self.alex.patient_id), 2)

    def test_console_search_and_remove(self):
        output = io.StringIO()
        answers = [
            "6", "name", "alex", "6", "id", self.other_alex.patient_id,
            "3", self.other_alex.patient_id, "5",
        ]
        with patch("builtins.input", side_effect=answers), redirect_stdout(output):
            self.app.run()
        text = output.getvalue()
        self.assertIn(self.alex.patient_id, text)
        self.assertIn(self.other_alex.patient_id, text)
        self.assertIn("Neurology Specialization", text)
        self.assertIn("Super Emergency", text)
        self.assertEqual(self.second.patient_data_list, [])

    def test_console_invalid_and_empty_searches(self):
        answers = [
            "6", "bad-mode", "6", "name", " ", "6", "id", "missing", "5"
        ]
        output = io.StringIO()
        with patch("builtins.input", side_effect=answers), redirect_stdout(output):
            self.app.run()
        self.assertIn("Invalid search mode", output.getvalue())
        self.assertIn("Search query cannot be empty", output.getvalue())
        self.assertIn("No matching patients", output.getvalue())

    def test_console_registration_reports_id(self):
        app = OperationManager()
        output = io.StringIO()
        with patch("builtins.input", side_effect=["1", "General", "Sam", "0", "5"]):
            with redirect_stdout(output):
                app.run()
        patient = app.specs[0].patient_data_list[0]
        self.assertIn(patient.patient_id, output.getvalue())

    def test_console_rejected_registration_does_not_report_success(self):
        app = OperationManager()
        output = io.StringIO()
        with patch("builtins.input", side_effect=["1", "General", "Sam", "99", "5"]):
            with redirect_stdout(output):
                app.run()
        self.assertEqual(app.specs, [])
        self.assertNotIn("Patient added", output.getvalue())


if __name__ == "__main__":
    unittest.main()
