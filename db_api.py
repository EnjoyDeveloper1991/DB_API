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

## 취향명으로 취향리스트 추출(랜덤) ##
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

## 책의 취향정보를 가져와서, 사용자 취향 정보에 추가 ##
@api.get('/AddBookToUserPreferences')
def AddBookToUserPreferences(user_id: str, book_id: str):
    conn = DBConnect.DBConnect()
    if conn:
        result_json = DBConnect.AddBookToUserPreferences(conn, user_id, book_id)
    return result_json

## 사용자 북마크 생성 (Insert) ##
@api.get('/PostAddBookmark')
def PostAddBookmark(user_id: str, book_id: str):
    conn = DBConnect.DBConnect()
    if conn:
        result_json = DBConnect.PostAddBookmark(conn, user_id, book_id)
    return result_json

## 사용자 북마크 삭제 (Delete) ##
@api.get('/DeleteBookmark')
def DeleteBookmark(user_id: str, book_id: str):
    conn = DBConnect.DBConnect()
    if conn:
        result_json = DBConnect.DeleteBookmark(conn, user_id, book_id)
    return result_json

## 사용자 북마크 목록 추출 (취향을 포함하여 반환) (SELECT) ##
@api.get('/GetUserBookmarkList')
def GetUserBookmarkList(user_id: str):
    conn = DBConnect.DBConnect()
    if conn:
        result_json = DBConnect.GetUserBookmarkList(conn, user_id)
    return result_json

#사용자 정보입력
@api.get('/PostUpdateUserInfo')
def PostUpdateUserInfo(user_nicname: str, user_gender: str, user_age: int, user_time: str, user_id: str):
    conn = DBConnect.DBConnect()
    if conn:
        result_json = DBConnect.PostUpdateUserInfo(conn, user_nicname, user_gender, user_age, user_time, user_id)
    return result_json
