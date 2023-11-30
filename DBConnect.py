import pymssql
import json
import random

#     print(row[0], row[1].encode('ISO-8859-1').decode('euc-kr'))
#     print(row[0], row[1].encode('ISO-8859-1').decode('cp949'))

## fetchall과 fetchone의 차이
## fetchall : 모든 행을 한번에 가져옴
## fecthone : 행을 하나씩 가져옴

## MSSQL 접속
def DBConnect():
    server = '172.16.104.69:1433'   # 김진영 부천대 Local
    #server = '192.168.45.216:1433' # 김진영 HOME Local
    #server = '222.108.212.104:1433'
    server = '172.16.114.196:1433' # 이세호 부천대 Local
    database = 'dnb'
    username = 'sa'
    password = '1234'
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
		        ISNULL(STUFF((SELECT ',' + pi.p_name FROM BOOK_PREFERENCE bp JOIN PREFERENCE_INFO pi ON bp.p_id = pi.p_id WHERE bi.b_id = bp.b_id FOR XML PATH('')), 1, 2, ''), '') AS p_names
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

## 취향명으로 취향목록 추출 ##
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
        for preference_id in preference_ids.split(','):
            query = f"INSERT INTO USER_PREFERENCE (u_id, p_id) VALUES (%s, %s)"
            cursor = conn.cursor()
            cursor.execute(query, (user_id, preference_id))
        conn.commit()
        data = {
                "message": "취향 입력 성공"
        }
        return data
    except Exception as e:
        print(f"Error adding user preferences: {str(e)}")
        conn.rollback()  # 롤백하여 이전 상태로 복구
        data = {
            "message": "취향 입력 중 오류 발생"
        }
        return data


## 책의 취향정보를 가져와서, 사용자 취향 정보에 추가
def AddBookToUserPreferences(conn, user_id, book_id):
    try:
        # 해당 책의 취향 정보 가져오기
        query_book_pref = "SELECT p_id FROM BOOK_PREFERENCE WHERE b_id = %s"
        cursor = conn.cursor()
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
                return True  # 취향 정보 추가 성공
            else:
                return False  # 사용자의 취향 정보에 추가할 새로운 정보 없음
        else:
            return False  # 해당 책의 취향 정보가 없음

    except Exception as e:
        print(f"Error adding book preferences to user: {str(e)}")
        conn.rollback()
        return False  # 취향 정보 추가 실패










"""
def AddtoBookmark(conn, user_id, book_id):
    try:
        # 현재 날짜와 시간 정보 가져오기
        current_time = datetime.datetime.now()

        # 즐겨찾기 테이블에 사용자와 책 정보 추가
        query = "INSERT INTO BOOKMARK (u_id, b_id, b_regist) VALUES (%s, %s, %s)"
        cursor = conn.cursor()
        cursor.execute(query, (user_id, book_id, current_time))
        conn.commit()

        return True  # 등록 성공을 나타내는 값 반환
    except Exception as e:
        print(f"Error adding to bookmark: {str(e)}")
        conn.rollback()  # 롤백하여 이전 상태로 복구
        return False  # 등록 실패를 나타내는 값 반환
"""
def GetUserBookmarksWithPreferences(conn, user_id):
    try:
        query = """
        SELECT bi.b_id, bi.b_name, bi.b_aut, bi.b_ps, bi.b_date, bi.b_short, bi.b_detail, bi.b_img, pi.p_name as preference_name
        FROM BOOKMARK bm
        INNER JOIN BOOK_INFO bi ON bm.b_id = bi.b_id
        LEFT JOIN BOOK_PREFERENCE bp ON bi.b_id = bp.b_id
        LEFT JOIN PREFERENCE_INFO pi ON bp.p_id = pi.p_id
        WHERE bm.u_id = %s
        """
        cursor = conn.cursor(as_dict=True)
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()

        if rows:  # 즐겨찾기 정보가 있다면
            bookmarks = []
            for row in rows:
                bookmark = {
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
                bookmarks.append(bookmark)
            json_data = json.dumps(bookmarks)  # 책 정보들을 리스트로 묶어 JSON 형식으로 변환
            print(json_data)  # 책 정보 JSON 문자열 출력
        else:  # 즐겨찾기 정보가 없다면
            data = {
                "message": "즐겨찾기 정보가 없습니다."
            }
            json_data = json.dumps(data)
            print(json_data)
        return json_data
    except Exception as e:
        print(f"Error getting user bookmarks with preferences: {str(e)}")
        return None


def RemoveFromBookmark(conn, user_id, book_id):
    try:
        query = "DELETE FROM BOOKMARK WHERE u_id = %s AND b_id = %s"
        cursor = conn.cursor()
        cursor.execute(query, (user_id, book_id))
        conn.commit()
        return True  # 삭제 성공을 나타내는 값 반환
    except Exception as e:
        print(f"Error removing from bookmark: {str(e)}")
        conn.rollback()  # 롤백하여 이전 상태로 복구
        return False  # 삭제 실패를 나타내는 값 반환

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
    
def execute_query1(conn):
    query = "SELECT * FROM table1"
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Exception as e:
        print(f"Error executing SQL query 1: {str(e)}")
        return None


## USER_INFO 가져오기
def SelectUserInfo(conn, u_id):
    cursor.execute('SELECT * FROM USER_INFO')
    row = cursor.fetchone()
    while row:
        u_id = row['u_id']
        u_pwd = row['u_pwd'].encode('ISO-8859-1').decode('cp949')
        u_name = row['u_name'].encode('ISO-8859-1').decode('cp949')
        u_nicname = row['u_nicname'].encode('ISO-8859-1').decode('cp949')
        u_division = row['u_division']
        u_gender = row['u_gender']
        u_age = row['u_age']
        u_time = row['u_time']
        print(u_id, u_pwd, u_name, u_nicname, u_division, u_gender, u_age, u_time)
        row = cursor.fetchone()



## SELECT
def DBSelect(sql):
    global conn, cursor
    cursor.execute(sql)
    row = cursor.fetchone()
    while row:
        print(row['u_id'], row['u_name'].encode('ISO-8859-1').decode('cp949'))
        row = cursor.fetchone()

"""
def GetUserLoginCheck(conn, u_id, u_pwd):
    query = 'SELECT COUNT(*) AS CNT FROM USER_INFO WHERE u_id = %s AND u_pwd = %s'
    try:
        # 딕셔너리로 결과 반환하는 커서 생성
        cursor = conn.cursor(as_dict=True)
        cursor.execute(query, (u_id, u_pwd))
        row = cursor.fetchone()
        count_value = row['CNT']
        if count_value == 1:
            data = {
                "login_yn":"y",
                "message":"로그인 성공"
            }
            print(data)
        else:
            data = {
                "login_yn":"n",
                "message":"실패 : 아이디가 존재하지 않거나 비밀번호가 일치하지 않습니다."
            }
        return data
    except Exception as e:
        print(f"MSSQL 쿼리 실행 중 오류 발생 {str(e)}")
        return None
#print(UserLoginCheck('', '1', '비밀번호'))
#UserLoginCheck('', '1', ' 비밀번호')
#SelectUserInfo('','','','','','','','')
#DBConnect(server, username, password, database)
#DBSelect(sql)
#DBClose()
"""
"""
#############################################################################
# INSERT
data = 'hello World !!'
query = "INSERT INTO POST (CONTENTS) VALUES ('" + str(data) + "')"  # 문자열은 무조건 홑따옴표
cursor.execute(query)
conn.commit()

#############################################################################
# UPDATE
data = '헬로우 월드 !!'
query = "UPDATE POST set CONTENTS = '" + str(data) + "'  where POST_NO = 11"
cursor.execute(query)
conn.commit()

#############################################################################
# DELETE
data = '헬로우 월드 !!'
query = "DELETE FROM POST WHERE CONTENTS = '" + str(data) + "'" 
cursor.execute(query)
conn.commit()
"""