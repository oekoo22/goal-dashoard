from datetime import date
from typing import List, Optional
import json


class Pruefungsleistung:
    """
    Represents an exam/assessment performance for a module.
    """
    def __init__(self, note: float, datum: date, status: str = "bestanden"):
        self.note = note
        self.datum = datum
        self.status = status
    
    def ist_bestanden(self) -> bool:
        """Check if the exam is passed (grade <= 4.0 in German system)."""
        return self.note <= 4.0 and self.status == "bestanden"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "note": self.note,
            "datum": self.datum.isoformat(),
            "status": self.status
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Pruefungsleistung':
        """Create instance from dictionary."""
        return cls(
            note=data["note"],
            datum=date.fromisoformat(data["datum"]),
            status=data["status"]
        )


class Modul:
    """
    Represents a study module with ECTS credits and optional exam performance.
    """
    def __init__(self, name: str, ects: int, pruefungsleistung: Optional[Pruefungsleistung] = None):
        self.name = name
        self.ects = ects
        self.pruefungsleistung = pruefungsleistung
    
    def ist_bestanden(self) -> bool:
        """Check if the module is passed."""
        return self.pruefungsleistung is not None and self.pruefungsleistung.ist_bestanden()
    
    def get_note(self) -> Optional[float]:
        """Get the grade if available."""
        return self.pruefungsleistung.note if self.pruefungsleistung else None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "ects": self.ects,
            "pruefungsleistung": self.pruefungsleistung.to_dict() if self.pruefungsleistung else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Modul':
        """Create instance from dictionary."""
        pruefungsleistung = None
        if data.get("pruefungsleistung"):
            pruefungsleistung = Pruefungsleistung.from_dict(data["pruefungsleistung"])
        
        return cls(
            name=data["name"],
            ects=data["ects"],
            pruefungsleistung=pruefungsleistung
        )


class Semester:
    """
    Represents a study semester containing multiple modules.
    """
    def __init__(self, nummer: int, geplante_ects: int, module: List[Modul] = None):
        self.nummer = nummer
        self.geplante_ects = geplante_ects
        self.module = module or []
    
    def ist_abgeschlossen(self) -> bool:
        """Check if the semester is completed (all modules passed)."""
        if not self.module:
            return False
        return all(modul.ist_bestanden() for modul in self.module)
    
    def berechne_ects(self) -> int:
        """Calculate actual ECTS earned in this semester."""
        return sum(modul.ects for modul in self.module if modul.ist_bestanden())
    
    def get_durchschnittsnote(self) -> Optional[float]:
        """Calculate average grade for the semester."""
        bestandene_module = [modul for modul in self.module if modul.ist_bestanden()]
        if not bestandene_module:
            return None
        
        weighted_sum = sum(modul.get_note() * modul.ects for modul in bestandene_module)
        total_ects = sum(modul.ects for modul in bestandene_module)
        
        return weighted_sum / total_ects if total_ects > 0 else None
    
    def add_modul(self, modul: Modul) -> None:
        """Add a module to this semester."""
        self.module.append(modul)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "nummer": self.nummer,
            "geplante_ects": self.geplante_ects,
            "module": [modul.to_dict() for modul in self.module]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Semester':
        """Create instance from dictionary."""
        module = [Modul.from_dict(modul_data) for modul_data in data.get("module", [])]
        return cls(
            nummer=data["nummer"],
            geplante_ects=data["geplante_ects"],
            module=module
        )


class Studiengang:
    """
    Represents a complete study program containing multiple semesters.
    """
    def __init__(self, name: str, ects_gesamt: int, semester: List[Semester] = None):
        self.name = name
        self.ects_gesamt = ects_gesamt
        self.semester = semester or []
    
    def berechne_gesamtfortschritt(self) -> float:
        """Calculate overall study progress as percentage."""
        erreichte_ects = sum(semester.berechne_ects() for semester in self.semester)
        return (erreichte_ects / self.ects_gesamt) * 100 if self.ects_gesamt > 0 else 0.0
    
    def berechne_notenschnitt(self) -> float:
        """Calculate overall GPA across all semesters."""
        alle_module = []
        for semester in self.semester:
            alle_module.extend([modul for modul in semester.module if modul.ist_bestanden()])
        
        if not alle_module:
            return 0.0
        
        weighted_sum = sum(modul.get_note() * modul.ects for modul in alle_module)
        total_ects = sum(modul.ects for modul in alle_module)
        
        return weighted_sum / total_ects if total_ects > 0 else 0.0
    
    def get_erreichte_ects(self) -> int:
        """Get total ECTS credits earned."""
        return sum(semester.berechne_ects() for semester in self.semester)
    
    def get_aktuelles_semester(self) -> Optional[Semester]:
        """Get the current semester (first incomplete semester)."""
        for semester in self.semester:
            if not semester.ist_abgeschlossen():
                return semester
        return None
    
    def add_semester(self, semester: Semester) -> None:
        """Add a semester to the study program."""
        self.semester.append(semester)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "ects_gesamt": self.ects_gesamt,
            "semester": [semester.to_dict() for semester in self.semester]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Studiengang':
        """Create instance from dictionary."""
        semester = [Semester.from_dict(sem_data) for sem_data in data.get("semester", [])]
        return cls(
            name=data["name"],
            ects_gesamt=data["ects_gesamt"],
            semester=semester
        )
    
    def save_to_file(self, filename: str) -> None:
        """Save study program to JSON file."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load_from_file(cls, filename: str) -> 'Studiengang':
        """Load study program from JSON file."""
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)