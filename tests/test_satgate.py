import os,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import satgate
class TestDemo(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory()
  satgate.DB_PATH=os.path.join(self.tmp.name,"db.sqlite3")
  satgate.init_db()
 def tearDown(self):self.tmp.cleanup()
 def test_order(self):
  o=satgate.create_order("supporter","my_unique_request_id")
  self.assertEqual(o["sats"],2500)
  self.assertEqual(satgate.get_order(o["id"])["status"],"pending")
 def test_idempotency(self):
  a=satgate.create_order("supporter","same_request_id_1")
  b=satgate.create_order("supporter","same_request_id_1")
  self.assertEqual(a["id"],b["id"])
 def test_cross_product_rejected(self):
  satgate.create_order("supporter","same_request_id_2")
  with self.assertRaises(ValueError):satgate.create_order("builder","same_request_id_2")
 def test_invalid_product(self):
  with self.assertRaises(ValueError):satgate.create_order("nope","request_012345")
 def test_fake_settlement(self):
  o=satgate.create_order("builder","request_012346")
  self.assertEqual(satgate.simulate_settle(o["id"])["status"],"settled")
 def test_invalid_order_id(self):self.assertIsNone(satgate.get_order("../invalid"))
if __name__=="__main__":unittest.main()
