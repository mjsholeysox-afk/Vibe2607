# 파이썬연습.py

#변수를 초기화
x=100
y=200
strA="문자열을 지정"

#함수 호출
print(dir())
print(len(strA))

#함수를 하나 정의
def times(a,b):
    return a*b
#함수 호출
result=times(3,4)
print(result)

#person클래스를 정의하는데 id, name변수가 있고, 
#이 값을 출력하는 printperson()함수를 정의한다.
class person:
    def __init__(self, id, name):
        self.id=id
        self.name=name
    def printperson(self):
        print("id:", self.id)
        print("name:", self.name)

#인스턴트를 생성
person1=person(1, "홍길동")
#인스턴트의 함수를 호출
p1.printperson()




