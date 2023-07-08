# import sys
# sys.path.insert(0, './src/import_s3')
# from handler import handler

# # Black box tests for import function.
# # Tests all valid and invalid paths through the function.


# # Test case 1 - success case
# def test_fetch_success():
#     response = handler(None, None)
#     print(response)
#     assert response["statusCode"] == 200
#     assert "data_source" in response["body"]
#     assert "dataset_type" in response["body"]
#     assert "dataset_id" in response["body"]
#     assert "time_object" in response["body"]
#     assert "events" in response["body"]
