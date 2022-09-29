---
title: wargame dropper 풀이
date: 2022-09-29 15:00:00 +0900
tags: [파이썬, 리버싱]

---

## 개요

리버싱 문제는 포스트를 작성하기 참 난감하다.

요구되는 배경 지식이 꽤 깊고, 문제 코드가 복잡하기 때문이다.

다른 분야에 비해 문제 풀이 과정을 툴에 의존하는 부분도 있어서, 글 구성 또한 쉽지 않다.

그러나 이번에 아주 쉽고 재미있는(?) 문제를 발견해 간단히 소개한다.

---

## 문제 상황

__dropper.exe__ 가 주어진다. 이를 분석하라.

_Hint: 이 프로그램은 파이썬 스크립트로부터 만들어졌습니다._

---

## 풀이 접근

불친절함의 극치. 하지만 결정적인 힌트가 접근 방향을 제시해 준다.

정말로 파이썬 스크립트를 사용했는지 확인하려면 확장자를 zip으로 바꾸고 열어 보시라.

<img src="https://user-images.githubusercontent.com/88845385/192952330-0fb4035c-d941-48d2-a09c-2a55f12c10b9.png" alt="1" style="zoom:67%;" />

짜잔. 파이썬은 인터프리터 언어이기 때문에, 네이티브로 컴파일되지 않는다.

파이썬 코드에 대응하는 바이트 코드와 이를 실행하는 프로그램이 잘 포장되어 있을 뿐이다.

따라서 원본 파일을 얻으려면 3가지 과정이 필요하다.

1. 원본 파이썬의 버전, 실행 파일 변환 패키지 종류 추측
2. 바이트 코드 추출
3. 디컴파일

1번은 그냥 때려 맞히면 되고(더 우아한 방법이 있는지는 모르겠으나, 별 차이는 없다), 2번과 3번도 이미 스크립트가 있다.

해 보자.

---

## 진짜 시작

왠지 __pyinstaller__ , 파이썬은 __3.x__ 를 사용했을 것 같았다.



### PyInstaller Extractor 사용

https://github.com/extremecoders-re/pyinstxtractor

원본 파이썬 코드와 동일한 버전의 파이썬에서 다음 코드를 실행한다.

```bash
$ python pyinstxtractor.py ../dropper.exe
```

```
[*] Processing ../dropper.exe
[*] Error : Unsupported pyinstaller version or not a pyinstaller archive
```

아무래도 pyinstaller는 아닌 것 같다.

### unpy2exe 사용

https://github.com/matiasb/unpy2exe

pyinstaller가 아니므로 py2exe를 사용했을 가능성이 높다. 위 스크립트를 사용해 보자.

먼저 종속성 패키지를 설치하고, 스크립트를 실행한다.

```bash
$ sudo pip install -r requirements.txt
$ python3 unpy2exe ../dropper.exe
There was an error: bad marshal data (unknown type code)
```

`python 3.x`는 아닌 모양이다. `python 2.7`에서 다시 해 보자.

```bash
$ sudo pip2 install -r requirements.txt
$ python2.7 unpy2exe ../dropper.exe
```

`dropper.py.pyc`가 생겼다. 우리가 찾던 바이트 코드다.

### 디컴파일

스크립트 대신 더 간편한 소프트웨어를 발견했다. 어지간한 파이썬 버전은 다 지원된다.

https://sourceforge.net/projects/easypythondecompiler/

변환된 `.py` 파일을 얻었다.

### (번외) python-exe-unpacker 사용

https://github.com/WithSecureLabs/python-exe-unpacker

사실 압축 해제와 디컴파일을 모두 할 수 있는 만능 도구도 있다.

종속성 패키지를 설치하자.

```
sudo pip2 install -r requirements.txt
```

C 컴파일을 해야 하므로 속편하게 wsl에서 진행했다.

```bash
fatal error: Python.h: No such file or directory
```

그럼에도 오류가 발생하는데, 아래 명령어로 해결할 수 있다고.

```bash
$ sudo apt-get install python-dev
```

이제 추출 및 디컴파일을 해 보자.

```bash
$ python2.7 python_exe_unpack.py -i ../dropper.exe
```

`unpacked/dropper.exe/` 폴더에 바이트 코드와 원본 스크립트가 나란히 있는 것을 볼 수 있다.

---

## 코드 해석

```python
a = 'TVqQAAMAAAAEAAAA//8AALgAAAAAAAAAQAAAAAAAAAAAAAA...'
import subprocess
import os
a = a.decode('base64')
b = a[:5152]
b += '0f0212131a1c155b0b0b113e0158051912065233081b5e0304041e1100'.decode('hex')
b += a[5180:]
f = open('mal.exe', 'wb')
f.write(b)
f.close()
subprocess.check_output(['mal.exe', 'install'])
f = open('killer.bat', 'w')
f.write('@echo off\n')
f.write('del mal.exe\n')
f.write('del killer.bat\n')
f.close()
os.system('killer.bat')
```

자칭 멀웨어 프로그램을 만들고 바로 지우는데, __진짜 랜섬웨어같은 거 아닐까__ 잠깐 고민했지만 설마 그러진 않겠지.

중간에 `mal.exe`의 결과값을 받아오지만 출력하지는 않는 것으로 보인다. 해당 값을 출력하는 코드를 넣고 직접 실행해 보자.

```bash
$ python2.7 dropper.py
flag{***}
```

이렇게 플래그를 얻었다.

---

## 여담

`mal.exe`가 뭔지 궁금해 어셈블리 분석을 해 봤는데, __내부에 저장된 바이트열을 파라미터와 xor해서 반환__ 하는 프로그램이었다. xor 암호화같은 느낌. 괜히 쫄았군.