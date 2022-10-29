---
title: Google Drive Image Uploader 프로토타입 개발
date: 2022-10-29 18:43:00 +0900
tags: [파이썬, gui]

---

## 개요

지난번에 소개한 GoogleDrive API를 이용해 간단한 이미지 업로더를 만들었다.

GUI 프레임워크로는 tkinter를 채택했다. 프로토타입이니 제일 가볍고 개발속도가 빠른 걸 사용하는 게 좋겠지.

tkinter는 지나치게 구려서(...) 별로 사용하고 싶지는 않지만, **애초에 파이썬 GUI 앱 개발에 선택지가 별로 없다.**

---

## Features

- 이미지 파일 불러오기

tkinter의 filedialog 모듈에서 파일 탐색기를 불러올 수 있다.

- 파일 Drag & Drop 기능

기본적으로 있어야 할 것 같지만 놀랍게도 **tkinter에서는 파일 DnD를 제공하지 않는다.**

방법이 아주 없는 것은 아닌데, `tkdnd` 확장과 `TkinterDnD2` 파이썬 래퍼를 사용하면 된다.

최종적으로 exe파일로 뽑아내기까지 아주 많은 시행착오가 있었는데, 처음부터 PyQt로 만드는 게 더 빠르지 않았을까 하는 생각이 들 정도.

아무튼 위의 filedialog와 더불어 이것을 이용해 이미지 파일을 불러올 수 있다.

- 이미지 미리보기

일단 이미지를 불러오면, `PILLOW` 모듈을 이용해 리사이즈 후 화면에 띄워 준다.

- 구글 드라이브 업로드 및 url 반환

제일 핵심적인 기능이다. 이미지 파일을 구글 드라이브에 업로드하고, 자동으로 공유 설정까지 마친 뒤 이미지 자체를 반환하는 url 링크를 출력한다.

- url 클립보드 복사

url 텍스트 옆에 위치한 버튼을 눌러 자동으로 클립보드해 복사해 준다. `win10toast` 모듈을 이용해 윈도우 환경에서 토스트 메시지까지 띄운다.

---

## 코드 조각

포스트 분량을 늘리기 위해 중요한 코드를 몇 줄 적어 보자.

```python
def split_filestring(data):
    ind = 0
    cnt = 0
    files = []
    res = data
    for i,c in enumerate(data):
        if c=='{':
            if cnt==0:
                ind = i
            cnt += 1
        if c=='}':
            cnt -= 1
            if cnt==0:
                files.append(data[ind+1:i])
                res = res.replace(data[ind:i+1], '', 1)
    files.extend(res.split())
    return files
```

`tkdnd`에서 건네주는 결과값은 각 파일들을 공백으로 구분한 문자열이다. 파일 경로 자체에 공백이 있을 경우 해당 파일 경로의 양쪽에 중괄호가 붙는다. 일관성이 없군.

프로그램 기능상 단일 파일만 받아들이고 복수 파일은 reject하면 좋겠지만 `tkdnd`에 그 정도 세분화는 되어 있지 않다. 그래서 일단 위 함수로 파싱한 뒤 첫 번째 파일을 이용하도록 구현했다.



```python
placeholder = Frame(window, bg='lavender', highlightthickness=4, highlightbackground="lightblue4", relief='flat')
placeholder.pack(side='top', fill='both', expand=True, padx=30, pady=15)
placeholder.pack_propagate(False)
placeholder.drop_target_register(DND_FILES)
placeholder.dnd_bind("<<Drop>>", drop)
```

이미지 DnD 영역 겸 미리보기 이미지가 표시되는 placeholder 선언 부분. 이처럼 모든 위젯 레이아웃은 `pack()`으로 관리된다.

`pack_propagate(False)`는 내부 위젯에 의한 프레임 크기 조절을 막는 옵션이다. placeholder 크기가 멋대로 변하면 레이아웃이 망가진다.

`drop_target_register()`와 `"<<Drop>>"` 이벤트는 예상 가능하듯이 드래그 앤 드랍 업로드 기능을 구현하는 부분이다. 그다지 흥미롭지는 않다.



```python
 def copy_url(event):
    clipboard.copy(filelogurl['text'])
    toast.show_toast('URL이 클립보드에 복사되었습니다', filelogurl['text'], threaded=True, icon_path='imageHosting.ico')
```

`Label`타입 위젯인 `filelogurl`에는 반환된 이미지 url이 표시된다. 이 값을 클립보드에 복사하고 toast message를 띄워 주는 함수다.

---

## 결과

<img src="https://drive.google.com/uc?id=1Yvo1dhv_jkvxoZ92WqqJWQbfqsNm9E5c" alt="result1" style="zoom:50%;" />

*tkinter 치고는* 나름 이쁘게 나온 것 같다. 그만큼 오래 걸리긴 했지만.

기능 모두 이상 없이 작동한다.

---

## 여담

**pyinstaller**를 사용해서 exe파일로 만들긴 했는데, 세상의 모든 백신이 프로그램을 바이러스로 인식한다.

해결하려면 pyinstaller를 직접 빌드해야 한다는데, 이것도 또 여간 귀찮은 일이 아니다.

나중에 PyQt로 재개발할 때 다시 살펴보기로 하고, 지금은 그냥 윈도우 디펜더를 꺼 놓는 것으로 타협을 보자.

아니, 경고하는 것도 아니고 얄짤없이 삭제해 버리면 제 마음이 아프죠, 안 그래요?

여담의 여담으로, 위 결과 이미지는 바로 저 프로그램을 이용해 구글 드라이브에 업로드되어 있는 상태다. 자기 자신의 이미지를 업로드하다니. 안될 건 없지만.