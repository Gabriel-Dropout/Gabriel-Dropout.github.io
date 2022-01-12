---
title: Pytube 아류 라이브러리 youpi 등록하기
date: 2022-01-12 02:52:00 +0900
tags: [프로그래밍, 파이썬, youpi]
---

## 개요

지난 여러 포스트는 전부 이 게시글을 위한 떡밥이었다. 깜짝 놀랐지!

수많은 시행착오와 업그레이드를 통해 외부 종속성이 없는 유튜브 동영상 다운로드 모듈인 `youpi`를 만들었다.

사실 `youpy`라고 짓는 게 더 자연스럽지만 _(youtube + python)_ 그건 이미 있던 관계로(...)

`youpi`로 명명했다. 뭐 아무래도 상관없다! 어차피 나만 쓸 거니까!

---

## 본론

각설하고 본론으로 넘어가자.

_ver.0.1.3_ 기준으로 기본 사용법을 설명한다.

### 설치

```bash
pip install youpi
```

### 임포트

```python
from youpi import YouTube
```

### 사용

```python
# YouTube 객체 생성
yt = YouTube('video id')

# 스트림 정보 반환
streams = yt.streams

s = streams.get_by_itag(299)  # itag가 299인 Stream 반환

s = streams.get(0)  # 첫 번째 Stream 반환

s = streams.best_video()  # Adaptive Video 중 최고 화질 Stream 반환

s = streams.best_audio()  # Adaptive Audio 중 최고 음질 Stream 반환

s = streams.best_both()  # Progressive 중 최고 화질 Stream 반환

# 여러 조건으로 필터링한 stream list 반환
# 아무 stream도 남지 않을 수 있다
# 하나의 stream만 남아도 StreamList로 반환된다
streams.filter(res=1080, datatype='video', extension='mp4', fps=60, bitrate=134178)

s.download('filename')  # 확장자는 자동으로 부여된다

```

`StreamList`와 `Stream`은 다른 객체임에 주의하자.

`StreamList`는 말 그대로 `Stream`의 목록을 담고 있고, 이들 중 필요한 스트림을 필터링하는 여러 함수를 제공하는 클래스다.

__아직 완성되지 않은 모듈__ 이므로 부족한 점이 많다.

- 동영상 제목, 업로더, 업로드 날짜 등의 정보를 반환하는 기능은 구현되지 않았다.
- Adaptive Video와 Audio를 합쳐 하나의 영상으로 만드는 기능은 구현되지 않았다.
- 다운로드 폴더를 별도로 지정하는 기능은 구현되지 않았다.

특별히 신경 써서 구현한 기능도 있다.

- 10MB 단위의 청크로 나누어 요청하는 기능을 ~~강요~~ 제공한다.
- 한 번 요청했던 링크는 __Cache__ 에 저장하고 유효 기간을 검사해 사용 가능하면 즉시 불러온다.
- 구조를 단순하게 만들기 위해 노력했다. 하지만 아무도 알아주지 않는다.
- 외부 종속성을 없애기 위해 `requests`등의 써드파티 라이브러리를 사용하지 않았다.

---

## pyPI에 등록

pip install을 지원하려면 저기에 등록해야된다. github이랑 쉽게 연동하는 방법같은 거 없나...?

pyPI는 상당히 까다로운 폴더 조건을 요구한다.

```bash
.
├─youpi //패키지 이름과 동일
│  │  __init__.py
│  │  cache.py
│  │  stream.py
│  │  streamlist.py
│  └─ youtube.py
│  .gitignore
│  LICENSE
│  MENIFEST.in
│  README.md
│  setup.cfg
└─ setup.py
```

github에도 계속 커밋해야 되니까 `LICENSE`랑 `.gitignore`도 있다.

하나하나 내용을 채워 보자.

---

### setup.py

```python
import setuptools

setuptools.setup(
    name='패키지 이름',
    version='버전',
    author='이름',
    author_email='이메일',
    description='짧은 설명',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url='깃허브 주소',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3',
)
```

다들 조금씩 다르게 쓰는데 대충 이렇게 했다.

`packages`가 제일 중요한데, 저렇게 `setuptools`를 써서 자동으로 빌드할 패키지를 탐색하게 했다.

---

### setup.cfg

```bash
[metadata]
description-file = README.md
license_file = LICENSE
```

뭔지 모르겠다. setup.py를 보조하는 역할인 듯? 메타데이터 두 개를 넣어 줬다.

---

### MENIFEST.in

```bash
include LICENSE

include README.md
```

패키지 내용은 아니지만 따로 포함시키고 싶은 파일을 적으면 된다.

---

### \_\_init.py\_\_

패키지, 즉 `import youpi`를 입력했을 때 실행되는 녀석이다. 다른 모듈을 불러오는 부분이 들어간다.

```python
from .youtube import YouTube

__all__ = ['YouTube']
```

나는 `YouTube` 클래스 하나만 불러오면 되기 때문에 저렇게 했다.

참고로 `__all__`은 `from youpi import *`를 입력했을 때 불러올 친구들의 목록을 `str`형태로 담고 있는 __list container__ 이다.

### .gitignore

```python
# 개발 중 테스트 목적으로 사용되는 폴더
/devtest

# api 캐시
Cache_*.pkl

# 파이썬 캐시
*.pyc
__pycache__/

# pyPI 빌드 파일
youpi.egg-info/
build/
dist/

# VS Code 관련 파일
.vscode

#다운로드한 동영상 파일
*.mp4
*.webm
```

pyPI 패키지를 빌드하면 이것저것 많이 나오기 때문에 신경 써서 작성했다.

---

## 빌드 및 업로드

### 빌드 관련 라이브러리 설치

```bash
pip install setuptools wheel
```

### 빌드

```bash
python setup.py bdist_wheel
```

또는

```bash
python setup.py sdist
```



### 업로드 관련 라이브러리 설치

```bash
pip install twine
```

### 업로드

```bash
python -m twine upload dist/*
```

자세한 내용은 아래 링크를 참조하자.

[여기!](https://suhwan.dev/2018/10/30/deep-dive-into-pip-2/)

---

## 여담

갑자기 _pytube_ 구조가 궁금해져 가볍게 시작한 프로젝트인데 어느새 커져 버렸다.
