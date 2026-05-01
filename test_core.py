import unittest,numpy as np
from run import run
class Tests(unittest.TestCase):
 def test_report_reconciles(self):
  r=run(60); self.assertGreater(r['holdout'],50); self.assertLess(r['reconciliation_max_error'],1e-8)
if __name__=='__main__':unittest.main()
