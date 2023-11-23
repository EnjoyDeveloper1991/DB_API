from fastapi import FastAPI
import random
import DBConnect

api = FastAPI()

@api.get('/random_number')
def random_no():
    val_random_number = random.randint(1, 10)

    json_object = {
        "key":val_random_number,
        "value":val_random_number * 10
    }
    return json_object

@api.get('/random_char')
def random_char():
    list_char = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    val_random_number = random.randint(1, 10)

    json_object = {
        "key":val_random_number,
        "value":list_char[val_random_number - 1]
    }
    #print(json_object)
    #json_string = json.dumps(json_object)
    #print(json_string)

    return json_object

@api.get('/GetUserLoginCheck')
def GetUserLoginCheck(id: str, pwd: str):
    conn = DBConnect.DBConnect()
    print(id, pwd)
    if conn:
        result_json = DBConnect.GetUserLoginCheck(conn, id, pwd)
    return result_json

@api.get("/GetUserInfo")
def GetUserInfo(id: str):
    conn = DBConnect.DBConnect()
    if conn:
        result_json = DBConnect.SelectUserInfo(conn, id)
    return result_json