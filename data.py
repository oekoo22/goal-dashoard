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
    semester1.add_modul(Modul("Grundlagen Programmierung", 8, 
                             Pruefungsleistung(2.0, date(2023, 2, 15))))
    semester1.add_modul(Modul("Mathematik I", 8, 
                             Pruefungsleistung(2.3, date(2023, 2, 20))))
    semester1.add_modul(Modul("Theoretische Informatik", 6, 
                             Pruefungsleistung(1.7, date(2023, 2, 25))))
    semester1.add_modul(Modul("Betriebssysteme", 8, 
                             Pruefungsleistung(2.0, date(2023, 3, 1))))
    
    # Semester 2 (completed)
    semester2 = Semester(2, 30)
    semester2.add_modul(Modul("Datenstrukturen", 8, 
                             Pruefungsleistung(2.3, date(2023, 7, 15))))
    semester2.add_modul(Modul("Mathematik II", 8, 
                             Pruefungsleistung(2.7, date(2023, 7, 20))))
    semester2.add_modul(Modul("Softwareengineering", 6, 
                             Pruefungsleistung(1.7, date(2023, 7, 25))))
    semester2.add_modul(Modul("Rechnernetze", 8, 
                             Pruefungsleistung(2.0, date(2023, 8, 1))))
    
    # Semester 3 (current - partially completed)
    semester3 = Semester(3, 30)
    semester3.add_modul(Modul("Datenbanken", 8, 
                             Pruefungsleistung(2.0, date(2024, 2, 15))))
    semester3.add_modul(Modul("Web-Entwicklung", 7, 
                             Pruefungsleistung(1.7, date(2024, 2, 20))))
    # Current modules without grades yet
    semester3.add_modul(Modul("Algorithmen", 8))  # In progress
    semester3.add_modul(Modul("Projektmanagement", 7))  # Registered
    
    # Future semesters (planned)
    semester4 = Semester(4, 30)
    semester4.add_modul(Modul("Machine Learning", 8))
    semester4.add_modul(Modul("IT-Sicherheit", 8))
    semester4.add_modul(Modul("Mobile Entwicklung", 6))
    semester4.add_modul(Modul("Wahlpflichtmodul 1", 8))
    
    semester5 = Semester(5, 30)
    semester5.add_modul(Modul("Verteilte Systeme", 8))
    semester5.add_modul(Modul("Wahlpflichtmodul 2", 8))
    semester5.add_modul(Modul("Wahlpflichtmodul 3", 8))
    semester5.add_modul(Modul("Seminar", 6))
    
    semester6 = Semester(6, 30)
    semester6.add_modul(Modul("Praktikum", 12))
    semester6.add_modul(Modul("Bachelorarbeit", 12))
    semester6.add_modul(Modul("Kolloquium", 6))
    
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