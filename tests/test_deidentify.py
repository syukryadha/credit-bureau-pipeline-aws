import tempfile
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),"..")))

from transform.deidentify import deidentify

def test_deidentify():
    csv_content ="""token|credit_score|risk_tier
TKN-001|720|LOW
TKN-003|440|HIGH"""
    with tempfile.NamedTemporaryFile(mode="w",suffix=".csv",delete = False) as f:
        f.write(csv_content)
        tmp_path = f.name

        token_map={"TKN-001":"C001", "TKN-003":"C003"}
        loan_map ={"C001":70000, "C003":50000}


    processed_rows, count_output_valid_rows = deidentify(tmp_path, token_map, loan_map)

    assert isinstance(processed_rows,list)
    assert isinstance(count_output_valid_rows,int)

    assert {'customer_id','credit_score','risk_tier','loan_amount','processed_date'} == set(processed_rows[0].keys()) 

    os.remove(tmp_path)
