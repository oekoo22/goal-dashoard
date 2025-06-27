#!/usr/bin/env python3
"""
Test script for the Student Goal Dashboard core functionality.
This tests all components without GUI dependencies.
"""

import os
import sys
from datetime import date


def test_models():
    """Test the core data models."""
    print("Testing core models...")
    
    from models import Studiengang, Semester, Modul, Pruefungsleistung
    
    # Test Pruefungsleistung
    exam = Pruefungsleistung(2.3, date.today(), "bestanden")
    assert exam.ist_bestanden() == True
    assert exam.note == 2.3
    
    # Test Modul
    module = Modul("Test Module", 5, exam)
    assert module.ist_bestanden() == True
    assert module.get_note() == 2.3
    assert module.ects == 5
    
    # Test Semester
    semester = Semester(1, 30, [module])
    assert semester.berechne_ects() == 5
    assert semester.get_durchschnittsnote() == 2.3
    
    # Test Studiengang
    program = Studiengang("Test Program", 180, [semester])
    assert program.get_erreichte_ects() == 5
    assert abs(program.berechne_gesamtfortschritt() - 2.78) < 0.1  # approximately 2.78%
    assert abs(program.berechne_notenschnitt() - 2.3) < 0.01
    
    print("✅ Core models tests passed!")


def test_sample_data():
    """Test sample data creation."""
    print("Testing sample data creation...")
    
    from data import create_sample_data
    
    studiengang = create_sample_data()
    
    # Verify basic structure
    assert studiengang.name == "Informatik Bachelor"
    assert studiengang.ects_gesamt == 180
    assert len(studiengang.semester) == 6
    
    # Verify progress calculation
    progress = studiengang.berechne_gesamtfortschritt()
    assert 40 <= progress <= 45  # Should be around 41.7%
    
    # Verify current semester detection
    current_sem = studiengang.get_aktuelles_semester()
    assert current_sem is not None
    assert current_sem.nummer == 3
    
    print("✅ Sample data tests passed!")


def test_json_persistence():
    """Test JSON serialization and persistence."""
    print("Testing JSON persistence...")
    
    from data import create_sample_data
    from models import Studiengang
    
    # Create and save data
    original = create_sample_data()
    test_file = "test_persistence.json"
    
    try:
        original.save_to_file(test_file)
        
        # Load data back
        loaded = Studiengang.load_from_file(test_file)
        
        # Verify data integrity
        assert loaded.name == original.name
        assert loaded.ects_gesamt == original.ects_gesamt
        assert len(loaded.semester) == len(original.semester)
        assert abs(loaded.berechne_gesamtfortschritt() - original.berechne_gesamtfortschritt()) < 0.01
        assert abs(loaded.berechne_notenschnitt() - original.berechne_notenschnitt()) < 0.01
        
    finally:
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)
    
    print("✅ JSON persistence tests passed!")


def test_business_logic():
    """Test business logic and edge cases."""
    print("Testing business logic...")
    
    from models import Studiengang, Semester, Modul, Pruefungsleistung
    from datetime import date
    
    # Test failed exam
    failed_exam = Pruefungsleistung(5.0, date.today(), "nicht bestanden")
    assert failed_exam.ist_bestanden() == False
    
    failed_module = Modul("Failed Module", 5, failed_exam)
    assert failed_module.ist_bestanden() == False
    
    # Test semester with mixed results
    passed_exam = Pruefungsleistung(2.0, date.today(), "bestanden")
    passed_module = Modul("Passed Module", 5, passed_exam)
    
    mixed_semester = Semester(1, 30, [passed_module, failed_module])
    assert mixed_semester.berechne_ects() == 5  # Only passed module
    assert mixed_semester.ist_abgeschlossen() == False  # Not all modules passed
    
    # Test empty semester
    empty_semester = Semester(2, 30, [])
    assert empty_semester.berechne_ects() == 0
    assert empty_semester.ist_abgeschlossen() == False
    assert empty_semester.get_durchschnittsnote() is None
    
    print("✅ Business logic tests passed!")


def main():
    """Run all tests."""
    print("🎓 Student Goal Dashboard - Functionality Tests")
    print("=" * 50)
    
    try:
        test_models()
        test_sample_data()
        test_json_persistence()
        test_business_logic()
        
        print("\n🎉 All tests passed successfully!")
        print("\nCore functionality is working correctly.")
        print("To run the GUI, install dependencies with:")
        print("  pip install -r requirements.txt")
        print("Then run:")
        print("  python main.py")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()