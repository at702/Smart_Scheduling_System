-- Patients Table
CREATE TABLE patients (
    patient_id NUMBER,
    name VARCHAR2(50) NOT NULL,
    date_of_birth DATE,
    CONSTRAINT pk_patients PRIMARY KEY (patient_id)
);

-- Doctors Table
CREATE TABLE doctors (
    doctor_id NUMBER,
    name VARCHAR2(50) NOT NULL,
    CONSTRAINT pk_doctors PRIMARY KEY (doctor_id)
);

-- Appointments Table
CREATE TABLE appointments (
    appointment_id NUMBER,
    patient_id NUMBER,
    doctor_id NUMBER,
    scheduled_time TIMESTAMP,
    check_in_time TIMESTAMP,
    seen_time TIMESTAMP,
    CONSTRAINT pk_appointments PRIMARY KEY (appointment_id),
    CONSTRAINT fk_appointments_patients FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    CONSTRAINT fk_appointments_doctors FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
);




 


CREATE TABLE appointments (
    appointment_id NUMBER,
    patient_id NUMBER,
    doctor_id NUMBER,
    scheduled_time TIMESTAMP,
    check_in_time TIMESTAMP,
    seen_time TIMESTAMP,
    CONSTRAINT pk_appointments PRIMARY KEY (appointment_id),
    CONSTRAINT fk_patients FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    CONSTRAINT fk_doctors FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
)
