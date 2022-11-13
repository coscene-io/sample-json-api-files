# -*- coding:utf-8 -*-
from cos import create_record_and_upload_files

# Account Specific
BEARER_TOKEN = "eyJraWQiOiI2YmE0N2Y0My02MWZkLTRlOGYtODhjMy05MTZjZTU3YjZlY2IiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJhYmQ4OTBmMC1iMDViLTQwZjktOTllOC02YzFkMjI4ZmU4M2MiLCJpc3MiOiJodHRwczovL2FwaS5jb3NjZW5lLmRldi9zdXBlcnRva2Vucy1zZXJ2ZXIvYXV0aCIsImV4cCI6MTY2ODM3NjQ0NSwiaWF0IjoxNjY4MzU0ODE0LCJvcmdJZCI6IjNmZjkxOGM3LTVkOGQtNDA0Yy1iZWJiLWU1NDk4NTI3ZDg5NSJ9.IWIIE4C5t-Fj8sjG_fBSG4HJCs_kYMj7TR4kV3DcariaURakNGCLLn4gQiRD2xltuCWiGWsDSuukZ8UJzIT54V3xcQMnyYq_EW56wVb2l6ZDWsOLjBDYhKfr6IE0kyP9zL1MyibowD5fOKZfL-O6jQpjk2a1KnEPGz3QcPZWOVQVQ63Lr4NK7GYDmapSy_hQqUb_g5PSGEUKwI3bI2QI4jQi8PFWlCiAIFa38Wx2Xd5S78f7JSVLsaT-z7Lr_-dpRxw26y2y3M8O5QOupl9aTAEUeJDnX9TU77bmHgmektBOP31v0dAXqTKF_KHEAjRAl3J0tZsNKOS9FD84nKQ-NA"
WAREHOUSE_ID = "1c593c01-eaa3-4b85-82ed-277494820866"
PROJECT_ID = "2b329c23-2d16-4290-a586-c7ad63b6f1d1"

if __name__ == "__main__":
    filepaths = ["./samples/3.jpg"]
    record_name = "Test Record"

    create_record_and_upload_files(BEARER_TOKEN, WAREHOUSE_ID, PROJECT_ID,
                                   record_name, filepaths)
