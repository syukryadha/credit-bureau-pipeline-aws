import pytest
import tempfile
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),"..")))

from transform.validate import validate_with_pandas

def test_validate_clean_rows_returned():
    csv_content ="""customer_id,name,ic_number,loan_amount
C001,Ahmad Razif,800101-14-5678,50000
C002,Siti Norzahra,920303-08-1234,30000"""
    with tempfile.NamedTemporaryFile(mode="w", suffix = ".csv", delete=False) as f:
        f.write(csv_content)
        tmp_path = f.name

    result = validate_with_pandas(tmp_path)

    assert type(result) is list
    assert len(result) == 2

    os.remove(tmp_path)

def test_validate_null_name_row_dropped():
    csv_content ="""customer_id,name,ic_number,loan_amount
C001,,800101-14-5678,50000
C002,Siti Norzahra,920303-08-1234,30000"""
    with tempfile.NamedTemporaryFile(mode="w",suffix=".csv",delete=False) as f:
        f.write(csv_content)
        tmp_path = f.name

    result = validate_with_pandas(tmp_path)

    assert type(result) is list
    assert len(result) == 1

    os.remove(tmp_path)

def test_validate_negative_loan_amount_dropped():
    csv_content = """customer_id,name,ic_number,loan_amount
C001,Ahmad Razif,800101-14-5678,-50000
C002,Siti Norzahra,920303-08-1234,30000"""
    with tempfile.NamedTemporaryFile(mode="w",suffix=".csv",delete=False) as f:
        f.write(csv_content)
        tmp_path= f.name
    
    result= validate_with_pandas(tmp_path)

    assert len(result) == 1

    os.remove(tmp_path)

def test_validate_duplicate_customer_id_dropped():
    csv_content="""customer_id,name,ic_number,loan_amount
C001,Ahmad Razif,800101-14-5678,50000
C001,Siti Norzahra,920303-08-1234,30000"""
    with tempfile.NamedTemporaryFile(mode="w",suffix=".csv",delete=False) as f:
        f.write(csv_content)
        tmp_path=f.name
    
    result = validate_with_pandas(tmp_path)

    assert len(result) == 1

    os.remove(tmp_path)