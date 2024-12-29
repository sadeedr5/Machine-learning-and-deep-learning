import math

SOURCE_NAMES = [
  "HOUSEHOLD",
  "SME",
  "INDUSTRIAL",
  "GO_NGO",
  "TRANSPORT",
]

GARBAGE_SOURCE_HOUSEHOLD = 0
GARBAGE_SOURCE_SME = 1
GARBAGE_SOURCE_INDUSTRIAL = 2
GARBAGE_SOURCE_GO_NGO = 3
GARBAGE_SOURCE_TRANSPORT = 4

GARBAGE_TYPE_BIO = 0
GARBAGE_TYPE_RECYCLE = 1
GARBAGE_TYPE_NON_RECYCLE = 2

MSG_TYPE_INFO = "INFO"
MSG_TYPE_WARNING = "WARNING"
MSG_TYPE_ERROR = "ERROR"

class Billing_Info:
  bill_bio = 0
  bill_recycle = 2
  bill_non_recycle = 5
  
  def __init__(self):
    self.billing_catalog = list()
  
  def calculate_bill(self, user, garbages):
    amount = garbages["bio"] * self.bill_bio + garbages["recycle"] * self.bill_recycle + garbages["non_recycle"] * self.bill_non_recycle
    
    user.total_bill += amount
    
    # search user in catelog
    user_index = -1
    for i, bill in enumerate(self.billing_catalog):
      if bill.id == user.id:
        user_index = i
        break

    # update billing catelog
    if user_index == -1:
      self.billing_catalog.append(user) # new user added to catalog
    else:
      self.billing_catalog[user_index] = user
    
class Bin:
  def __init__(self, capacity=math.inf, garbages = {"bio": 0,"recycle": 0,"non_recycle": 0}):
    self.total_count = 0
    self.message = ""
    self.capacity = capacity
    self.garbages = garbages
    
  def send_garbages(self, bin, garbages):
    garbage_count = 0
    for key, value in garbages.items():
      garbage_count += garbages[key]

    if garbage_count == 0:
      self.message = f"[{MSG_TYPE_ERROR}] You cannot send 0 garbages. Add more garbages!"
      return False
    elif bin.receive_garbages(self, garbages, garbage_count):
      self.total_count = 0
      for key, value in garbages.items():
        self.garbages[key] = 0  
      
      self.message = f"[{MSG_TYPE_INFO}] Successfully sent garbages."
      return True
    else:
      self.message = f"[{MSG_TYPE_ERROR}] Could not send garbages. Out of capacity"
      return False
  
  def receive_garbages(self, garbages, garbage_count):
    if (self.total_count + garbage_count) <= self.capacity:
      # add garbages to bin_sources
      for key, value in garbages.items():
        self.garbages[key] += garbages[key]

      self.total_count += garbage_count
      return True
    else:
      self.message = f"[{MSG_TYPE_ERROR}] Could not add garbages. Out of capacity."
      return False
  
  def send_message(self, obj, message):
    obj.receive_message(message)
  
  def output_garbages(self, bin_name):
    output = f"[{MSG_TYPE_INFO}] ({bin_name}) [" 
    for key, value in self.garbages.items():
      output += f"{key}: {self.garbages[key]}, "
    output += "]"
    
    print(output)
  
  def receive_message(self, message):
    self.message = message
    print(self.message)

class Source_Bin(Bin):
  def __init__(self, capacity, type):
    super().__init__(capacity)
    self.type = type
  
  def output_garbages(self):
    bin_name = f"SOURCE BIN: {SOURCE_NAMES[self.type]}"
    super().output_garbages(bin_name)
  
  def send_garbages(self, bin):
    self.output_garbages()
    return super().send_garbages(bin, self.garbages)
    
  def receive_garbages(self, obj, garbages, garbage_count):
    if super().receive_garbages(garbages, garbage_count):
      self.message = f"[{MSG_TYPE_INFO}] (SOURCE BIN: {SOURCE_NAMES[self.type]}) Reduce garbage production"
      self.send_message(obj, self.message)
      return True
    else:
      return False
    
  def receive_message(self, user, message):
    super().receive_message(message)
    message = "Reduce garbage production"
    self.send_message(user, message)
  
class GMP_Bin(Bin):
  def __init__(self, capacity):
    super().__init__(capacity)
    
  def send_garbages(self, bin_1, bin_2):
    self.output_garbages()
    b_garbages = {"bio": self.garbages["bio"]}
    nb_garbages = {"recycle": self.garbages["recycle"], "non_recycle": self.garbages["non_recycle"]}
    if super().send_garbages(bin_1, b_garbages) & super().send_garbages(bin_2, nb_garbages):
      return True
    else:
      return False
    
  def receive_garbages(self, obj, garbages, garbage_count):
    if super().receive_garbages(garbages, garbage_count):
      self.message = f"[{MSG_TYPE_INFO}] (GMP BIN) Warning from GMP-bin"
      # self.send_message(obj, self.message)
      return True
    else:
      return False
    
  def output_garbages(self, bin_name):
    bin_name = "GMP BIN"
    super().output_garbages(bin_name)
      
class B_Bin(Bin):
  pass

class NB_Bin(Bin):
  def __init__(self, capacity):
    super().__init__(capacity)

class R_Bin(Bin):
  pass

class NR_Bin(Bin):
  pass

class User:
  num_of_users = 0

  def __init__(self, name, address, type):
    User.num_of_users += 1

    self.id = User.num_of_users
    self.name = name
    self.address = address
    self.type = type
    self.message = ""
    self.total_bill = 0
  
  def send_garbages(self, bin_sources, garbages, bill_info):
    garbage_count = 0    
    for key, value in garbages.items():
      garbage_count += garbages[key]
          
    if garbage_count == 0:
      self.message = f"[{MSG_TYPE_ERROR}] You cannot send 0 garbages. Add more garbages!"
    elif bin_sources[self.type].receive_garbages(self, garbages, garbage_count):
      # update bill_info
      bill_info.calculate_bill(self, garbages)
      self.message = f"[{MSG_TYPE_INFO}] Successfully sent garbages to {SOURCE_NAMES[self.type]} source bin."
      print(bin_sources[self.type].__dict__)
      return True
    else:
      self.message = f"[{MSG_TYPE_ERROR}] Could not send garbages to {SOURCE_NAMES[self.type]} source bin."
      return False

  def check_bill(self):
    print(f"[{MSG_TYPE_INFO}] Your total bill = {self.total_bill}")
  
  def receive_message(self, message):
    self.message = message
    print(self.message)

# bill setup
bill_info = Billing_Info()

# bin setup
bin_gmp = GMP_Bin(30)
bin_b = B_Bin()
bin_nb = NB_Bin(20)
bin_r = R_Bin()
bin_nr = NR_Bin()

bin_sources = list()
bin_sources.append(Source_Bin(30, GARBAGE_SOURCE_HOUSEHOLD))
bin_sources.append(Source_Bin(40, GARBAGE_SOURCE_SME))
bin_sources.append(Source_Bin(50, GARBAGE_SOURCE_INDUSTRIAL))
bin_sources.append(Source_Bin(50, GARBAGE_SOURCE_GO_NGO))
bin_sources.append(Source_Bin(40, GARBAGE_SOURCE_TRANSPORT))

# users
users = list()
users.append(User("Humam", "Banasree", GARBAGE_SOURCE_HOUSEHOLD))
users.append(User("Sadeed", "South Banasree", GARBAGE_SOURCE_HOUSEHOLD))
users.append(User("Zulkar", "Banasree", GARBAGE_SOURCE_HOUSEHOLD))
users.append(User("Abrar", "Banasree", GARBAGE_SOURCE_SME))
users.append(User("Rafi", "Banasree", GARBAGE_SOURCE_SME))

garbages = {
  "bio": 1,
  "recycle": 2,
  "non_recycle": 3
}

for user in users:
  user.send_garbages(bin_sources, garbages, bill_info)
  # print(user.message)
  # user.check_bill()
  print(user.__dict__)
  
# for source in bin_sources:
#   source.send_garbages(bin_gmp)
#   print(source.message)

# print("[DEBUG] gmp bin")
# print(bin_gmp.__dict__)