# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
message ="Hello"
print(message)

message =message +" World"
print(message)

#===basic data types====
#integer(number)
counter = 2
print(counter)

#floating-point(number)
weight_sum = 10.5
print(weight_sum)

#strings (text)
message = "Future collars"
print(message)

message2 = '''
line1
line2
line3
'''
print(message2)

#boolean value - True/False
always_true = True
print(always_true)

always_false = False
print(always_false)

#none - Nothing
nothing_here = None
print(nothing_here)

#====math operators=====
a = 2
b = 3
print(a + b)
print(a - b)
print(a * b)
print(a / b)
print(b % a) #reminder from divide
print(a**b) #to the power of

#====logical operators====
print(a==b) #equals
print(a!=b) #different
print(a<b)
print(a<=b)
print(a>=b)

#======AND OR NOT operator====
#and both are true
print(False and False)
print(False and True)
print(True and False)
print(True and True)

#or at least one is true
print(False or False)
print(False or True)
print(True or False)
print(True or True)

#not negation
print(not True)
print(not False)

#======variables in boolen context====
print()
print()
print(bool(-1))#true
print(bool(0)) #false
print(bool(0.0))#false
print(bool(''))


#=====checking variable type====
a = "text"
print(type(a)) #check varyable type

print(type(a) is str)
print(type(a) is int)
print(type(a) is not int)

print(1 + 2) #add like number
print("1"+ "2") #concatenating the strings

print(int("1") + int("2")) #chnage type string to ing

print(str(1) + str(2)) #change type int to string

print(bool(-1))
print(bool(0))
print(bool(1))

message = "new message"
print(message)

message = 2
print(message)





