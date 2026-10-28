from uuid import uuid4


class Patient:
    def __init__(self, name, status):
        self._patient_id = str(uuid4())
        self.name = name
        self.status = status

    @property
    def patient_id(self):
        return self._patient_id
