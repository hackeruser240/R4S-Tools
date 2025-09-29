import unittest
from unittest.mock import patch, MagicMock
from functions_folder import keyword_monitor

class TestKeywordMonitor(unittest.TestCase):
    def test_create_timestamped_folder(self):
        with patch("os.makedirs") as makedirs:
            folder = keyword_monitor.create_timestamped_folder("test_folder")
            self.assertTrue(folder.startswith("test_folder"))
            makedirs.assert_called_once()

    @patch("requests.get")
    def test_perform_google_search_success(self, mock_get):
        mock_get.return_value.json.return_value = {"items": [{"title": "SEO Tools"}]}
        result = keyword_monitor.perform_google_search("SEO Tools", "fake_key", "fake_cx")
        self.assertIn("items", result)

    @patch("requests.get", side_effect=Exception("Network error"))
    def test_perform_google_search_failure(self, mock_get):
        result = keyword_monitor.perform_google_search("SEO Tools", "fake_key", "fake_cx")
        self.assertIn("error", result)

    def test_find_keyword_rank_found(self):
        search_results = {
            "items": [
                {"title": "Best SEO Tools", "link": "http://example.com", "snippet": "SEO tools overview"}
            ]
        }
        rank, item = keyword_monitor.find_keyword_rank("SEO Tools", search_results)
        self.assertEqual(rank, 1)
        self.assertIsNotNone(item)

    def test_find_keyword_rank_not_found(self):
        search_results = {"items": [{"title": "Other", "link": "http://example.com", "snippet": "No match"}]}
        rank, item = keyword_monitor.find_keyword_rank("SEO Tools", search_results)
        self.assertIsNone(rank)
        self.assertIsNone(item)

    @patch("builtins.open", new_callable=MagicMock)
    def test_save_json(self, mock_open):
        data = {"test": "data"}
        folder_path = "test_folder"
        filename = "test.json"
        keyword_monitor.save_json(data, folder_path, filename)
        mock_open.assert_called_once()

if __name__ == "__main__":
    unittest.main()