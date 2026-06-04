from transform.anonymize import anonymize


def test_anonymize():
    list_dict = [
        {
            "customer_id": "C001",
            "name": "Abu",
            "ic_number": "39",
            "loan_amount": "10000"
        },
        {
            "customer_id": "C002",
            "name": "Ali",
            "ic_number": "42",
            "loan_amount": "70000"}
    ]

    anonymized_rows, token_map, loan_map = anonymize(list_dict)

    assert isinstance(anonymized_rows, list)
    assert isinstance(token_map, dict)
    assert isinstance(loan_map, dict)

    for row in list_dict:
        expected_token = f"TKN-{row['customer_id'][1:]}"
        assert token_map[expected_token] == row["customer_id"]
