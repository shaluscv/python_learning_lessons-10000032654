
from src.user_data.patient import Patient


class Specialization:


	MAX_CAPACITY = 10

	PATIENT_STATUS=[0,1,2]
	def __init__(self,name):
		self.name=f"{name} Specialization"
		self.patient_data_list=[]

	@classmethod
	def acess(cls):
		print(cls.MAX_CAPACITY)

	def add_new_patient(self,patient_name,patient_status):
		if len(self.patient_data_list) >= self.MAX_CAPACITY:
			print("Queue for the specialization is full")
			return

		if patient_status not in self.PATIENT_STATUS:
			print("Invalid")
			return

		new_patient=Patient(patient_name,patient_status)
		self.patient_data_list.append(new_patient)
		return new_patient
		#print(f"Patient Name is {patient_name} | Patient status : {self.format_patient_status(patient_status)}")

	def get_next_patient(self):
		if len(self.patient_data_list)==0:
			print("No patients in this specialization")
			return
		next_patient=self.patient_data_list.pop(0)
		print(f"ID : {next_patient.patient_id} ;Patient : {next_patient.name} ;Status : {next_patient.status} can consult the Doctor now")

	def print_patients(self):
		if len(self.patient_data_list) == 0:
			print(f"No patients in {self.name}")
			return
		for patient in self.patient_data_list:
			print(f"ID : {patient.patient_id} ;Patient : {patient.name} ;Status : {patient.status}")

	def remove_patient(self,patient_id):
		patient_id = patient_id.strip().casefold()
		for patient in self.patient_data_list:
			if patient.patient_id == patient_id:
				self.patient_data_list.remove(patient)
				print(f"Removed patient {patient.patient_id}")
				return True
		print("No such patient")
		return False


	@staticmethod
	def format_patient_status(patient_status):
		if patient_status==0:
			return "normal"
		elif patient_status==1:
			return "Emergency"
		else:
			return "Super Emergency"
