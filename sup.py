def __init__(self, parent_attr):
 self.parent_attr = parent_attr
def parent_method(self):
 print("Calling parent method")

class ChildClass():
 def __init__(self, parent_attr, child_attr):
  super().__init__(parent_attr)  # Call the initializer of the parent class
  self.child_attr = child_attr

 def child_method(self):
  print("Calling child method")
  print(f"Parent attribute: {self.parent_attr}")
  print(f"Child attribute: {self.child_attr}")



