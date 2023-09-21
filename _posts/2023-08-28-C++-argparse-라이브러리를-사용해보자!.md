---
title: C++ argparse 라이브러리를 사용해보자!
date: 2023-08-28 22:01:00 +0900
tags: [프로그래밍, C++, 라이브러리]

---

# 개요

최근 명령줄 프로그램을 개발하면서 직접 인수를 파싱하다 보니 코드가 상당히 지저분하게 되었다. 그래서 **C++**에서 사용할 수 있는 파서 라이브러리를 찾아 사용법을 정리하고자 한다.

***본 게시글은 C++ 명령줄 프로그램의 인자를 파싱하기 위한 오픈 소스 라이브러리 [argparse](https://github.com/p-ranav/argparse/tree/master)의 공식 소개 문서를 기반으로 작성되었습니다.***

---

<p align="center">
  <img height="100" src="https://i.imgur.com/oDXeMUQ.png" alt="argparse"/>
</p>



## 특징

* 단일 헤더 파일
* **C++17** 필요
* MIT 라이선스

## Quick Start

**argparse.hpp** 헤더파일을 포함시키면 바로 사용할 수 있습니다!

```cpp
#include <argparse/argparse.hpp>
```

명령줄 인수를 파싱하기 위해 먼저 `ArgumentParser` 객체를 선언한다.

```cpp
argparse::ArgumentParser program("program_name");
```

**NOTE:** `ArgumentParser`의 두 번째 인수로 프로그램 버전을 입력할 수 있다.

**NOTE:** `ArgumentParser`의 세 번째 및 네 번째 인수로 기본 인자를 정의할 수도 있다.

Ex) `argparse::ArgumentParser program("libfoo", "1.9.0", default_arguments::help, false);`

새 인수를 추가하려면 `.add_argument(...)`를 호출하면 된다. 여러 개의 인수 이름(`-v`와 `--verbose` 등)을 하나의 그룹으로 지정할 수 있다.

```cpp
program.add_argument("foo");
program.add_argument("-v", "--verbose"); // parameter packing
```

`argparse`는 위치 인수, 선택적 인수 및 복합 인수와 같은 다양한 인수 유형을 지원한다. 아래에서 각 유형에 대한 사용법을 기술한다.

---

### 위치 인수(Positional Arguments)

**위치 인수**는 입력 순서대로 할당되는 인수 유형이다. 다음 예제처럼 사용할 수 있다.

```cpp
#include <argparse/argparse.hpp>

int main(int argc, char *argv[]) {
  argparse::ArgumentParser program("program_name");

  program.add_argument("square")
    .help("display the square of a given integer")
    .scan<'i', int>();

  try {
    program.parse_args(argc, argv);
  }
  catch (const std::runtime_error& err) {
    std::cerr << err.what() << std::endl;
    std::cerr << program;
    return 1;
  }

  auto input = program.get<int>("square");
  std::cout << (input * input) << std::endl;

  return 0;
}
```

그리고 코드를 실행하면 다음 결과를 얻는다.

```console
foo@bar:/home/dev/$ ./main 15
225
```

무슨 일이 일어났는지 살펴보자:

* 프로그램이 받을 명령줄 옵션을 지정하기 위해 `add_argument()` 함수가 사용되었다.
* 기본적으로 명령줄 인자는 문자열로 해석된다. `.scan()` 함수 체이닝을 통해 값을 정수로 변환했다.
* 특정 인수의 값을 읽기 위해 `parser.get<T>(key)` 함수를 사용했다.

### 선택적 인수(Optional Arguments)

이제 선택적 인수를 살펴 보자. 선택적 인수는 `-`나 `--`로 시작한다. 명령어 입력 시 꼭 순서대로 배열할 필요 없이 아무 위치에나 들어갈 수 있는 인수이다.


```cpp
argparse::ArgumentParser program("test");

program.add_argument("--verbose")
  .help("increase output verbosity")
  .default_value(false)
  .implicit_value(true);

try {
  program.parse_args(argc, argv);
}
catch (const std::runtime_error& err) {
  std::cerr << err.what() << std::endl;
  std::cerr << program;
  std::exit(1);
}

if (program["--verbose"] == true) {
  std::cout << "Verbosity enabled" << std::endl;
}
```

```console
foo@bar:/home/dev/$ ./main --verbose
Verbosity enabled
```

무슨 일이 일어났는지 살펴보자:
* `--verbose` 인수가 주어졌을 때만 화면에 뭔가 출력하고 그렇지 않을 때는 아무 것도 출력하지 않는 프로그램이다.
* Since the argument is actually optional, no error is thrown when running the program without ```--verbose```. Note that by using ```.default_value(false)```, if the optional argument isn’t used, it's value is automatically set to false.
* 실행 시 `--verbose` 인수를 명시하지 않아도 오류를 뱉지 않는다. `.default_value(false)`를 사용해 인수가 주어지지 않았을 때의 기본값을 설정했다.
* `.implicit_value(true)`를 사용해 이 옵션이 어떤 값을 저장하기보다는 플래그 역할로 사용되도록 명시했다. 값 없이 `--verbose`만 입력하면 자동으로 `true`로 설정된다.

#### 선택적 인수 요구하기(Requiring optional arguments)

물론 선택적 인수를 **필수**로 만들고 싶은 경우가 있을 수 있다. 위에서 언급한 대로 선택적 인수는 `-` 또는 `--`로 시작한다. 이러한 유형의 인수를 필수로 만들려면 다음과 같이 작성하면 된다.

```cpp
program.add_argument("-o", "--output")
  .required()
  .help("specify the output file.");
```

이제 사용자가 이 매개변수에 값을 제공하지 않으면 예외가 발생한다.

또는 다음과 같이 기본 값을 지정하는 방법도 있다.

```cpp
program.add_argument("-o", "--output")
  .default_value(std::string("-"))
  .required()
  .help("specify the output file.");
```

#### 기본값 없이 선택적 인수 안전하게 사용하기(Accessing optional arguments without default values)

선택적 인수에 특별히 지정할 만한 기본값이 없지만 예외 처리를 하기는 싫다면 다음과 같이 사용할 수도 있다.

```cpp
if (auto fn = program.present("-o")) {
    do_something_with(*fn);
}
```

`get`과 유사하게, `present` 메서드도 템플릿으로 타입 지정이 가능하다. 그러나 `parser.present<T>(key)`은 `T` 대신 `std::optional<T>`를 반환하며, 사용자가 인수에 값을 지정하지 않았다면 값이 `std::nullopt`로 지정된다.

#### 사용자가 직접 지정한 값인지 확인하기

`default_value`를 가진 인수의 값을 사용자가 제공했는지, 혹은 기본값인지 여부를 확인하려면 `argument.is_used()`를 이용하자.

```cpp
program.add_argument("--color")
  .default_value(std::string{"orange"})   // might otherwise be type const char* leading to an error when trying program.get<std::string>
  .help("specify the cat's fur color");

try {
  program.parse_args(argc, argv);    // Example: ./main --color orange
}
catch (const std::runtime_error& err) {
  std::cerr << err.what() << std::endl;
  std::cerr << program;
  std::exit(1);
}

auto color = program.get<std::string>("--color");  // "orange"
auto explicit_color = program.is_used("--color");  // true, user provided orange
```

#### 선택적 인수 반복

동일한 이름의 선택적 인수를 반복 지정했을 때 이 값들을 `std::vector` 컨테이너에 모아둘 수 있다.

```cpp
program.add_argument("--color")
  .default_value<std::vector<std::string>>({ "orange" })
  .append()
  .help("specify the cat's fur color");

try {
  program.parse_args(argc, argv);    // Example: ./main --color red --color green --color blue
}
catch (const std::runtime_error& err) {
  std::cerr << err.what() << std::endl;
  std::cerr << program;
  std::exit(1);
}

auto colors = program.get<std::vector<std::string>>("--color");  // {"red", "green", "blue"}
```

```.default_value``` 의 인자는 ```.get```에서 읽고자 하는 값과 동일한 타입으로 작성해햐 한다는 점에 주의하자.

#### 값을 증가시키기 위한 인수 반복

해당 인수가 몇 번 입력되었는지를 확인할 수도 있다.

```cpp
int verbosity = 0;
program.add_argument("-V", "--verbose")
  .action([&](const auto &) { ++verbosity; })
  .append()
  .default_value(false)
  .implicit_value(true)
  .nargs(0);

program.parse_args(argc, argv);    // Example: ./main -VVVV

std::cout << "verbose level: " << verbosity << std::endl;    // verbose level: 4
```

### 음수 표현

알다시피 선택적 인수는 `-`로 시작한다. 이때문에 음수값 지정에 대해 걱정할 수 있는데, 다행히도 `argparse`는 음수를 잘 처리한다.

```cpp
argparse::ArgumentParser program;

program.add_argument("integer")
  .help("Input number")
  .scan<'i', int>();

program.add_argument("floats")
  .help("Vector of floats")
  .nargs(4)
  .scan<'g', float>();

try {
  program.parse_args(argc, argv);
}
catch (const std::runtime_error& err) {
  std::cerr << err.what() << std::endl;
  std::cerr << program;
  std::exit(1);
}

// Some code to print arguments
```

```console
foo@bar:/home/dev/$ ./main -5 -1.1 -3.1415 -3.1e2 -4.51329E3
integer : -5
floats  : -1.1 -3.1415 -310 -4513.29
```

### 위치 인수와 선택적 인수 함께 쓰기

```cpp
argparse::ArgumentParser program("main");

program.add_argument("square")
  .help("display the square of a given number")
  .scan<'i', int>();

program.add_argument("--verbose")
  .default_value(false)
  .implicit_value(true);

try {
  program.parse_args(argc, argv);
}
catch (const std::runtime_error& err) {
  std::cerr << err.what() << std::endl;
  std::cerr << program;
  std::exit(1);
}

int input = program.get<int>("square");

if (program["--verbose"] == true) {
  std::cout << "The square of " << input << " is " << (input * input) << std::endl;
}
else {
  std::cout << (input * input) << std::endl;
}
```

```console
foo@bar:/home/dev/$ ./main 4
16

foo@bar:/home/dev/$ ./main 4 --verbose
The square of 4 is 16

foo@bar:/home/dev/$ ./main --verbose 4
The square of 4 is 16
```

### 도움말 출력

`std::cout << program` 은 `ArgumentParser`에 등록된 정보를 바탕으로 프로그램 사용법을 출력합니다. 이전 예제 코드에 대한 기본 도움말은 다음과 같습니다:

```
foo@bar:/home/dev/$ ./main --help
Usage: main [-h] [--verbose] square

Positional arguments:
  square       	display the square of a given number

Optional arguments:
  -h, --help   	shows help message and exits
  -v, --version	prints version information and exits
  --verbose
```

`program.help().str()`를 이용해 도움말 메시지를 스트링으로 읽을 수도 있습니다.

#### 도움말에 설명 또는 에필로그 추가하기

`ArgumentParser::add_description`로 인수의 상세 설명 이전에 텍스트를 추가합니다.
`ArgumentParser::add_epilog` 도움말 끝부분에 텍스트를 추가합니다.

```cpp
#include <argparse/argparse.hpp>

int main(int argc, char *argv[]) {
  argparse::ArgumentParser program("main");
  program.add_argument("thing").help("Thing to use.").metavar("THING");
  program.add_argument("--member").help("The alias for the member to pass to.").metavar("ALIAS");
  program.add_argument("--verbose").default_value(false).implicit_value(true);

  program.add_description("Forward a thing to the next member.");
  program.add_epilog("Possible things include betingalw, chiz, and res.");

  program.parse_args(argc, argv);

  std::cout << program << std::endl;
}
```

```console
Usage: main [-h] [--member ALIAS] [--verbose] THING

Forward a thing to the next member.

Positional arguments:
  THING         	Thing to use.

Optional arguments:
  -h, --help    	shows help message and exits
  -v, --version 	prints version information and exits
  --member ALIAS	The alias for the member to pass to.
  --verbose     	

Possible things include betingalw, chiz, and res.
```

### 인수 리스트

`.nargs`를 사용해 한 종류의 인수에 여러 개의 값을 요구할 수 있습니다. `std::vector` 형식으로 읽어집니다.

```cpp
argparse::ArgumentParser program("main");

program.add_argument("--input_files")
  .help("The list of input files")
  .nargs(2);

try {
  program.parse_args(argc, argv);   // Example: ./main --input_files config.yml System.xml
}
catch (const std::runtime_error& err) {
  std::cerr << err.what() << std::endl;
  std::cerr << program;
  std::exit(1);
}

auto files = program.get<std::vector<std::string>>("--input_files");  // {"config.yml", "System.xml"}
```

```ArgumentParser.get<T>()``` 는 ```std::vector``` and ```std::list``` 각각에 대한 특수화를 제공합니다. 따라서 다음 예제처럼 ```.get<std::list>``` 또한 작동합니다.

```cpp
auto files = program.get<std::list<std::string>>("--input_files");  // {"config.yml", "System.xml"}
```

```.scan```을 사용해 인수의 자료형을 원하는 형태로 전처리할 수 있습니다.

```cpp
argparse::ArgumentParser program("main");

program.add_argument("--query_point")
  .help("3D query point")
  .nargs(3)
  .default_value(std::vector<double>{0.0, 0.0, 0.0})
  .scan<'g', double>();

try {
  program.parse_args(argc, argv); // Example: ./main --query_point 3.5 4.7 9.2
}
catch (const std::runtime_error& err) {
  std::cerr << err.what() << std::endl;
  std::cerr << program;
  std::exit(1);
}

auto query_point = program.get<std::vector<double>>("--query_point");  // {3.5, 4.7, 9.2}
```

```.nargs```로 가변 개수의 값을 요구하는 인수를 설정할 수 있습니다.

아래는 예시입니다.

```cpp
program.add_argument("--input_files")
  .nargs(1, 3);  // This accepts 1 to 3 arguments.
```

파이썬 argparse 모듈의 "?", "*", "+" 에 대응하는 유용한 패턴 또한 정의되어 있습니다.

```cpp
program.add_argument("--input_files")
  .nargs(argparse::nargs_pattern::any);  // "*" in Python. This accepts any number of arguments including 0.
```
```cpp
program.add_argument("--input_files")
  .nargs(argparse::nargs_pattern::at_least_one);  // "+" in Python. This accepts one or more number of arguments.
```
```cpp
program.add_argument("--input_files")
  .nargs(argparse::nargs_pattern::optional);  // "?" in Python. This accepts an argument optionally.
```

### 복합 인수

복합 인수란 서로 결합되어 마치 하나의 인수처럼 사용될 수 있는 선택적 인수입니다.

Ex)  ```ps -aux```

```cpp
argparse::ArgumentParser program("test");

program.add_argument("-a")
  .default_value(false)
  .implicit_value(true);

program.add_argument("-b")
  .default_value(false)
  .implicit_value(true);

program.add_argument("-c")
  .nargs(2)
  .default_value(std::vector<float>{0.0f, 0.0f})
  .scan<'g', float>();

try {
  program.parse_args(argc, argv);                  // Example: ./main -abc 1.95 2.47
}
catch (const std::runtime_error& err) {
  std::cerr << err.what() << std::endl;
  std::cerr << program;
  std::exit(1);
}

auto a = program.get<bool>("-a");                  // true
auto b = program.get<bool>("-b");                  // true
auto c = program.get<std::vector<float>>("-c");    // {1.95, 2.47}

/// Some code that prints parsed arguments
```

```console
foo@bar:/home/dev/$ ./main -ac 3.14 2.718
a = true
b = false
c = {3.14, 2.718}

foo@bar:/home/dev/$ ./main -cb
a = false
b = true
c = {0.0, 0.0}
```

무슨 일이 일어났는지 살펴보자:
* 세 개의 선택적 인수 ```-a```, ```-b``` 그리고```-c```가 존재한다.
* ```-a``` 와 ```-b``` 는 `.default_value`와 `.implicit_value`설정으로 인해 플래그처럼 사용된다.
* ```-c``` 는 두 개의 부동 소수점 값을 요구한다.
* argparse는 ```-abc``` or ```-bac``` or ```-cab```와 같은 복합 인수를 허용한다. 단, 단일 알파벳 인수 이름에만 적용된다.
  - ```-a``` 와 ```-b``` 는 true로 설정된다.
  - argv는 파싱되어 ```-c```가 요구하는 값을 찾는다.
  - 만약 argparse가 c에 매핑된 값을 찾지 못하면, c는 `.default_value`에 정의된 대로 기본값 `{0.0, 0.0}`을 갖는다.

### 숫자 자료형으로 변환

사용자는 값을 기본 자료형으로 표현할 수 있습니다.

`.scan<Shape, T>` 함수는 주어진 `std::string`을 `Shape` 변환 지시자를 통해 자료형 `T`로 변환하려고 시도합니다. 만약 이 과정에서 문제가 생긴다면 `std::invalid_argument` 또는 `std::range_error` 예외를 발생합니다.

```cpp
program.add_argument("-x")
       .scan<'d', int>();

program.add_argument("scale")
       .scan<'g', double>();
```

`Shape`은 입력값이 어떻게 생겼는지를 지정하고 자료형 인자는 결과적으로 반환될 값의 자료형을 지정합니다. 허용되는 자료형은 부동 소수점(i.e float, double, long double) 과 정수형 (i.e. signed char, short, int, long, long long)입니다.

문법은 `std::from_chars`를 따르지만 똑같지는 않습니다. 예를 들어, 16진수는 `0x`나 `0X`로 시작할 수 있고 0으로 시작하는 숫자는 8진수로 해석될 수 있습니다.

|   Shape    | interpretation                            |
| :--------: | ----------------------------------------- |
| 'a' or 'A' | hexadecimal floating point                |
| 'e' or 'E' | scientific notation (floating point)      |
| 'f' or 'F' | fixed notation (floating point)           |
| 'g' or 'G' | general form (either fixed or scientific) |
|            |                                           |
|    'd'     | decimal                                   |
|    'i'     | `std::from_chars` grammar with base == 0  |
|    'o'     | octal (unsigned)                          |
|    'u'     | decimal (unsigned)                        |
| 'x' or 'X' | hexadecimal (unsigned)                    |

### 사전 정의된 인수

`argparse` 는 미리 정의된 인수 `-h`/`--help` 와 `-v`/`--version`를 제공합니다. 기본적으로, 이 인수가 주어졌을 때 도움말 또는 버전 메시지를 출력하고 프로그램을 종료합니다. 이때 지금껏 할당된 리소스의 소멸자를 호출하는 과정은 생략됩니다.

`ArgumentParser`를 생성할 때 사전 정의된 인수를 비활성화할 수 있습니다.

(기본 인수를 조정하기 위해 프로그램의 이름과 버전이 반드시 명시되어야 하는 점에 주목하세요.)

```cpp
argparse::ArgumentParser program("test", "1.0", default_arguments::none);

program.add_argument("-h", "--help")
  .action([=](const std::string& s) {
    std::cout << help().str();
  })
  .default_value(false)
  .help("shows help message")
  .implicit_value(true)
  .nargs(0);
```

위의 코드는 도움말을 출력하고 프로그램을 계속 실행합니다. `--version`는 직접 정의하지 않았으므로 위 예제에서는 이 인수를 사용할 수 없습니다.

기본값은 `default_arguments:all`입니다. 이외에 `default_arguments::none`. `default_arguments::help` 및 `default_arguments::version`를 사용할 수 있습니다.

사전 정의된 인수(version, help)가 사용자로부터 입력되면 버전 또는 도움말을 출력한 뒤 프로그램을 종료합니다. `ArgumentParser`의 네 번째 인자를 설정해 이를 바꿀 수 있습니다. `exit_on_default_arguments`는 기본값이 **true**인 플래그 값입니다. 아래 코드에서는 사전 정의된 인수를 사용하지만 이것이 사용자로부터 입력되어도 프로그램을 계속 실행합니다.

```cpp
argparse::ArgumentParser program("test", "1.0", default_arguments::all, false)
```

### 잔여 인수

`argparse` 는 명령어의 끝에 "남아 있는" 인수를 처리하는 기능을 지원합니다. 컴파일러 등에서 사용되곤 하는 방식입니다.

```console
foo@bar:/home/dev/$ compiler file1 file2 file3
```

To enable this, simply create an argument and mark it as `remaining`. All remaining arguments passed to argparse are gathered here.

이를 활설화하기 위해 인수를 정의하고 `remaining`으로 설정해두세요. `std::vector<std::string>`컨테이너에 잔여 인수를 저장합니다.

```cpp
argparse::ArgumentParser program("compiler");

program.add_argument("files")
  .remaining();

try {
  program.parse_args(argc, argv);
}
catch (const std::runtime_error& err) {
  std::cerr << err.what() << std::endl;
  std::cerr << program;
  std::exit(1);
}

try {
  auto files = program.get<std::vector<std::string>>("files");
  std::cout << files.size() << " files provided" << std::endl;
  for (auto& file : files)
    std::cout << file << std::endl;
} catch (std::logic_error& e) {
  std::cout << "No files provided" << std::endl;
}
```

위 예제에서, 인수를 지정하지 않았을 때는 다음과 같은 결과가 나타납니다.

```console
foo@bar:/home/dev/$ ./compiler
No files provided
```

인수에 여러 값이 할당되었을 때는 다음과 같습니다.

```console
foo@bar:/home/dev/$ ./compiler foo.txt bar.txt baz.txt
3 files provided
foo.txt
bar.txt
baz.txt
```

잔여 인수는 선택적 인수와 함께 사용해도 잘 작동합니다.

```cpp
argparse::ArgumentParser program("compiler");

program.add_arguments("-o")
  .default_value(std::string("a.out"));

program.add_argument("files")
  .remaining();

try {
  program.parse_args(argc, argv);
}
catch (const std::runtime_error& err) {
  std::cerr << err.what() << std::endl;
  std::cerr << program;
  std::exit(1);
}

auto output_filename = program.get<std::string>("-o");
std::cout << "Output filename: " << output_filename << std::endl;

try {
  auto files = program.get<std::vector<std::string>>("files");
  std::cout << files.size() << " files provided" << std::endl;
  for (auto& file : files)
    std::cout << file << std::endl;
} catch (std::logic_error& e) {
  std::cout << "No files provided" << std::endl;
}

```

```console
foo@bar:/home/dev/$ ./compiler -o main foo.cpp bar.cpp baz.cpp
Output filename: main
3 files provided
foo.cpp
bar.cpp
baz.cpp
```

***NOTE***: 선택적 인수가 명령어 내에서 비교적 위치 선정이 자유롭다고는 하지만, 반드시 잔여 인수의 앞에 위치해야 합니다. 선택적 인수를 잔여 인수의 뒤에 지정하려고 하면 그냥 잔여 인수로 취급됩니다. 아래 예시를 보세요.

```console
foo@bar:/home/dev/$ ./compiler foo.cpp bar.cpp baz.cpp -o main
5 arguments provided
foo.cpp
bar.cpp
baz.cpp
-o
main
```

---

### ArgumentParser의 bool 값

An `ArgumentParser` is `false` until it (or one of its subparsers) have extracted
known value(s) with `.parse_args` or `.parse_known_args`. When using `.parse_known_args`,
unknown arguments will not make a parser `true`.

`ArgumentParser`는 `.parse_args`나 `.parse_known_args`를 이용해 값을 추출하기 전까지 `false`값을 가집니다. `.parse_known_args`를 사용했지만 어떠한 값도 파싱하지 못한 경우에도 여전히 `false`를 유지합니다.

### 커스텀 접두사

대부분의 명령줄 옵션은 `-`를 접두사로 사용합니다. 그러나 `argparse`는 커스텀 접두사를 설정하는 기능을 제공합니다. `set_prefix_chars()`를 이용합니다.

당연히 기본 설정값은 `-` 입니다.

```cpp
#include <argparse/argparse.hpp>
#include <cassert>

int main(int argc, char *argv[]) {
  argparse::ArgumentParser program("test");
  program.set_prefix_chars("-+/");

  program.add_argument("+f");
  program.add_argument("--bar");
  program.add_argument("/foo");

  try {
    program.parse_args(argc, argv);
  }
  catch (const std::runtime_error& err) {
    std::cerr << err.what() << std::endl;
    std::cerr << program;
    return 1;
  }

  if (program.is_used("+f")) {
    std::cout << "+f    : " << program.get("+f") << "\n";
  }

  if (program.is_used("--bar")) {
    std::cout << "--bar : " << program.get("--bar") << "\n";
  }

  if (program.is_used("/foo")) {
    std::cout << "/foo  : " << program.get("/foo") << "\n";
  }  
}
```

```console
foo@bar:/home/dev/$ ./main +f 5 --bar 3.14f /foo "Hello"
+f    : 5
--bar : 3.14f
/foo  : Hello
```

### 커스텀 할당 문자 

접두 문자 뿐만 아니라, '할당 문자' 또한 지정할 수 있습니다. `./test --foo=FOO /B:Bar`와 같이 사용하도록 설정할 수 있습니다.

기본 할당 문자는 `=`입니다.

```cpp
#include <argparse/argparse.hpp>
#include <cassert>

int main(int argc, char *argv[]) {
  argparse::ArgumentParser program("test");
  program.set_prefix_chars("-+/");
  program.set_assign_chars("=:");

  program.add_argument("--foo");
  program.add_argument("/B");

  try {
    program.parse_args(argc, argv);
  }
  catch (const std::runtime_error& err) {
    std::cerr << err.what() << std::endl;
    std::cerr << program;
    return 1;
  }

  if (program.is_used("--foo")) {
    std::cout << "--foo : " << program.get("--foo") << "\n";
  }

  if (program.is_used("/B")) {
    std::cout << "/B    : " << program.get("/B") << "\n";
  }
}
```

```console
foo@bar:/home/dev/$ ./main --foo=Foo /B:Bar
--foo : Foo
/B    : Bar
```

---

## 심화 예제

### filename 인수를 받아 JSON 객체 구성하기

```cpp
argparse::ArgumentParser program("json_test");

program.add_argument("config")
  .action([](const std::string& value) {
    // read a JSON file
    std::ifstream stream(value);
    nlohmann::json config_json;
    stream >> config_json;
    return config_json;
  });

try {
  program.parse_args({"./test", "config.json"});
}
catch (const std::runtime_error& err) {
  std::cerr << err.what() << std::endl;
  std::cerr << program;
  std::exit(1);
}

nlohmann::json config = program.get<nlohmann::json>("config");
```

### 위치 인수와 복합 토글 인수 함께 사용하기

```cpp
argparse::ArgumentParser program("test");

program.add_argument("numbers")
  .nargs(3)
  .scan<'i', int>();

program.add_argument("-a")
  .default_value(false)
  .implicit_value(true);

program.add_argument("-b")
  .default_value(false)
  .implicit_value(true);

program.add_argument("-c")
  .nargs(2)
  .scan<'g', float>();

program.add_argument("--files")
  .nargs(3);

try {
  program.parse_args(argc, argv);
}
catch (const std::runtime_error& err) {
  std::cerr << err.what() << std::endl;
  std::cerr << program;
  std::exit(1);
}

auto numbers = program.get<std::vector<int>>("numbers");        // {1, 2, 3}
auto a = program.get<bool>("-a");                               // true
auto b = program.get<bool>("-b");                               // true
auto c = program.get<std::vector<float>>("-c");                 // {3.14f, 2.718f}
auto files = program.get<std::vector<std::string>>("--files");  // {"a.txt", "b.txt", "c.txt"}

/// Some code that prints parsed arguments
```

```console
foo@bar:/home/dev/$ ./main 1 2 3 -abc 3.14 2.718 --files a.txt b.txt c.txt
numbers = {1, 2, 3}
a = true
b = true
c = {3.14, 2.718}
files = {"a.txt", "b.txt", "c.txt"}
```

### 인수에 할당 가능한 값의 종류 제한하기

```cpp
argparse::ArgumentParser program("test");

program.add_argument("input")
  .default_value(std::string{"baz"})
  .action([](const std::string& value) {
    static const std::vector<std::string> choices = { "foo", "bar", "baz" };
    if (std::find(choices.begin(), choices.end(), value) != choices.end()) {
      return value;
    }
    return std::string{ "baz" };
  });

try {
  program.parse_args(argc, argv);
}
catch (const std::runtime_error& err) {
  std::cerr << err.what() << std::endl;
  std::cerr << program;
  std::exit(1);
}

auto input = program.get("input");
std::cout << input << std::endl;
```

```console
foo@bar:/home/dev/$ ./main fex
baz
```

## `option=value` 문법 사용하기

```cpp
#include "argparse.hpp"
#include <cassert>

int main(int argc, char *argv[]) {
  argparse::ArgumentParser program("test");
  program.add_argument("--foo").implicit_value(true).default_value(false);
  program.add_argument("--bar");

  try {
    program.parse_args(argc, argv);
  }
  catch (const std::runtime_error& err) {
    std::cerr << err.what() << std::endl;
    std::cerr << program;
    return 1;
  }

  if (program.is_used("--foo")) {
    std::cout << "--foo: " << std::boolalpha << program.get<bool>("--foo") << "\n";
  }

  if (program.is_used("--bar")) {
    std::cout << "--bar: " << program.get("--bar") << "\n";
  }  
}
```

```console
foo@bar:/home/dev/$ ./test --bar=BAR --foo
--foo: true
--bar: BAR
```

---

## 설명하지 않은 기능들

이외에 argparse에 구현되어 있지만 설명하지 않은 기능으로 Parent Parsers, Subcommands, Known Args Pasring이 있다. 추후 이것들을 사용하게 되면 그때 정리하는 게 나을 듯.
