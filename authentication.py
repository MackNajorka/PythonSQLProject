class Authentication(object):
    def __init__(self, username = ''):
        self.username = username

    def __lower(self):
        lower = any(c.islower() for c in self.username)
        return lower
    
    def __upper(self):
        upper = any(c.isupper() for c in self.username)
        return upper
    
    def __digit(self):
        digit = any(c.isdigit() for c in self.username)
        return digit
    
    def validate(self):
        lower = self.__lower()
        upper = self.__upper()
        digit = self.__digit()
        
        length = len(self.username)
        
        report = lower and upper and digit and length >=6
        
        if report:
            print("Username passed all checks ")
            return True
        
        elif not lower:
            print("Please use at least one lowercase character ")
            return False
        
        elif not upper:
            print("Please use at least one uppercase character ")
            return False
        
        elif not digit:
            print("Please use at least one digit ")
            return False
        
        elif length < 6:
            print("Your username must be at least 6 characters ")
            return False
        else:
            pass

#Test authentiation with this function.
C = Authentication ("Makazar2")
print(C.validate())