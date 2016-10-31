# if variable is passed, variable changes is not propagated out of scope
# def foo(test):
    # test=1
    # #return a
    
# test=0
# print(test)
# test=foo(5)
# print(test)

# if array is passed, the data is changed
# def foo(test):
    # test[0]=5
    
# def main():
    # test =["a"]*5
    # foo(test)
    # print(test[0])
    
# main()

# if object is passed, the object is changed
class Class1:
    def __init__(self):
        self.data=6
        
    def setData(self,d):
        self.data=d

def foo(class1):
    class1.setData(10)
    
def main():
    class1=Class1()
    foo(class1)
    print(class1.data)
    
main()