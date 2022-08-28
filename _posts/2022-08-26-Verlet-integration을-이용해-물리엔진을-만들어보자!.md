---
title: Verlet integration을 이용해 물리엔진을 만들어보자!
date: 2022-08-26 15:47:00 +0900
tags: [C++, raylib, 프로젝트]

---

## 개요

초등학생 때부터 보존력이 작용하는 역학적 상황을 테스트하기 위해 __오일러 방법__ 을 사용해 왔다.

__오일러 방법__을 사용하면 비접촉력만이 존재하는 시스템을 쉽게 구현할 수 있었지만 접촉력, 특히 수직항력이 처리하기 까다롭다는 문제점이 있었다.

십 년 묵은 오일러 방법은 이제 버리고 다르게 접근해 보자.

---

## Verlet integration

이름은 거창해 보이지만 생각보다 별 거 없다.

우선 오일러 방법은 아래와 같이 서술된다.

![euler](https://user-images.githubusercontent.com/88845385/186844303-2a89af6c-2d17-48c6-915f-69b9fc1ce227.png)

둘을 연립해서 v_n 항을 소거하고 작은 마법을 부려 주면 아래 식을 얻는다.

![verlet](https://user-images.githubusercontent.com/88845385/186844306-4432b202-3c87-4c4a-bf2a-737c01dd4d9a.png)

마지막 식에 주목하자. ___이제는 입자의 이전 위치에 대한 정보가 필요하지만, 그 대가로 속도 항이 사라져 버렸다.___

따라서 __Verlet integration__ 은 기존의 방법에 비해 다음과 같은 장단점이 있는 것으로 생각된다.

_장점:_ 입자를 임의로 조작하기 위해 신경써야 하는 변수가 하나로 줄었다. 다시 말해, 위치를 임의로 제한하거나 조작해도 그에 맞게 시뮬레이션된다.

_단점:_ 속도를 임의로 제한하거나 조작하기 까다롭다.

위의 장점 부분이 수직항력의 구현을 가능케한다. __오일러 방법__ 에서는 물체의 위치뿐 아니라 __속도 벡터 또한 섬세하게 조작하지 않으면 안 되었으나,__ __verlet integration__ 에서는 그저 __위치를 알맞게 조정해주는 것만으로 충분한 것이다.__

글로만 서술하면 와닿지 않으니 이론은 이쯤 하고 넘어가자. 사실 나도 잘 모르겠다.

---

## 구현

언어는 `C++`, 외부 라이브러리는 `raylib`을 사용했다.

글이 길어지지 않게 하기 위해 핵심 코드만 서술한다. 어차피 주석이 없어서 나도 해석 못 한다. 수고링.

### Verlet integration을 수행하는 클래스

```C++
class VerletMatter{
protected:
    Vector2 pos, pos_prev;
public:
    VerletMatter(Vector2 _pos, Vector2 _pos_prev):pos(_pos), pos_prev(_pos_prev) {}

    void setPos(Vector2 _pos) {pos = _pos;}
    void addPos(Vector2 _pos) {pos = Vector2Add(pos, _pos);}
    void subPos(Vector2 _pos) {pos = Vector2Subtract(pos, _pos);}
    Vector2 getPos() {return pos;}

    void update(Vector2 acc, float delta){
        Vector2 pos_save = pos;
        
        // pos = 2*pos - pos_prev + acc*delta*delta;
        pos = Vector2Add(pos, Vector2Scale(pos,0.999f));
        pos = Vector2Subtract(pos, Vector2Scale(pos_prev, 0.999f));
        pos = Vector2Add(pos, Vector2Scale(acc, delta*delta));

        pos_prev = pos_save;
    }
};
```

사족으로, 가속도를 클래스 멤버로 넣어야 하나 고민했으나 이는 외부 요인(힘)에 의한 것이므로 인자로 전달받기로 했다.

### 원(반지름과 색 추가)

```c++
class VerletCircle : public VerletMatter{
private:
    float radius;
    Color color;
public:
    VerletCircle(Vector2 pos, Vector2 pos_prev, float _radius, Color _color):VerletMatter(pos, pos_prev), radius(_radius), color(_color) {}

    float getRadius() {return radius;}
    void setColor(Color _color) {color = _color;}

    void draw(){
        DrawCircleV(pos, radius, color);
    }
};
```

### 전체 시스템

```c++
class VerletSystem{
private:
    float radius;
    Vector2 gravity;
    std::vector<VerletCircle*> mats;
public:
    void update(float delta){
        for(int i=0; i<(int)mats.size(); i++){
            // update circle position
            mats[i]->update(gravity, delta);
            
            // Wall constraint
            Vector2 towards = Vector2Subtract({800.0f, 450.0f}, mats[i]->getPos());
            float correction = Vector2Length(towards) - (radius - mats[i]->getRadius());
            if(correction > 0.0f){
                Vector2 correction_vec = Vector2Scale(Vector2Normalize(towards), correction);
                mats[i]->setPos(Vector2Add(mats[i]->getPos(), correction_vec));
            }
            
            // Circle constraint
            for(int j=0; j<(int)mats.size(); j++){
                if(i != j){
                    Vector2 towards = Vector2Subtract(mats[i]->getPos(), mats[j]->getPos());
                    float correction = mats[i]->getRadius() + mats[j]->getRadius() - Vector2Length(towards);
                    if(correction>0.0f){
                        Vector2 correction_vec = Vector2Scale(Vector2Normalize(towards), correction*0.5f);
                        mats[i]->addPos(correction_vec);
                        mats[j]->subPos(correction_vec);
                    }
                }
            }
        }
    }
};
```

---

## 결과

![ball](https://user-images.githubusercontent.com/88845385/186849005-4d95592d-c55f-42a7-8aab-c2fc50fff936.gif)

그저 신기할 따름...

---

## Constraint 구현

간단한 아이디어로 constraint를 구현할 수 있다.

### 입자를 고정시키기

```c++
class Pin{
public:
    VerletMatter *m;
private:
    Vector2 pos;

public:
    Pin(VerletMatter* _m, Vector2 _pos):m(_m), pos(_pos) {}

    void bind(){
        m->setPos(pos);
    }
};
```

### 두 입자 사이의 거리를 제한하기

단순히 두 입자 간 거리가 멀어지면 서로 다가가도록 만드는 것으로 충분하다. verlet integration의 진가가 드러나는 대목이다.

```c++
class Chain{
public:
    VerletMatter *m1, *m2;
private:
    float length;
    float stiffness;

public:
    Chain(VerletMatter* _m1, VerletMatter* _m2, float _length, float _stiffness = 0.5f):m1(_m1), m2(_m2), length(_length), stiffness(_stiffness) {}

    bool checkLimit(){
        float tension = (Vector2Distance(m1->getPos(), m2->getPos()) - length)/length;
        return tension > stiffness;
    }

    void bind(){
        Vector2 towards = Vector2Subtract(m2->getPos(), m1->getPos());
        float towards_length = Vector2Length(towards);
        if(towards_length > length){
            Vector2 correction_vec = Vector2Scale(Vector2Normalize(towards), (towards_length-length)*0.5f);
            m1->addPos(correction_vec);
            m2->subPos(correction_vec);
        }
    }
};
```

---

## 결과(2)

![chain](https://user-images.githubusercontent.com/88845385/186848898-38613dfa-a9e3-475b-8efd-bf4b89eabf3e.gif)

솔직히 이렇게 잘 나올 줄 몰랐다(...)

---

## 여담

상당히 흥미로운 방법이지만 그렇다고 만능은 아니다. 간단히 구현할 수 있는 건 저 정도가 대부분이고, 강체물리 등은 전혀 다른 접근이 필요할 것으로 생각된다.

글을 쓰기 너무 귀찮아서 대충대충 한 감이 있는데 양해 바랍니다. 어차피 아무도 안 읽는데 뭐. 불만 있으면 내게 돌을 던져라.
