import pymssql
import json
import random
import numpy as np
#     print(row[0], row[1].encode('ISO-8859-1').decode('euc-kr'))
#     print(row[0], row[1].encode('ISO-8859-1').decode('cp949'))

# GET       SELECT  데이터 가져오기
# POST      INSERT  데이터 생성
# PUT	    UPDATE  데이터 업데이트
# DELETE	DELETE  데이터 삭제
# PATCH     UPDATE  데이터 부분 업데이트

## fetchall과 fetchone의 차이
## fetchall : 모든 행을 한번에 가져옴
## fecthone : 행을 하나씩 가져옴

## MSSQL 접속
def DBConnect():
    #server = '172.16.104.69:1433'       # 김진영 부천대 Local
    server = '192.168.45.172:1433'     # 김진영 HOME Local
    #server = '222.108.212.104:1433'
    #server = '172.16.114.196:1433'     # 이세호 부천대 Local
    #server = '192.168.219.104:1433'    # 도성대 HOME Local
    database = 'dnb'
    username = 'sa'
    password = '1234'                   # 김진영 HOME
    #password = 'Qwer1234'              # 도성대 HOME
    charset = 'utf8'
    try:
        conn = pymssql.connect(server, username, password, database)
        return conn
    except Exception as e:
        print(f"MSSQL 연결 중 오류가 발생했습니다. {str(e)}")
        return None

## MSSQL 닫기
def DBClose(conn):
    try:
        conn.close()
    except Exception as e:
        print(f"MSSQL 연결을 종료하던 중 오류가 발생했습니다. {str(e)}")
        return None
    
## 로그인 및 계정정보 추출 ##
def GetUserLoginCheck(conn, u_id, u_pwd):
    query = 'SELECT * FROM USER_INFO WHERE u_id = %s AND u_pwd = %s'
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(query, (u_id, u_pwd))
        user_data = cursor.fetchone()

        if user_data:
            data = {
                "login_yn": "y",
                "message": "로그인 성공",
                "user_info": user_data  # 로그인한 사용자의 모든 정보
            }
            user_data.pop('u_pwd')
            user_data['u_name'] = user_data['u_name'].encode('ISO-8859-1').decode('cp949')
            user_data['u_nicname'] = user_data['u_nicname'].encode('ISO-8859-1').decode('cp949')
            user_data['u_time'] = user_data['u_time'].strftime('%Y-%m-%d %H:%M:%S')
        else:
            data = {
                "login_yn": "n",
                "message": "실패 : 아이디가 존재하지 않거나 비밀번호가 일치하지 않습니다.",
                "user_info": None  # 로그인 실패 시 정보 없음
            }
        return data
    except Exception as e:
        print(f"MSSQL 쿼리 실행 중 오류 발생 {str(e)}")
        return "" #None

## 도서명으로 도서 검색 (취향을 포함하여 반환) ##
def GetBookSearch(conn, book_name):
    book_name = '%' + book_name + '%'  # 부분 일치하는 문자열을 만듬
    query = f'''SELECT b_id, b_name, b_aut, b_ps, b_date, b_short, b_detail, b_img,
		        ISNULL(STUFF((SELECT ',' + pi.p_name FROM BOOK_PREFERENCE bp JOIN PREFERENCE_INFO pi ON bp.p_id = pi.p_id WHERE bi.b_id = bp.b_id FOR XML PATH('')), 1, 1, ''), '') AS p_names
                FROM BOOK_INFO bi
                WHERE b_name LIKE %s
            '''
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(query, (book_name,))
        rows = cursor.fetchall()
        b = 1
        if rows:  # 책 정보가 있다면
            books = []
            for row in rows:
                book = {
                    "b_id": row['b_id'],
                    "b_name": row['b_name'].encode('ISO-8859-1').decode('cp949'),
                    "b_aut": row['b_aut'].encode('ISO-8859-1').decode('cp949'),
                    "b_ps": row['b_ps'].encode('ISO-8859-1').decode('cp949'),
                    "b_date": row['b_date'],
                    "b_short": row['b_short'].encode('ISO-8859-1').decode('cp949'),
                    "b_detail": row['b_detail'].encode('ISO-8859-1').decode('cp949'),
                    "b_img": row['b_img'].encode('ISO-8859-1').decode('cp949'),
                    "p_names": list(row['p_names'].split(','))
                }
                books.append(book)
            return books
        else:  # 책 정보가 없다면
            data = {
                "message": "책 정보를 찾을 수 없습니다."
            }
            return data
    except Exception as e:
        print(f"MSSQL 쿼리 실행 중 오류 발생 {str(e)}")
        return None

## 취향명으로 취향목록 추출 (랜덤) ##  *** 전체조회도 가능 
def GetPreferencesNameList(conn, preference_name, like_option):
    if like_option == True:
        preference_name = '%' + preference_name + '%'  # 부분 일치하는 문자열을 만듬
        query = f"SELECT * FROM PREFERENCE_INFO WHERE p_name LIKE %s"
    else:
        query = f"SELECT * FROM PREFERENCE_INFO WHERE p_name = %s"

    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(query, (preference_name,))
        rows = cursor.fetchall()
        
        if rows:  # 취향정보가 있다면
            preferences = []
            for row in rows:
                preference = {
                    "p_id": row['p_id'],
                    "p_name": row['p_name'].encode('ISO-8859-1').decode('cp949')
                }
                preferences.append(preference)
                np.random.shuffle(preferences)                                  # 랜덤으로 정렬 - numpy 모듈 설치 필요
                #random.shuffle(preferences)                                    # 랜덤으로 정렬 - 너무 느림
                #preferences = random.sample(preferences, len(preferences))     # 랜덤으로 정렬 - 더 느림
            return preferences
        else:  # 취향정보가 없다면
            data = {
                "message": "취향정보가 존재하지 않습니다."
            }
            return data
    except Exception as e:
        print(f"MSSQL 쿼리 실행 중 오류 발생 {str(e)}")
        return None

## 사용자 취향목록 추출 ##
def GetUserPreferenceList(conn, user_id):
    if user_id == "":
        data = {
            "message": "사용자ID가 입력되지 않았습니다."
        }
        return data
    else:
        query = f"SELECT pi.p_id, pi.p_name FROM USER_PREFERENCE as up, PREFERENCE_INFO as pi WHERE up.u_id = %s And up.p_id = pi.p_id"
        try:
            cursor = conn.cursor(as_dict=True)
            cursor.execute(query, (user_id,))
            rows = cursor.fetchall()
            user_preferences = []

            if rows:  # 사용자 취향정보가 존재하면?
                for row in rows:
                    user_preference = {
                        "p_id": row['p_id'],
                        "p_name": row['p_name'].encode('ISO-8859-1').decode('cp949')
                    }
                    user_preferences.append(user_preference)
            return user_preferences
        except Exception as e:
            print(f"MSSQL 쿼리 실행 중 오류 발생 {str(e)}")
            return None

## 사용자 취향 생성 (Insert) ##
def PostUserPreferences(conn, user_id, preference_ids):
    try:
        if user_id == "":
            data = {
                "message": "사용자ID가 입력되지 않았습니다."
            }
        elif preference_ids == "":
            data = {
                "message": "취향ID가 입력되지 않았습니다. (여러 건일 경우 ,로 구분)"
            }
        else:
            for preference_id in preference_ids.split(','):
                check_query = f"SELECT * FROM USER_PREFERENCE WHERE u_id = %s AND p_id = %s"
                cursor = conn.cursor()
                cursor.execute(check_query, (user_id, preference_id,))
                rows = cursor.fetchone()

                if rows:  # 등록된 취향정보가 존재한다면 작업하지 않음
                    continue
                else: # 등록된 취향정보가 없다면 등록
                    insert_query = f"INSERT INTO USER_PREFERENCE (u_id, p_id) VALUES (%s, %s)"
                    cursor = conn.cursor()
                    cursor.execute(insert_query, (user_id, preference_id,))
            conn.commit()
            data = {
                "message": "Success"
            }
        return data
    except Exception as e:
        conn.rollback()  # 롤백하여 이전 상태로 복구
        data = {
            "message": "취향 입력 중 오류 발생"
        }
        return data

## 책의 취향정보를 가져와서, 사용자 취향 정보에 추가 ##
def AddBookToUserPreferences(conn, user_id, book_id):
    try:
        # 해당 책의 취향 정보 가져오기
        book_query = f"SELECT p_id FROM BOOK_PREFERENCE WHERE b_id = %s"
        cursor = conn.cursor()
        cursor.execute(book_query, (book_id,))
        book_preferences_rows = cursor.fetchall()

        if book_preferences_rows:
            # 사용자의 취향 정보에 추가할 취향 정보 찾기
            user_preferences = []
            for pref in book_preferences_rows:
                user_pref_query = f"SELECT p_id FROM USER_PREFERENCE WHERE u_id = %s AND p_id = %s"
                cursor.execute(user_pref_query, (user_id, pref[0],))
                user_pref_exists = cursor.fetchone()
                if not user_pref_exists:
                    print(pref[0])
                    user_preferences.append((user_id, pref[0],))

            # 사용자의 취향 정보에 추가하기
            if user_preferences:
                insert_user_pref_query = f"INSERT INTO USER_PREFERENCE (u_id, p_id) VALUES (%s, %s)"
                cursor.executemany(insert_user_pref_query, user_preferences)
                conn.commit()
                data = {
                    "message": "Success"
                }
                return data
            else:
                data = {
                    "message": "사용자의 취향 정보에 추가할 새로운 정보 없음"
                }
                return data
        else:
            data = {
                "message": "해당 책의 취향 정보가 없음"
            }
            return data 
    except Exception as e:
        print(f"Error adding book preferences to user: {str(e)}")
        conn.rollback()
        data = {
            "message": "취향 정보 추가 실패"
        }
        return data

## 사용자 북마크 생성 (Insert) ##
def PostAddBookmark(conn, user_id, book_id):
    try:
        if user_id == "":
            data = {
                "message": "사용자ID가 입력되지 않았습니다."
            }
        elif book_id == "":
            data = {
                "message": "책ID가 입력되지 않았습니다."
            }
        else:
            check_query = f"SELECT * FROM BOOKMARK WHERE u_id = %s AND b_id = %s"
            cursor = conn.cursor()
            cursor.execute(check_query, (user_id, book_id,))
            rows = cursor.fetchone()

            if rows: # 이미 Bookmark가 존재할 경우 작업하지 않음
                data = {
                    "message": "이미 등록된 북마크"
                }
            else: # 등록된 취향정보가 없다면 등록
                insert_query = f"INSERT INTO BOOKMARK (u_id, b_id, b_regist) VALUES (%s, %s, GETDATE())"
                cursor = conn.cursor()
                cursor.execute(insert_query, (user_id, book_id,))
                conn.commit()
                data = {
                    "message": "Success"
                }
        return data
    except Exception as e:
        print(f"Error adding to bookmark: {str(e)}")
        conn.rollback()  # 롤백하여 이전 상태로 복구
        data = {
            "message": "북마크 등록 실패"
        }
        return data

## 사용자 북마크 삭제 (Delete) ##
def DeleteBookmark(conn, user_id, book_id):
    try:
        if user_id == "":
            data = {
                "message": "사용자ID가 입력되지 않았습니다."
            }
        elif book_id == "":
            data = {
                "message": "책ID가 입력되지 않았습니다."
            }
        else:
            check_query = f"SELECT * FROM BOOKMARK WHERE u_id = %s AND b_id = %s"
            cursor = conn.cursor()
            cursor.execute(check_query, (user_id, book_id,))
            rows = cursor.fetchone()

            if rows: # 이미 Bookmark가 존재할 경우 삭제
                delete_query = f"DELETE BOOKMARK WHERE u_id = %s AND b_id = %s"
                cursor = conn.cursor()
                cursor.execute(delete_query, (user_id, book_id,))
                conn.commit()
                data = {
                    "message": "Success"
                }
            else: # Bookmark가 존재하지 않으면 Pass
                data = {
                    "message": "존재하지 않는 북마크"
                }
        return data
    except Exception as e:
        print(f"Error delete to bookmark: {str(e)}")
        conn.rollback()  # 롤백하여 이전 상태로 복구
        data = {
            "message": "북마크 삭제 실패"
        }
        return data

## 사용자 북마크 목록 추출 (취향을 포함하여 반환) ##
def GetUserBookmarkList(conn, user_id):
    if user_id == "":
        data = {
            "message": "사용자ID가 입력되지 않았습니다."
        }
        return data
    else:
        query = f'''SELECT bm.u_id, bm.b_id, bm.b_regist, b_name, b_aut, b_ps, b_date, b_short, b_detail, b_img,
                    ISNULL(STUFF((SELECT ',' + pi.p_name FROM BOOK_PREFERENCE bp JOIN PREFERENCE_INFO pi ON bp.p_id = pi.p_id WHERE bi.b_id = bp.b_id FOR XML PATH('')), 1, 1, ''), '') AS p_names
                    FROM BOOKMARK AS bm, BOOK_INFO AS bi
                    WHERE bm.b_id = bi.b_id AND u_id = %s
                 '''
        try:
            cursor = conn.cursor(as_dict=True)
            cursor.execute(query, (user_id,))
            rows = cursor.fetchall()
            user_bookmarks = []

            if rows:  # 사용자 북마크가 존재하면?
                for row in rows:
                    user_bookmark = {
                        "b_id": row['b_id'],
                        "b_regist": row['b_regist'],
                        "u_id": row['u_id'].encode('ISO-8859-1').decode('cp949'),
                        "b_name": row['b_name'].encode('ISO-8859-1').decode('cp949'),
                        "b_aut": row['b_aut'].encode('ISO-8859-1').decode('cp949'),
                        "b_ps": row['b_ps'].encode('ISO-8859-1').decode('cp949'),
                        "b_date": row['b_date'],
                        "b_short": row['b_short'].encode('ISO-8859-1').decode('cp949'),
                        "b_detail": row['b_detail'].encode('ISO-8859-1').decode('cp949'),
                        "b_img": row['b_img'].encode('ISO-8859-1').decode('cp949'),
                        "p_names": row['p_names']
                    }
                    user_bookmarks.append(user_bookmark)
            return user_bookmarks
        except Exception as e:
            print(f"MSSQL 쿼리 실행 중 오류 발생 {str(e)}")
            return None








###################
'''
def RecommendBooksWithPreferences(conn, user_id):
    try:
        query = """
        SELECT bi.b_id, bi.b_name, bi.b_aut, bi.b_ps, bi.b_date, bi.b_short, bi.b_detail, bi.b_img, pi.p_name as preference_name
        FROM USER_PREFERENCE up
        INNER JOIN BOOK_PREFERENCE bp ON up.p_id = bp.p_id
        INNER JOIN BOOK_INFO bi ON bp.b_id = bi.b_id
        LEFT JOIN PREFERENCE_INFO pi ON bp.p_id = pi.p_id
        WHERE up.u_id = %s
        """
        cursor = conn.cursor(as_dict=True)
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()

        if rows:  # 사용자의 취향에 맞는 도서가 있다면
            recommended_books = []
            for row in rows:
                book = {
                    "book_id": row['b_id'],
                    "book_name": row['b_name'],
                    "book_author": row['b_aut'],
                    "book_description": row['b_ps'],
                    "book_date": row['b_date'],
                    "book_short": row['b_short'],
                    "book_detail": row['b_detail'],
                    "book_image": row['b_img'],
                    "preference_name": row['preference_name']
                }
                recommended_books.append(book)
            return recommended_books
        else:  # 추천 도서가 없다면 랜덤하게 다른 책들을 보여줌
            query_all_books = """
            SELECT bi.b_id, bi.b_name, bi.b_aut, bi.b_ps, bi.b_date, bi.b_short, bi.b_detail, bi.b_img, pi.p_name as preference_name
            FROM BOOK_INFO bi
            LEFT JOIN BOOK_PREFERENCE bp ON bi.b_id = bp.b_id
            LEFT JOIN PREFERENCE_INFO pi ON bp.p_id = pi.p_id
            """
            cursor.execute(query_all_books)
            all_rows = cursor.fetchall()

            if all_rows:
                random_books = random.sample(all_rows, min(5, len(all_rows)))  # 랜덤하게 5개 이하의 책 선택
                recommended_books = []
                for row in random_books:
                    book = {
                        "book_id": row['b_id'],
                        "book_name": row['b_name'],
                        "book_author": row['b_aut'],
                        "book_description": row['b_ps'],
                        "book_date": row['b_date'],
                        "book_short": row['b_short'],
                        "book_detail": row['b_detail'],
                        "book_image": row['b_img'],
                        "preference_name": row['preference_name']
                    }
                    recommended_books.append(book)
                return recommended_books
            else:
                return None
    except Exception as e:
        print(f"Error recommending books with preferences: {str(e)}")
        return None

def AddBookToUserBookmark(conn, user_id, book_id):
    try:
        # 해당 사용자의 책 즐겨찾기에 추가된 도서인지 확인
        query_check_bookmark = "SELECT COUNT(*) FROM BOOKMARK WHERE u_id = %s AND b_id = %s"
        cursor = conn.cursor()
        cursor.execute(query_check_bookmark, (user_id, book_id))
        bookmark_exists = cursor.fetchone()[0]

        if bookmark_exists > 0:
            return True  # 이미 즐겨찾기에 추가된 도서

        # 사용자의 책 즐겨찾기에 도서 추가
        query_add_to_bookmark = "INSERT INTO BOOKMARK (u_id, b_id, b_regist) VALUES (%s, %s, GETDATE())"
        cursor.execute(query_add_to_bookmark, (user_id, book_id))
        conn.commit()

        # 해당 책의 취향 정보 가져오기
        query_book_pref = "SELECT p_id FROM BOOK_PREFERENCE WHERE b_id = %s"
        cursor.execute(query_book_pref, (book_id,))
        book_preferences = cursor.fetchall()

        if book_preferences:
            # 사용자의 취향 정보에 추가할 취향 정보 찾기
            user_preferences = []
            for pref in book_preferences:
                query_user_pref = "SELECT p_id FROM USER_PREFERENCE WHERE u_id = %s AND p_id = %s"
                cursor.execute(query_user_pref, (user_id, pref[0]))
                user_pref_exists = cursor.fetchone()
                if not user_pref_exists:
                    user_preferences.append((user_id, pref[0]))

            # 사용자의 취향 정보에 추가하기
            if user_preferences:
                query_insert_user_pref = "INSERT INTO USER_PREFERENCE (u_id, p_id) VALUES (%s, %s)"
                cursor.executemany(query_insert_user_pref, user_preferences)
                conn.commit()
                return True  # 즐겨찾기 및 취향 정보 추가 성공
            else:
                return True  # 즐겨찾기는 추가되었으나 사용자의 취향 정보에 추가할 새로운 정보 없음
        else:
            return True  # 즐겨찾기는 추가되었으나 해당 책의 취향 정보가 없음

    except Exception as e:
        print(f"Error adding book to user bookmark and preferences: {str(e)}")
        conn.rollback()
        return False  # 즐겨찾기 및 취향 정보 추가 실패
'''