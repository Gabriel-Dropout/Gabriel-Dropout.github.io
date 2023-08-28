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
* MIT 라이선스스

## Quick Start

**argparse.hpp** 헤더파일을 포함시키는 것으로 충분하다.

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

**위치 인수**는 다음 예제처럼 사용할 수 있다.

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
* 기본적으로 명령줄 인자는 문자열로 해석된다. `.scan` 함수 체이닝을 통해 값을 정수로 변환했다.
* 특정 인수의 값을 읽기 위해 `parser.get<T>(key)` 함수를 사용했다.

### 선택적 인수(Optional Arguments)

이제 선택적 인수를 살펴 보자. 선택적 인자는 `-`나 `--`로 시작한다. 프로그램 실행 시 꼭 순서대로 배열할 필요 없이 아무 위치에나 들어갈 수 있는 인수이다.


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
* `--verbose` 인자가 주어졌을 때만 화면에 뭔가 출력하고 그렇지 않을 때는 아무 것도 출력하지 않는 프로그램이다.
* Since the argument is actually optional, no error is thrown when running the program without ```--verbose```. Note that by using ```.default_value(false)```, if the optional argument isn’t used, it's value is automatically set to false.
* 실행 시 `--verbose` 인자를 명시하지 않아도 오류를 뱉지 않는다. `.default_value(false)`를 사용해 인수가 주어지지 않았을 때의 기본값을 설정했다.
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

#### Accessing optional arguments without default values

선택적 인수에 특별히 지정할 만한 기본값이 없지만 예외 처리를 하기는 싫다면 다음과 같이 사용할 수도 있다.

```cpp
if (auto fn = program.present("-o")) {
    do_something_with(*fn);
}
```

`get`과 유사하게, `present` 메서드도 템플릿 인수를 사용할 수 있다. 그러나 `parser.present<T>(key)`은 `std::optional<T>`를 반환하여 사용자가 이 매개변수에 값을 지정하지 않으면 반환값이 `std::nullopt`가 된다.

#### 사용자가 직접 지정한 값인지 확인하기

`default_value`를 가진 인수의 값을 사용자가 제공했는지 여부를 확인하려면 `argument.is_used()`를 이용하자.

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

더 큰 값을 표현하기 위해 인수를 반복하는 경우도 종종 있다.

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

알다시피 선택적 인수는 `-`로 시작한다. 다행히도 `argparse`는 음수를 잘 처리한다.

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

---

## 미번역 부분(수정 예정)

### 도움말 출력

`std::cout << program` prints a help message, including the program usage and information about the arguments registered with the `ArgumentParser`. For the previous example, here's the default help message:

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

You may also get the help message in string via `program.help().str()`.

#### Adding a description and an epilog to help

`ArgumentParser::add_description` will add text before the detailed argument
information. `ArgumentParser::add_epilog` will add text after all other help output.

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

### List of Arguments

ArgumentParser objects usually associate a single command-line argument with a single action to be taken. The ```.nargs``` associates a different number of command-line arguments with a single action. When using ```nargs(N)```, N arguments from the command line will be gathered together into a list.

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

```ArgumentParser.get<T>()``` has specializations for ```std::vector``` and ```std::list```. So, the following variant, ```.get<std::list>```, will also work.

```cpp
auto files = program.get<std::list<std::string>>("--input_files");  // {"config.yml", "System.xml"}
```

Using ```.scan```, one can quickly build a list of desired value types from command line arguments. Here's an example:

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

You can also make a variable length list of arguments with the ```.nargs```.
Below are some examples.

```cpp
program.add_argument("--input_files")
  .nargs(1, 3);  // This accepts 1 to 3 arguments.
```

Some useful patterns are defined like "?", "*", "+" of argparse in Python.

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

### Compound Arguments

Compound arguments are optional arguments that are combined and provided as a single argument. Example: ```ps -aux```

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

Here's what's happening:
* We have three optional arguments ```-a```, ```-b``` and ```-c```.
* ```-a``` and ```-b``` are toggle arguments.
* ```-c``` requires 2 floating point numbers from the command-line.
* argparse can handle compound arguments, e.g., ```-abc``` or ```-bac``` or ```-cab```. This only works with short single-character argument names.
  - ```-a``` and ```-b``` become true.
  - argv is further parsed to identify the inputs mapped to ```-c```.
  - If argparse cannot find any arguments to map to c, then c defaults to {0.0, 0.0} as defined by ```.default_value```

### Converting to Numeric Types

For inputs, users can express a primitive type for the value.

The ```.scan<Shape, T>``` method attempts to convert the incoming `std::string` to `T` following the `Shape` conversion specifier. An `std::invalid_argument` or `std::range_error` exception is thrown for errors.

```cpp
program.add_argument("-x")
       .scan<'d', int>();

program.add_argument("scale")
       .scan<'g', double>();
```

`Shape` specifies what the input "looks like", and the type template argument specifies the return value of the predefined action. Acceptable types are floating point (i.e float, double, long double) and integral (i.e. signed char, short, int, long, long long).

The grammar follows `std::from_chars`, but does not exactly duplicate it. For example, hexadecimal numbers may begin with `0x` or `0X` and numbers with a leading zero may be handled as octal values.

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

### Default Arguments

`argparse` provides predefined arguments and actions for `-h`/`--help` and `-v`/`--version`. By default, these actions will **exit** the program after displaying a help or version message, respectively. This exit does not call destructors, skipping clean-up of taken resources.

These default arguments can be disabled during `ArgumentParser` creation so that you can handle these arguments in your own way. (Note that a program name and version must be included when choosing default arguments.)

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

The above code snippet outputs a help message and continues to run. It does not support a `--version` argument.

The default is `default_arguments::all` for included arguments. No default arguments will be added with `default_arguments::none`. `default_arguments::help` and `default_arguments::version` will individually add `--help` and `--version`.

The default arguments can be used while disabling the default exit with these arguments. This forth argument to `ArgumentParser` (`exit_on_default_arguments`) is a bool flag with a default **true** value. The following call will retain `--help` and `--version`, but will not exit when those arguments are used.

```cpp
argparse::ArgumentParser program("test", "1.0", default_arguments::all, false)
```

### Gathering Remaining Arguments

`argparse` supports gathering "remaining" arguments at the end of the command, e.g., for use in a compiler:

```console
foo@bar:/home/dev/$ compiler file1 file2 file3
```

To enable this, simply create an argument and mark it as `remaining`. All remaining arguments passed to argparse are gathered here.

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

When no arguments are provided:

```console
foo@bar:/home/dev/$ ./compiler
No files provided
```

and when multiple arguments are provided:

```console
foo@bar:/home/dev/$ ./compiler foo.txt bar.txt baz.txt
3 files provided
foo.txt
bar.txt
baz.txt
```

The process of gathering remaining arguments plays nicely with optional arguments too:

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

***NOTE***: Remember to place all optional arguments BEFORE the remaining argument. If the optional argument is placed after the remaining arguments, it too will be deemed remaining:

```console
foo@bar:/home/dev/$ ./compiler foo.cpp bar.cpp baz.cpp -o main
5 arguments provided
foo.cpp
bar.cpp
baz.cpp
-o
main
```

### Parent Parsers

A parser may use arguments that could be used by other parsers.

These shared arguments can be added to a parser which is then used as a "parent" for parsers which also need those arguments. One or more parent parsers may be added to a parser with `.add_parents`. The positional and optional arguments in each parent is added to the child parser.

```cpp
argparse::ArgumentParser surface_parser("surface", 1.0, argparse::default_arguments::none);
parent_parser.add_argument("--area")
  .default_value(0)
  .scan<'i', int>();

argparse::ArgumentParser floor_parser("floor");
floor_parser.add_argument("tile_size").scan<'i', int>();
floor_parser.add_parents(surface_parser);
floor_parser.parse_args({ "./main", "--area", "200", "12" });  // --area = 200, tile_size = 12

argparse::ArgumentParser ceiling_parser("ceiling");
ceiling_parser.add_argument("--color");
ceiling_parser.add_parents(surface_parser);
ceiling_parser.parse_args({ "./main", "--color", "gray" });  // --area = 0, --color = "gray"
```

Changes made to parents after they are added to a parser are not reflected in any child parsers. Completely initialize parent parsers before adding them to a parser.

Each parser will have the standard set of default arguments. Disable the default arguments in parent parsers to avoid duplicate help output.

### Subcommands

Many programs split up their functionality into a number of sub-commands, for example, the `git` program can invoke sub-commands like `git checkout`, `git add`, and `git commit`. Splitting up functionality this way can be a particularly good idea when a program performs several different functions which require different kinds of command-line arguments. `ArgumentParser` supports the creation of such sub-commands with the `add_subparser()` member function.

```cpp
#include <argparse/argparse.hpp>

int main(int argc, char *argv[]) {
  argparse::ArgumentParser program("git");

  // git add subparser
  argparse::ArgumentParser add_command("add");
  add_command.add_description("Add file contents to the index");
  add_command.add_argument("files")
    .help("Files to add content from. Fileglobs (e.g.  *.c) can be given to add all matching files.")
    .remaining();

  // git commit subparser
  argparse::ArgumentParser commit_command("commit");
  commit_command.add_description("Record changes to the repository");
  commit_command.add_argument("-a", "--all")
    .help("Tell the command to automatically stage files that have been modified and deleted.")
    .default_value(false)
    .implicit_value(true);

  commit_command.add_argument("-m", "--message")
    .help("Use the given <msg> as the commit message.");

  // git cat-file subparser
  argparse::ArgumentParser catfile_command("cat-file");
  catfile_command.add_description("Provide content or type and size information for repository objects");
  catfile_command.add_argument("-t")
    .help("Instead of the content, show the object type identified by <object>.");

  catfile_command.add_argument("-p")
    .help("Pretty-print the contents of <object> based on its type.");

  // git submodule subparser
  argparse::ArgumentParser submodule_command("submodule");
  submodule_command.add_description("Initialize, update or inspect submodules");
  argparse::ArgumentParser submodule_update_command("update");
  submodule_update_command.add_description("Update the registered submodules to match what the superproject expects");
  submodule_update_command.add_argument("--init")
    .default_value(false)
    .implicit_value(true);
  submodule_update_command.add_argument("--recursive")
    .default_value(false)
    .implicit_value(true);
  submodule_command.add_subparser(submodule_update_command);

  program.add_subparser(add_command);
  program.add_subparser(commit_command);
  program.add_subparser(catfile_command);
  program.add_subparser(submodule_command);

  try {
    program.parse_args(argc, argv);
  }
  catch (const std::runtime_error& err) {
    std::cerr << err.what() << std::endl;
    std::cerr << program;
    return 1;
  }

  // Use arguments
}
```

```console
foo@bar:/home/dev/$ ./git --help
Usage: git [-h] {add,cat-file,commit,submodule}

Optional arguments:
  -h, --help   	shows help message and exits
  -v, --version	prints version information and exits

Subcommands:
  add           Add file contents to the index
  cat-file      Provide content or type and size information for repository objects
  commit        Record changes to the repository
  submodule     Initialize, update or inspect submodules

foo@bar:/home/dev/$ ./git add --help
Usage: add [-h] files

Add file contents to the index

Positional arguments:
  files        	Files to add content from. Fileglobs (e.g.  *.c) can be given to add all matching files.

Optional arguments:
  -h, --help   	shows help message and exits
  -v, --version	prints version information and exits

foo@bar:/home/dev/$ ./git commit --help
Usage: commit [-h] [--all] [--message VAR]

Record changes to the repository

Optional arguments:
  -h, --help   	shows help message and exits
  -v, --version	prints version information and exits
  -a, --all    	Tell the command to automatically stage files that have been modified and deleted.
  -m, --message	Use the given <msg> as the commit message.

foo@bar:/home/dev/$ ./git submodule --help
Usage: submodule [-h] {update}

Initialize, update or inspect submodules

Optional arguments:
  -h, --help   	shows help message and exits
  -v, --version	prints version information and exits

Subcommands:
  update        Update the registered submodules to match what the superproject expects
```

When a help message is requested from a subparser, only the help for that particular parser will be printed. The help message will not include parent parser or sibling parser messages.

Additionally, every parser has the `.is_subcommand_used("<command_name>")` and `.is_subcommand_used(subparser)` member functions to check if a subcommand was used. 

### Getting Argument and Subparser Instances

```Argument``` and ```ArgumentParser``` instances added to an ```ArgumentParser``` can be retrieved with ```.at<T>()```. The default return type is ```Argument```.

```cpp
argparse::ArgumentParser program("test");

program.add_argument("--dir");
program.at("--dir").default_value(std::string("/home/user"));

program.add_subparser(argparse::ArgumentParser{"walk"});
program.at<argparse::ArgumentParser>("walk").add_argument("depth");
```

### Parse Known Args

Sometimes a program may only parse a few of the command-line arguments, passing the remaining arguments on to another script or program. In these cases, the `parse_known_args()` function can be useful. It works much like `parse_args()` except that it does not produce an error when extra arguments are present. Instead, it returns a list of remaining argument strings.

```cpp
#include <argparse/argparse.hpp>
#include <cassert>

int main(int argc, char *argv[]) {
  argparse::ArgumentParser program("test");
  program.add_argument("--foo").implicit_value(true).default_value(false);
  program.add_argument("bar");

  auto unknown_args =
    program.parse_known_args({"test", "--foo", "--badger", "BAR", "spam"});

  assert(program.get<bool>("--foo") == true);
  assert(program.get<std::string>("bar") == std::string{"BAR"});
  assert((unknown_args == std::vector<std::string>{"--badger", "spam"}));
}
```

### ArgumentParser in bool Context

An `ArgumentParser` is `false` until it (or one of its subparsers) have extracted
known value(s) with `.parse_args` or `.parse_known_args`. When using `.parse_known_args`,
unknown arguments will not make a parser `true`.

### Custom Prefix Characters

Most command-line options will use `-` as the prefix, e.g. `-f/--foo`. Parsers that need to support different or additional prefix characters, e.g. for options like `+f` or `/foo`, may specify them using the `set_prefix_chars()`.

The default prefix character is `-`.

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

### Custom Assignment Characters 

In addition to prefix characters, custom 'assign' characters can be set. This setting is used to allow invocations like `./test --foo=Foo /B:Bar`.

The default assign character is `=`.

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

## Further Examples

### Construct a JSON object from a filename argument

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

### Positional Arguments with Compound Toggle Arguments

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

### Restricting the set of values for an argument

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

## Using `option=value` syntax

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
