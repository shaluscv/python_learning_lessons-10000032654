from src.models.specialization import Specialization


class OperationManager:
    def __init__(self):
        self.specs = []

    def options(self):
        print("RK Hospitals")
        choices = [
            "1) Add a new Patient",
            "2) Print all patients",
            "3) Remove a patient by ID",
            "4) Get Next Patient",
            "5) Exit",
            "6) Search patients",
        ]
        print("\n".join(choices))
        while True:
            try:
                return int(input("Enter your Choice: "))
            except ValueError:
                print("Please enter a numeric choice")

    def search_patients(self, query, search_by="id"):
        """Return (specialization, patient) pairs from current queues."""
        if search_by not in ("id", "name"):
            raise ValueError("Search by 'id' or 'name'")
        query = query.strip().casefold()
        if not query:
            return []
        matches = []
        for specialization in self.specs:
            for patient in specialization.patient_data_list:
                if search_by == "id":
                    matched = patient.patient_id == query
                else:
                    matched = query in patient.name.casefold()
                if matched:
                    matches.append((specialization, patient))
        return matches

    def run(self):
        while True:
            choice = self.options()
            if choice == 1:
                print("ADD NEW PATIENT")
                spec_name = input("Enter Specialization : ").strip()
                patient_name = input("Enter Patient Name : ").strip()
                try:
                    patient_status = int(input("Enter Patient Status : ").strip())
                except ValueError:
                    print("Patient status must be a number")
                    continue

                spec_found = next(
                    (spec for spec in self.specs
                     if spec.name == f"{spec_name} Specialization"),
                    None,
                )
                new_specialization = spec_found is None
                if new_specialization:
                    spec_found = Specialization(spec_name)
                patient = spec_found.add_new_patient(patient_name, patient_status)
                if patient is not None:
                    if new_specialization:
                        self.specs.append(spec_found)
                    print(f"Patient added. ID : {patient.patient_id}")

            elif choice == 2:
                for specialization in self.specs:
                    print(f"Specialization : {specialization.name}")
                    specialization.print_patients()
                    print("-" * 82)

            elif choice == 3:
                patient_id = input("Enter Patient ID : ").strip()
                matches = self.search_patients(patient_id)
                if matches:
                    specialization, patient = matches[0]
                    specialization.remove_patient(patient.patient_id)
                else:
                    print("No such patient")

            elif choice == 4:
                spec_name = input("Enter Specialization name : ").strip()
                for specialization in self.specs:
                    if specialization.name == f"{spec_name} Specialization":
                        specialization.get_next_patient()
                        break
                else:
                    print("There is no such specialization")

            elif choice == 5:
                break

            elif choice == 6:
                search_mode = input("Search by (id/name): ").strip().casefold()
                if search_mode not in ("id", "name"):
                    print("Invalid search mode. Choose id or name")
                    continue
                query = input("Enter search query: ")
                if not query.strip():
                    print("Search query cannot be empty")
                    continue
                matches = self.search_patients(query, search_mode)
                if not matches:
                    print("No matching patients")
                for specialization, patient in matches:
                    status = specialization.format_patient_status(patient.status)
                    print(
                        f"ID : {patient.patient_id} ;Patient : {patient.name} ;"
                        f"Status : {status} ;Specialization : {specialization.name}"
                    )
            else:
                print("Invalid option. Please select a valid one")
