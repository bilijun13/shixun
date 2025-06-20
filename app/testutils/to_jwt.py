import jwt

'''解码jwt令牌'''

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc1MDQwNzMxOSwianRpIjoiM2ZmOTc4YmYtMWUyNy00YjJkLTkxZTUtMzlhNWRiMGYwZmJhIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MSwibmJmIjoxNzUwNDA3MzE5LCJjc3JmIjoiOTg2OTIwMzAtNTQ3ZC00NWY4LWI4MDktNmRkNWEzNDVjNmI0IiwiZXhwIjoxNzUwNDEwOTE5fQ.Q8Sqx3p5bHIdoGjEqG_RXAd4XCr3FS8m5UTwy8aTu9k"
secret = "dSwUNTPrBXLN60RVdbUsPN1CU5l0OArPrpdB6sQVHvs"

decoded = jwt.decode(token, secret, algorithms=["HS256"], options={"verify_signature": False})
print(decoded)  # 查看sub字段类型