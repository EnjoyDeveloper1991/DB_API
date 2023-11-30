from fastapi import FastAPI
import random
import uvicorn
import DBConnect

"""
    Get     : 데이터 가져오기
    Post    : 데이터 생성
    Put     : 데이터 업데이트
    Delete  : 데이터 삭제
"""
api = FastAPI()

# FastAPI 서버 실행
if __name__ == "__main__":
    uvicorn.run("db_api:api", host="0.0.0.0", port=8000, reload=True)

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


## 로그인 및 계정정보 추출 ##
@api.get('/GetUserLoginCheck')
def GetUserLoginCheck(id: str, pwd: str):
    conn = DBConnect.DBConnect()
    if conn:
        result_json = DBConnect.GetUserLoginCheck(conn, id, pwd)
    return result_json

## 도서명으로 도서 검색 (취향을 포함하여 반환) ##
@api.get('/GetBookSearch')
def GetBookSearch(book_name: str):
    conn = DBConnect.DBConnect()
    if conn:
        result_json = DBConnect.GetBookSearch(conn, book_name)
    return result_json

## 취향명으로 취향리스트 추출 ##
@api.get('/GetPreferencesNameList')
def GetPreferencesNameList(preference_name: str, like_option: bool):
    conn = DBConnect.DBConnect()
    if conn:
        result_json = DBConnect.GetPreferencesNameList(conn, preference_name, like_option)
    return result_json

## 사용자 취향목록 추출 ##
@api.get('/GetUserPreferenceList')
def GetUserPreferenceList(user_id: str):
    conn = DBConnect.DBConnect()
    if conn:
        result_json = DBConnect.GetUserPreferenceList(conn, user_id)
    return result_json



## 사용자 취향 생성 (Insert) ##
@api.get('/PostUserPreferences')
def PostUserPreferences(user_id: str, preference_ids: str):
    conn = DBConnect.DBConnect()
    if conn:
        result_json = DBConnect.PostUserPreferences(conn, user_id, preference_ids)
    return result_json



"""
## User 취향정보 입력(Insert)
@api.post("/PostUserPreferences")
def PostUserPreferences(id: str, preference_ids: str):
        conn = DBConnect.DBConnect()
        if conn:
            result_json = DBConnect.PostUserPreferences(conn, id, preference_ids)
        return result_json
"""