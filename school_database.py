"""
School Database Simulator — A CLI-based school management system.
Supports creation and management of students, teachers, and homeroom teachers.
"""


class Student:
    """Represents a student enrolled in a class."""

    def __init__(self, first_name, last_name, class_name):
        self.first_name = first_name
        self.last_name = last_name
        self.class_name = class_name

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"Student: {self.full_name()} | Class: {self.class_name}"


class Teacher:
    """Represents a teacher who teaches a subject across one or more classes."""

    def __init__(self, first_name, last_name, subject, classes):
        self.first_name = first_name
        self.last_name = last_name
        self.subject = subject
        self.classes = classes  # list of class names

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        classes_str = ", ".join(self.classes) if self.classes else "None"
        return f"Teacher: {self.full_name()} | Subject: {self.subject} | Classes: {classes_str}"


class HomeroomTeacher:
    """Represents a homeroom teacher who leads a specific class."""

    def __init__(self, first_name, last_name, class_name):
        self.first_name = first_name
        self.last_name = last_name
        self.class_name = class_name

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"Homeroom Teacher: {self.full_name()} | Class: {self.class_name}"


class SchoolDatabase:
    """Central database managing all students, teachers, and homeroom teachers."""

    def __init__(self):
        self.students = []
        self.teachers = []
        self.homeroom_teachers = []

    # ── Creation Methods ──────────────────────────────────────────────

    def create_student(self):
        """Prompt for and create a new student."""
        first_name = input("  First name: ").strip()
        last_name = input("  Last name: ").strip()
        if not first_name or not last_name:
            print("  [!] First and last name are required.")
            return
        class_name = input("  Class name (e.g. 3C): ").strip()
        if not class_name:
            print("  [!] Class name is required.")
            return

        student = Student(first_name, last_name, class_name)
        self.students.append(student)
        print(f"  ✓ Created: {student}")

    def create_teacher(self):
        """Prompt for and create a new teacher."""
        first_name = input("  First name: ").strip()
        last_name = input("  Last name: ").strip()
        if not first_name or not last_name:
            print("  [!] First and last name are required.")
            return
        subject = input("  Subject: ").strip()
        if not subject:
            print("  [!] Subject is required.")
            return

        classes = []
        print("  Enter class names (one per line, empty line to finish):")
        while True:
            cls = input("    Class: ").strip()
            if cls == "":
                break
            classes.append(cls)

        teacher = Teacher(first_name, last_name, subject, classes)
        self.teachers.append(teacher)
        print(f"  ✓ Created: {teacher}")

    def create_homeroom_teacher(self):
        """Prompt for and create a new homeroom teacher."""
        first_name = input("  First name: ").strip()
        last_name = input("  Last name: ").strip()
        if not first_name or not last_name:
            print("  [!] First and last name are required.")
            return
        class_name = input("  Class they lead (e.g. 3C): ").strip()
        if not class_name:
            print("  [!] Class name is required.")
            return

        homeroom = HomeroomTeacher(first_name, last_name, class_name)
        self.homeroom_teachers.append(homeroom)
        print(f"  ✓ Created: {homeroom}")

    # ── Management Methods ────────────────────────────────────────────

    def manage_class(self):
        """Display all students and the homeroom teacher of a given class."""
        class_name = input("  Enter class name (e.g. 3C): ").strip()
        if not class_name:
            print("  [!] Class name is required.")
            return

        # Find students in this class
        students_in_class = [s for s in self.students if s.class_name == class_name]

        # Find homeroom teacher for this class
        homeroom = None
        for ht in self.homeroom_teachers:
            if ht.class_name == class_name:
                homeroom = ht
                break

        print(f"\n  ── Class: {class_name} ──")

        if homeroom:
            print(f"  Homeroom Teacher: {homeroom.full_name()}")
        else:
            print("  Homeroom Teacher: Not assigned")

        if students_in_class:
            print(f"  Students ({len(students_in_class)}):")
            for s in students_in_class:
                print(f"    - {s.full_name()}")
        else:
            print("  No students enrolled in this class.")

    def manage_student(self):
        """Display all classes a student attends and their teachers."""
        first_name = input("  Student first name: ").strip()
        last_name = input("  Student last name: ").strip()
        if not first_name or not last_name:
            print("  [!] First and last name are required.")
            return

        # Find the student
        student = None
        for s in self.students:
            if s.first_name.lower() == first_name.lower() and s.last_name.lower() == last_name.lower():
                student = s
                break

        if not student:
            print(f"  Student '{first_name} {last_name}' not found.")
            return

        print(f"\n  ── Student: {student.full_name()} | Class: {student.class_name} ──")

        # Find teachers who teach this student's class
        teachers_for_student = [t for t in self.teachers if student.class_name in t.classes]

        if teachers_for_student:
            print(f"  Teachers ({len(teachers_for_student)}):")
            for t in teachers_for_student:
                print(f"    - {t.full_name()} ({t.subject})")
        else:
            print("  No teachers assigned to this student's class yet.")

    def manage_teacher(self):
        """Display all classes a teacher teaches."""
        first_name = input("  Teacher first name: ").strip()
        last_name = input("  Teacher last name: ").strip()
        if not first_name or not last_name:
            print("  [!] First and last name are required.")
            return

        # Find the teacher
        teacher = None
        for t in self.teachers:
            if t.first_name.lower() == first_name.lower() and t.last_name.lower() == last_name.lower():
                teacher = t
                break

        if not teacher:
            print(f"  Teacher '{first_name} {last_name}' not found.")
            return

        print(f"\n  ── Teacher: {teacher.full_name()} | Subject: {teacher.subject} ──")

        if teacher.classes:
            print(f"  Teaches classes ({len(teacher.classes)}):")
            for cls in teacher.classes:
                print(f"    - {cls}")
        else:
            print("  Not assigned to any classes.")

    def manage_homeroom_teacher(self):
        """Display all students the homeroom teacher leads."""
        first_name = input("  Homeroom teacher first name: ").strip()
        last_name = input("  Homeroom teacher last name: ").strip()
        if not first_name or not last_name:
            print("  [!] First and last name are required.")
            return

        # Find the homeroom teacher
        homeroom = None
        for ht in self.homeroom_teachers:
            if ht.first_name.lower() == first_name.lower() and ht.last_name.lower() == last_name.lower():
                homeroom = ht
                break

        if not homeroom:
            print(f"  Homeroom teacher '{first_name} {last_name}' not found.")
            return

        print(f"\n  ── Homeroom Teacher: {homeroom.full_name()} | Class: {homeroom.class_name} ──")

        # Find students in the homeroom teacher's class
        students_led = [s for s in self.students if s.class_name == homeroom.class_name]

        if students_led:
            print(f"  Students ({len(students_led)}):")
            for s in students_led:
                print(f"    - {s.full_name()}")
        else:
            print("  No students enrolled in this class yet.")


# ── Menu Display Functions ────────────────────────────────────────────


def display_main_menu():
    """Display the main menu commands."""
    print("\n" + "=" * 45)
    print("  SCHOOL DATABASE — Main Menu")
    print("=" * 45)
    print(f"  {'create':<20} — Create a new user")
    print(f"  {'manage':<20} — Manage existing users")
    print(f"  {'end':<20} — Exit the program")
    print("=" * 45)


def display_create_menu():
    """Display the user creation menu."""
    print("\n" + "-" * 45)
    print("  CREATE — Select user type")
    print("-" * 45)
    print(f"  {'student':<20} — Create a student")
    print(f"  {'teacher':<20} — Create a teacher")
    print(f"  {'homeroom teacher':<20} — Create a homeroom teacher")
    print(f"  {'end':<20} — Return to main menu")
    print("-" * 45)


def display_manage_menu():
    """Display the user management menu."""
    print("\n" + "-" * 45)
    print("  MANAGE — Select option")
    print("-" * 45)
    print(f"  {'class':<20} — View a class roster")
    print(f"  {'student':<20} — Look up a student")
    print(f"  {'teacher':<20} — Look up a teacher")
    print(f"  {'homeroom teacher':<20} — Look up a homeroom teacher")
    print(f"  {'end':<20} — Return to main menu")
    print("-" * 45)


# ── Sub-Loops ─────────────────────────────────────────────────────────


def create_loop(db):
    """Handle the user creation sub-menu loop."""
    while True:
        display_create_menu()
        choice = input("\n  Enter user type: ").strip().lower()

        if choice == "student":
            db.create_student()
        elif choice == "teacher":
            db.create_teacher()
        elif choice == "homeroom teacher":
            db.create_homeroom_teacher()
        elif choice == "end":
            break
        else:
            print(f"  [!] Unknown option: '{choice}'. Please try again.")


def manage_loop(db):
    """Handle the user management sub-menu loop."""
    while True:
        display_manage_menu()
        choice = input("\n  Enter option: ").strip().lower()

        if choice == "class":
            db.manage_class()
        elif choice == "student":
            db.manage_student()
        elif choice == "teacher":
            db.manage_teacher()
        elif choice == "homeroom teacher":
            db.manage_homeroom_teacher()
        elif choice == "end":
            break
        else:
            print(f"  [!] Unknown option: '{choice}'. Please try again.")


# ── Main Entry Point ──────────────────────────────────────────────────


def main():
    """Main application loop."""
    db = SchoolDatabase()
    print("\n  Welcome to the School Database!")

    while True:
        display_main_menu()
        command = input("\n  Enter command: ").strip().lower()

        if command == "create":
            create_loop(db)
        elif command == "manage":
            manage_loop(db)
        elif command == "end":
            print("\n  Goodbye!\n")
            break
        else:
            print(f"  [!] Unknown command: '{command}'. Please try again.")


if __name__ == "__main__":
    main()
