---
title: gtest Makefile v1.0
date: 2023-05-07 22:52:00 +0900
tags: [삽질, C++, Makefile]

---

## 개요

지난번에 gtest 단위 테스트 환경을 구축했었다. 환경이라 해 봐야 그냥 리포지토리 다운받아서 빌드한 것뿐이다. 이번엔 이를 실제 프로젝트에 적용할 때 사용할 수 있는 Makefile을 작성했다.

---

## 본론

현재 폴더 구조는 다음과 같다.

```

├─gtest
│  ├─gtest
│  │  └─헤더파일들
│  ├─lib
│  │  └─*.a
│  └─lib_shared
│     └─*.dll.a, *.dll
└─include
   └─my_spline
      ├─spline.hpp
      ├─spline_test.cpp
      └─Makefile
```

`spline.hpp`를 테스트하기 위해 `spline_test.cpp`를 만들고, 이것을 컴파일/링크하기 위해 `Makefile`을 만들었다. cpp파일은 아래처럼 쓰여 있다.

```c++
#include "spline.hpp"
#include "gtest/gtest.h"
namespace {

TEST(FactorialTest, TRUE) { EXPECT_EQ(1, 1); }
TEST(FactorialTest, FALSE) { EXPECT_EQ(1, 2); }

}  // namespace
```

사실 그냥 더미 파일이다(...). 아무튼 이 cpp 파일을 헤더 경로와 함께 컴파일해서 목적 파일을 생성하고, 이 목적 파일을 gtest 라이브러리와 링크하면 된다. Makefile은 다음과 같이 작성했다.

```makefile
CC = g++
CFLAGS = -O2 -std=c++17 -I . -I ../../gtest
LDFLAGS= -L ../../gtest/lib
LDLIBS = -lgtest -lgtest_main
OBJS = spline_test.o
TARGET = spline_test.exe

.PHONY: all test execute clean

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) -o $@ $(OBJS) $(LDFLAGS) $(LDLIBS)

%.o: %.cpp
	$(CC) -c $< $(CFLAGS)

test: $(TARGET) execute clean

execute:
	-$(TARGET)

clean:
	del /q $(OBJS) $(TARGET)
```

하나씩 살펴보자.

```makefile
CC = g++
CFLAGS = -O2 -std=c++17 -I . -I ../../gtest
LDFLAGS= -L ../../gtest/lib
LDLIBS = -lgtest -lgtest_main
OBJS = spline_test.o
TARGET = spline_test.exe
```

차례대로 컴파일러, 컴파일 옵션, 링킹 옵션, 링크할 라이브러리, 만들어지는 목적파일 목록, 실행파일 이름에 해당한다. 헤더파일 경로를 나타내는 `-I` 옵션은 컴파일 시 삽입되고, 라이브러리 경로를 나타내는 `-L` 옵션은 링킹 시 삽입된다.

```makefile
.PHONY: all test execute clean
```

실제 파일명이 아닌 레시피들은 이 목록에 추가한다. 해당 타겟과 같은 이름의 파일이 존재할 때 발생하는 오류를 막아 준다.

```makefile
$(TARGET): $(OBJS)
	$(CC) -o $@ $(OBJS) $(LDFLAGS) $(LDLIBS)
```

최종 실행 파일은 각 목적 파일을 필요로 한다. 목적 파일이 준비될 경우 미리 작성한 라이브러리 목록과 함께 링크해서 실행 파일을 생성한다. `$@`는 타겟 이름을 의미하는 자동 변수로 여기서는 `$(TARGET)`이 된다.

```makefile
%.o: %.cpp
	$(CC) -c $< $(CFLAGS)
```

각 목적 파일은 동일한 이름의(확장자 제외) C++ 소스코드를 필요로 한다. 미리 작성한 컴파일 옵션을 이용해 컴파일한다. `$<`는 첫 번째 의존 파일을 의미하는 자동 변수로 여기서는 `%.cpp`이 된다.

```makefile
test: $(TARGET) execute clean

execute:
	-$(TARGET)

clean:
	del /q $(OBJS) $(TARGET)
```

**test**는 실행 파일을 준비하고, 이를 실행하고, 정리하는 편리한 명령이다. 원하는 작업을 의존성 목록에 순서대로 쓰는 트릭을 활용했다.

**execute**는 exe파일을 실행한다. 단위 테스트가 실패하면 비정상적인 **exit code**를 반환하는데, 원래 make 명령은 이를 에러로 간주해 스스로를 종료한다. 테스트 성공 여부에 관계없이 **clean** 명령을 수행하려면 종료 코드를 무시하도록 `-$(TARGET)`처럼 앞에 하이픈을 붙여 준다.

**clean**은 생성된 모든 파일을 삭제한다. 해당 명령어는 윈도우 의존적이다. 리눅스의 경우 `rm -rf` 등을 이용하면 되는데 여기서는 생략했다.

---

## 여담

디렉토리 구조에 큰 신경을 쓰지 않기도 했고, 여러 개의 단위 테스트 파일을 빌드할 수도 없는 등 아직 한계가 많다. 추후 필요해지면 다음 버전의 Makefile을 작성하게 될 것 같다. 이러다가 결국 Cmake로 넘어갈 것 같긴 한데...
