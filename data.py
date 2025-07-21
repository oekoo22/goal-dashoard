from datetime import date
from models import Studiengang, Semester, Modul, Pruefungsleistung


def create_sample_data() -> Studiengang:
    """
    Create sample student data that matches the dashboard sketch.
    """
    # Create study program
    studiengang = Studiengang("Informatik Bachelor", 180)
    
    # Semester 1 (completed)
    semester1 = Semester(1, 30)
    semester1.add_modul(Modul("Grundlagen Programmierung", 5, 
                             Pruefungsleistung(2.0, date(2023, 2, 15))))
    semester1.add_modul(Modul("Mathematik I", 5, 
                             Pruefungsleistung(2.3, date(2023, 2, 20))))
    semester1.add_modul(Modul("Theoretische Informatik", 5, 
                             Pruefungsleistung(1.7, date(2023, 2, 25))))
    semester1.add_modul(Modul("Betriebssysteme", 5, 
                             Pruefungsleistung(2.0, date(2023, 3, 1))))
    
    # Semester 2 (completed)
    semester2 = Semester(2, 30)
    semester2.add_modul(Modul("Datenstrukturen", 5, 
                             Pruefungsleistung(2.3, date(2023, 7, 15))))
    semester2.add_modul(Modul("Mathematik II", 5, 
                             Pruefungsleistung(2.7, date(2023, 7, 20))))
    semester2.add_modul(Modul("Softwareengineering", 5, 
                             Pruefungsleistung(1.7, date(2023, 7, 25))))
    semester2.add_modul(Modul("Rechnernetze", 5, 
                             Pruefungsleistung(2.0, date(2023, 8, 1))))
    
    # Semester 3 (current - partially completed)
    semester3 = Semester(3, 30)
    semester3.add_modul(Modul("Datenbanken", 5, 
                             Pruefungsleistung(2.0, date(2024, 2, 15))))
    semester3.add_modul(Modul("Web-Entwicklung", 5, 
                             Pruefungsleistung(1.7, date(2024, 2, 20))))
    # Current modules without grades yet
    semester3.add_modul(Modul("Algorithmen", 5))  # In progress
    semester3.add_modul(Modul("Projektmanagement", 5))  # Registered
    
    # Future semesters (planned)
    semester4 = Semester(4, 30)
    semester4.add_modul(Modul("Machine Learning", 5))
    semester4.add_modul(Modul("IT-Sicherheit", 5))
    semester4.add_modul(Modul("Mobile Entwicklung", 5))
    semester4.add_modul(Modul("Wahlpflichtmodul 1", 5))
    
    semester5 = Semester(5, 30)
    semester5.add_modul(Modul("Verteilte Systeme", 5))
    semester5.add_modul(Modul("Wahlpflichtmodul 2", 5))
    semester5.add_modul(Modul("Wahlpflichtmodul 3", 5))
    semester5.add_modul(Modul("Seminar", 5))
    
    semester6 = Semester(6, 30)
    semester6.add_modul(Modul("Praktikum", 10))
    semester6.add_modul(Modul("Bachelorarbeit", 10))
    semester6.add_modul(Modul("Kolloquium", 5))
    
    # Add all semesters to study program
    studiengang.add_semester(semester1)
    studiengang.add_semester(semester2)
    studiengang.add_semester(semester3)
    studiengang.add_semester(semester4)
    studiengang.add_semester(semester5)
    studiengang.add_semester(semester6)
    
    return studiengang


def save_sample_data(filename: str = "student_data.json") -> None:
    """
    Create and save sample data to JSON file.
    """
    studiengang = create_sample_data()
    studiengang.save_to_file(filename)
    print(f"Sample data saved to {filename}")


if __name__ == "__main__":
    save_sample_data()