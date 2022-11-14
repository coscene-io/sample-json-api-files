# -*- coding:utf-8 -*-
from cos import create_record_and_upload_files

# Account Specific
BEARER_TOKEN = "eyJraWQiOiI3ZTAwZWRjZC1mY2Q0LTQ5M2YtYmUxYy0yZWQ1ZDI0NWQxMDUiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIwNWMwOWZjMC0wMzcxLTRiMGItYmRlOS02MWJhOWYwMWMwODIiLCJpc3MiOiJodHRwczovL2FwaS5jb3NjZW5lLmNuL3N1cGVydG9rZW5zLXNlcnZlci9hdXRoIiwiZXhwIjoxNjY4NDE5MDM4LCJpYXQiOjE2NjgzOTc0MDcsIm9yZ0lkIjoiNmI0ZDhjOTgtY2M2Ny00N2VhLTk2MjUtZTdiMjk1YzQ2YmI4In0.Duq4lMi3otG9QNbOz783PUQB9ZaTEeTZjjTz8fQQIm2zKZniJ9BWhZ4Lz6v8DWaCwTiQx93BXa9UFAwr-75Dm7S4mUlINzuZRY9q3HknaUvXYkA5dvPH6gBvFs0y3bl6tWMfU2E3HLl8L29gpL4ACWxRSu9kem_7PDHy4d7hHNZqmENgHVtTvd3bLEhy_owoLBBaRac3isiLFWWZTRwim9w-yDuqjkrGdf6AIc9UcNgDP2v5pUWJgbharYf553KH2-NvtQcJlVk682pO_Lcl2KnL-YRrjYeI4BseAKb5rw2smwyW71Vx_AEO8QdeSNwTn2i1jFrCvsdFWuUowtfZqw"
WAREHOUSE_ID = "7ab79a38-49fb-4411-8f1b-dff4ae95b0e5"
PROJECT_ID = "8793e727-5ed9-4403-98a3-58906a975e55"
API_BASE = "https://api.coscene.cn"

if __name__ == "__main__":
    filepaths = ["./samples/3.jpg"]
    record_name = "Test Record"

    create_record_and_upload_files(API_BASE, BEARER_TOKEN, WAREHOUSE_ID, PROJECT_ID,
                                   record_name, filepaths)
