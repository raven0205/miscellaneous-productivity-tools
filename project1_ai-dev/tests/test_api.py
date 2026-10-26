import unittest
import json
from app import app, init_db, DB_FILE
import os

class APITestCase(unittest.TestCase):
    def setUp(self):
        # Force a fresh DB for tests
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
        init_db()
        self.app = app.test_client()

    def test_metrics(self):
        res = self.app.get('/api/metrics')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn('rpr', data)
        self.assertEqual(data['pendingApprovals'], 1)

    def test_approvals(self):
        res = self.app.get('/api/approvals')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(len(data) > 0)
        self.assertEqual(data[0]['status'], 'pending')

    def test_webhook_responder_agent(self):
        alert_payload = {
            "alerts": [{"status": "firing", "labels": {"alertname": "HighRejectionRate"}}]
        }
        res = self.app.post('/webhook/alert', json=alert_payload)
        self.assertEqual(res.status_code, 200)
        
        # Check if alert status became critical
        res_metrics = self.app.get('/api/metrics')
        data = json.loads(res_metrics.data)
        self.assertEqual(data['alertStatus'], 'critical')

if __name__ == '__main__':
    unittest.main()
