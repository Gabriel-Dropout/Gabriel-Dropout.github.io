---
title: Google Drive API 제대로 사용하기
date: 2022-10-28 21:40:00 +0900
tags: [파이썬, 웹]
---

## 연구배경

Jekyll 블로그는 관리하기가 상당히 까다롭다. 특히 이미지 호스팅.

**Github Issue** 탭을 이용해 블로그에 필요한 이미지를 호스팅하고는 있으나, 편법에는 아무래도 이런저런 위험부담이 있기 마련이다.

그마저도 네이버 블로그나 티스토리같은 플랫폼에 비하면 상당히 불편하기도 하고.

그래서 **velog**로 블로그 이전을 계획하고 있었는데, 준비를 전부 마친 후에야 큰 문제점을 발견했다.

주인장 관심 분야가 마이너하기 짝이 없다 보니 블로그에서 웹어셈블리를 돌릴 일이 있는 것.

타 플랫폼 입장에서 생각해 보면 이건 웹에 악성코드를 심는 것과 같지 않은가. XSS도 아니고... 당연히 제대로 실행될 리가 없었다.

뭐 그래서 이런 저런 일을 겪고 다시 Github Blog로 돌아오긴 했는데...아무래도 편의성 개선을 할 필요가 있어 보였더랬다.

그 대장정은 우선 **이미지를 구글 드라이브에 올리고 액세스 링크를 받아오는 애플리케이션**을 만드는 것으로 시작되었다.

---

## 서론

아무도 관심 없는 이야기는 이쯤 하고, 저런 앱을 만들려면 우선 Google API에 대해 이해해야 하지 않겠는가.

한국어로 정리한 문서가 없고 다들 간단한 업로드/다운로드 예제 코드만 올려놓길래 직접 정리해 보려고 한다.

구글에서 다행히 파이썬 모듈을 만들어 놓았으므로 RESTful API의 HTTP 구조까지 들여다볼 필요는 없겠다.

자세한 내용은 아래 링크를 참조하자.

[개발자를 위한 Google Drive API](https://developers.google.com/drive/api/quickstart/python)

[파이썬 API 모듈](https://github.com/googleapis/google-api-python-client/blob/main/docs/README.md)

본 글에는 문서 또는 API 구조에 대한 잘못된 해석이 있을 수 있다.

---

## 모듈 설치

```bash
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

---

## 인증 및 권한 부여

### 인증 방식

API Keys와 OAuth 2.0방식을 지원하며, 개인 데이터에 접근하기 위해서는 OAuth 2.0을 사용해야만 한다.

그러므로 프로젝트, **클라이언트**, 사용자, client ID, client secret, **token**, **scope** 등에 관한 사전지식이 전제가 된다.

### 코드

아무튼 API를 이용할 때에는 **의도한 사용자**가 **의도한 클라이언트**에서 요청하는지 확인해야 할 것이다.

클라이언트 인증 파일은 클라우드 콘솔의 `API 및 서비스 -> 사용자 인증 정보 -> OAuth 클라이언트 다운로드`를 통해 내려받을 수 있다. 이를 `credentials.json`이라고 하자.

이 파일과 함께, 필요한 경우 사용자 계정 인증 절차를 거쳐 임시 token이 발급된다.

```python
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
def ensure_cred():
    SCOPES = 'https://www.googleapis.com/auth/drive.file'
    creds = None
 
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # 유효한 토큰이 없으면 갱신 또는 생성(로그인)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # 토큰 저장
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
   
    return creds
```

`SCOPE`는 접근 수준을 설정하는데, `drive.file`은 해당 클라이언트에서 생성한 파일만 확인, 수정, 삭제가 가능한 설정이다.

원래는 **절대로** 네이티브 앱에 `client secret`을 저장하면 안 되는데, 구글에서는 이상하게도 위와 같은 방식을 예제로 사용하고, Documentation에서도 이를 비밀 정보로 취급하지 않는다고 직접 언급하기까지 한다. 일단 앱을 공개 배포할 생각은 없으니 자세한 건 넘어가자.

---

## API 진짜로 사용하기

위에서 발급한 토큰(원문에선 credential; client credentials과의 혼동을 고려해 이하 토큰으로 서술)으로 drive의 v3버전 클라이언트를 생성하자.

```python
service = build('drive', 'v3', credentials=creds)
```

앞으로 다룰 모든 요청은 `service.target().method(q='query', fields='partial response', ...)`과 같은 형태로 구조화되어 있다.

### 파일 조작

파일 조회, 업로드, 수정과 같은 기능은 `service.files()`객체에서 제공한다.

#### 전체 파일 조회

`service.files().list()`함

```python
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def search_file(creds):
    try:
        service = build('drive', 'v3', credentials=creds)
        files = []
        page_token = None
        while True:
            response = service.files().list().execute()
            for file in response.get('files', []):
                print(F'Found file: {file.get("name")}, {file.get("id")}')
            files.extend(response.get('files', []))
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break
 
    except HttpError as error:
        print(F'An error occurred: {error}')
        files = None
    return files
```

#### 파일 다운로드

`service.files().get_media()`

```python
import io
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

def download_file(real_file_id, creds):
    try:
        service = build('drive', 'v3', credentials=creds)
 
        file_id = real_file_id
 
        request = service.files().get_media(fileId=file_id)
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(F'Download {int(status.progress() * 100)}.')
 
    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None
 
    return file.getvalue()
```

#### 파일 업로드

`service.files().create()`

```python
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
 
def upload_file(creds):
    try:
        service = build('drive', 'v3', credentials=creds)
 
        file_metadata = {'name': 'cat.jpeg', "parents": ["FolderID"]}
        media = MediaFileUpload('cat.jpeg')
       
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print(F'File ID: {file.get("id")}')
 
    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None
 
    return file.get('id')
```

#### 파일 권한 확인

`service.permissions().list()`

```python
service.permissions().list(fileId='fileId').execute()
```

#### 파일 권한 설정(임의의 사용자-뷰어)

`service.permissions().create()`

```python
user_permission = {
    'type': 'anyone',
    'role': 'reader',
}
service.permissions().create(fileId='fileId', body=user_permission).execute()
```

---

## 여담

프로그램을 만들기 앞서 사용할 API에 대해 알아봤다.

물론 전체 기능에 비하면 극히 일부분에 불과하지만, 공식 문서를 참조하면 나머지 기능도 쉽게 알 수 있을 것이다.

어째선지 이 글 포스팅하는 데 하루 종일 걸렸다.

남이 다 만들어 놓은 걸 사용하는 것도 이렇게 오래 걸리다니, 세상엔 쉬운 게 없나 보다.