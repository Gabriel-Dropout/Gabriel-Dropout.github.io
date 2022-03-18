#octo language

#실제 처리 과정에서 변수와 함수를 구분하지 말 것(변수는 사실상 상수함수와 다르지 않으므로)

class octo_lang:
    def __init__(self, code):
        self.code = code

        #주석 처리 규칙 
        self.ignore_keyword = {
            '//' : '\n', 
            '/*' : '*/'
        }
        #키워드
        self.keyword = [
            {
                '+' : ['operator', '+'], 
                '-' : ['operator', '-'], 
                '*' : ['operator', '*'], 
                '/' : ['operator', '/'], 
                '%' : ['operator', '%'], 
                '^' : ['operator', '^'], 
                '(' : ['indicator', '('],  
                ')' : ['indicator', ')'], 
                ':' : ['indicator', ':'], 
                ',' : ['indicator', ','], 
                '\\n' : ['newline_indicator', '\\n'], 
                '\'' : ['indicator', '\''], 
                'int' : ['type_indicator', 'int'], 
                '==' : ['comparison_operator', '=='], 
                '!=' : ['comparison_operator', '!='], 
                '>' : ['comparison_operator', '>'], 
                '<' : ['comparison_operator', '<'], 
                '>=' : ['comparison_operator', '>='], 
                '<=' : ['comparison_operator', '<=']
            }, 
            {
                'if' : ['control_statement', 'if'], 
                'elif' : ['control_statement', 'elif'], 
                'else' : ['control_statement', 'else'], 
                'func' : ['function_definition', 'func'], 
                'main' : ['main_function', 'main'], 
                'return' : ['function_return', 'return'], 
                'int' : ['builtin_function', 'int'], 
                'gets' : ['builtin_function', 'gets'], 
                'puts' : ['builtinfunction', 'puts'], 
                'and' : ['logical_operator', 'and'], 
                'or' : ['logical_operator', 'or'], 
                'not' : ['logical_operator', 'not'], 
                '=' : ['constant_definition', '=']
            }
        ]
        #변수명 및 함수명 작명 규칙, 인덱스 0는 머리글자, 인덱스 1은 이후 글자의 규칙이다(알파벳과 언더바로 시작, 뒤로는 숫자까지 이어질 수 있음)
        self.naming_rules = [
                list(map(chr, range(65, 91))) + list(map(chr, range(97, 123))) + ['_'],
            list(map(chr, range(48, 58))) + list(map(chr, range(65, 91))) + list(map(chr, range(97, 123))) + ['_']
            ]

        self.token = []

    def disassemble(self): #현재까지는 주석 처리 및 키워드 추출만 구현됨, 식별자 추출은 곧 구현 예정
        chr_pointer = 0 #코드 포인터
        keyword_match = False #키워드가 인식되었을 경우 True로 설정
        word = ''
        while chr_pointer < len(self.code):
            #주석 처리
            for k in self.ignore_keyword.keys(): #주석 처리 규칙에서 주석 처리 시작 문자열을 가지고 옴
                if chr_pointer < len(self.code) - (len(k) - 1):
                    if self.code[chr_pointer : chr_pointer + len(k)] == k:
                        while chr_pointer < len(self.code):
                            #현재 코드 포인터가 가리키는 위치에서 앞쪽으로 주석 처리 종료 문자열이 등장하는지 검사
                            if chr_pointer >= len(self.ignore_keyword[k]) - 1:
                                #주석 처리 종료 문자열을 만났을 경우
                                if self.code[chr_pointer - (len(self.ignore_keyword[k]) - 1) : chr_pointer + 1] == self.ignore_keyword[k]:
                                    chr_pointer += 1
                                    break
                            chr_pointer += 1
            #부분적으로 글자가 겹치는 키워드들이 있어 처리 순서를 나눔
            for process_level in range(0, len(self.keyword)):
                for k in self.keyword[process_level].keys():
                    if chr_pointer < len(self.code) - (len(k) - 1):
                        if self.code[chr_pointer : chr_pointer + len(k)] == k:
                            #인식된 키워드가 식별자(변수명 및 함수명) 작명 규칙을 만족하는지 확인하고 그렇다면 키워드를 추출하지 않음
                            #변수명으로 쓴 'funcl'에서 키워드 'func'를 추출해 버리는 오류 방지 
                            if chr_pointer < len(self.code) - (len(k) - 1) - 1:
                                #머리글자부터 규칙에 해당될 경우
                                if k[0] not in self.naming_rules[0]:
                                    keyword_match = True
                                #이후 글자가 규칙에 해당될 경우
                                else:
                                    if self.code[chr_pointer + len(k)] not in self.naming_rules[1]:
                                        keyword_match = True
                            else:
                                keyword_match = True
                            if keyword_match:
                                self.token.append(self.keyword[process_level][k])
                                chr_pointer += (len(k) - 1)
                                break
                if keyword_match:
                    keyword_match = False
                    break
            chr_pointer += 1

    #추출된 토큰을 분석
    def parse(self):
        pass

with open('prime.octo', 'r', encoding = 'utf-8') as f:
    code = f.read()

octo = octo_lang(code)
octo.disassemble()
print(octo.token)