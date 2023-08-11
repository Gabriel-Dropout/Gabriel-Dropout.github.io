---
title: std::string_view 사용 관련 삽질(서론 주의)
date: 2023-08-11 20:01:00 +0900
tags: [C++, STL, 삽질]

---

## 개요

최근 raylib-C++으로 게임을 개발하면서 개발 프로세스를 정립하기 위해 이리저리 시도하고 있다. 유명 게임 엔진을 사용할 때는 나름대로 정해진 프로세스를 따라가기만 하면 됐는데, 비교적 로우 레벨에서 접근하려니 요령이 많이 필요하다.

스프라이트 아틀라스에서 원하는 스프라이트 영역을 지정하기 위해 `std::map<std::string, AtlasSprite>`를 사용하기로 했다. 스프라이트 정보를 png 청크에 심어놓은 뒤 이를 런타임에 불러오려는 것이다.

예전 같았으면 상상도 못 할 발상이다. 헤더파일에 써 놓으면 되는 걸 굳이 런타임에 불러와 map에 넣는다니, 이 자바스러운 발상에 조상님이 노여워하시는 것 같다! C++나라에 살고 있었다면 최소 징역 3년 정도는 받지 않을까.

그럼에도 불구하고 이런 선택에는 다음과 같은 이유가 있다.

- 추가적인 헤더파일을 만들지 않고 이미지에 모든 데이터를 저장할 수 있다.
- 문자열을 통해 에셋에 접근할 수 있다.
- 스프라이트 색인 함수를 오버로드해서 다양한 형태로 에셋 참조가 가능하다.
- **충분히 빠르다(!)**

그동안 마이크로 최적화에 대해 과도한 집착이 있었다는 사실을 인정한다. 이것은 g++컴파일러님에 대한 불신으로 간주되어 엄하게 다스려야 할 것이다. 아님 말고. 아무튼 map을 쓰든 선형탐색을 쓰든 enum을 쓰든 현대 문명에 보급된 기기에서는 쌩쌩 돌아간다는 게 핵심이다. 허구헌 날 문자열끼리 비교해대는 자바스크립터들을 비난하고 살다가 결국 enum 광신도가 되어버린 나 자신을 마주하자 문득 회의감이 들었던 것이다.

---

## 그래서 하고싶은 말이 뭐죠

서론이 너무 길었다. 본론은 저거랑 상관 없는 내용이다. 처음에 맵의 키 타입을 `std::string_view`로 설정했다가 낭패를 본 건데, **string_view는 문자열 데이터를 참조할 뿐 소유하지 않는다.** 원본 객체가 사라지면 C에서 겪었던 포인터 지옥이 다시 열리는 것. 이렇게 되면 **RAII**랑 **스마트 포인터**로 겨우 봉인했던 널포인터 에러 마왕이 다시 강림하고 만다!

문제 상황은 다음과 같다.

```C++
void initAtlas(const std::string& filename) {
    atlas = raylib::Texture(filename);

	// Read custom PNG chunk: rTPb
    int spriteCount = 0;
    AtlasSprite *spriteList = NULL;

    // NOTE: chunk.data contains a standard .rtpb binary file, we can process it
    rpng_chunk chunk = rpng_chunk_read(filename.c_str(), "rTPb");
    if(chunk.data == NULL) {
        std::cout << "Error loading atlas file" << std::endl;
        exit(1);
    }

    // Load sprite data from .rtpb file data
    spriteList = LoadAtlasSpriteData(chunk.data, chunk.length, &spriteCount);
    if(spriteList == NULL) {
        std::cout << "Error loading atlas file" << std::endl;
        exit(1);
    }

    // iterate spriteList to make a map
    for(int i = 0; i < spriteCount; i++) {
        auto tmp = spriteList[i];
        spriteMap.insert(std::make_pair(std::string_view( spriteList[i].nameId ), tmp));  // HERE!
    }
    // Free chunk data
    RPNG_FREE(chunk.data);
    RPNG_FREE(spriteList);
    
    std::cout << "Sprite Count: " << spriteCount << std::endl;
}
```

`spriteMap.insert()`부분을 잘 보자. 만약 spriteMap의 키 타입이 `std::string_view`라면 `RPNG_FREE(spriteList)`에서 키 정보를 잃어버리고 만다. 연관 컨테이너 내의 객체를 컨테이너가 소유하지 못하는 것이다.

결론은, 자원 좀 아껴보겠다고 괜히 string_view 쓰지 말고 그냥 맘 편하게 string 쓰자는 이야기다.

---

## 여담

아니, 몇 개월 만에 와서 쓴다는 게 이런 뻘글이냐고요? 사실 읽는 사람도 없겠지만 뭐. 반나절 삽질하다 정신이 조금 이상해진 것뿐이다.

포인터는 좋다. 그런데 malloc은 싫다. 언젠가 러스트 쪽에 기웃거리게 될 것은 정해진 미래임을 되새기며 다음엔 정상적인 글로 돌아오겠습니다.