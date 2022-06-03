class person:
    # double underscores makes the variable private to the class
    __height = 0
    __weight = 0

    def get_height(self, ht):
        self.__height = ht

    def __init__(self, logItName, height = 0, weight = 0):
        print("Define all the properties within this.")

        #names
        length = len(logItName)
        if length == 1:
            self.name = logItName(1)
        elif length == 2:
            self.nameIt([logItName(1), logItName(2)])
        elif length == 3:
            self.nameIt([logItName(1), logItName(2)])
            self.age = logItName(3)
        #height, weight
        self.__height = height
        self.__weight = weight

    def nameIt(self, names):
        length = len(names)
        if length == 1:
            self.name = names(1)
            #do regular expression to check for 2 names
        elif length == 2:
            self.first_name = names(1) 
            self.last_name = names(2)
            self.name = names(1) + " " + names(2)


    @staticmethod
    def static_method():
        print("This is a static method")

    def object_method(self):
        print("This is an object method")

    @classmethod
    def class_method(cls):
        print("This accesses the class and not the instance of the class.")

    @classmethod
    def darnell(cls):
        return cls("Darnell Baird")
    @classmethod
    def conrad(cls):
        return cls("Conrad Baird")

    def __repr__(self):
        print("No matter what you call, you will get this same string.")
        str = f"Just kidding, {self.name}"
        return str

    
def police(person):  #police class inherites from person class
    __department = ""

    def __init__(self, name, height, weight, department):
        self.__department = department;
        super(police, self).__init__(name, height, weight)  #'super' accesses the inherited class of the class in the 1st argument
    

    