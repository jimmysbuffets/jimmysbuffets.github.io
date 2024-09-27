import csv
from ortools.sat.python import cp_model

# Model setup
model = cp_model.CpModel()

# Parameters
rooms = ['Sassafras', 'Oak', 'Maple', 'Birch', 'Sage', 'Dining', 'Dining Foyer']
time_slots = list(range(12))
teachers = ['Gorman','Bowness','L.Hammond','Rubin','Shar','Bowden','Murawski','Thomas','Edwards','Stillman','Slattery','Bowder','B.Hammond','Pearce','Rowell','Meyers','B.Heron',
            'Hirschfeld','S.Heron','Nelson','Arcara','Watt','Richmond','B.West','E.West','Spadone','Bagg','Rouillard','Holmes','B.Stockwell','K.Stockwell','Marschall']
subjects = ['BG', 'OT', 'J']
max_classes_per_teacher = 8
min_teachers_per_class = 2  # At least 2 teachers per class
max_teachers_per_class = 4

# Teacher qualifications
teacher_qualifications = {'Gorman': ['BG', 'OT'],
                          'Bowness': ['BG', 'OT', 'J'],
                          'L.Hammond': ['BG', 'OT', 'J'],
                          'Rubin': ['BG', 'OT'],
                          'Shar': ['BG', 'OT'],
                          'Bowden': ['BG'],
                          'Murawski': ['OT'],
                          'Thomas': ['BG'],
                          'Edwards': ['OT', 'J'],
                          'Stillman': ['BG'],
                          'Slattery': ['OT'],
                          'Bowder': ['BG', 'OT', 'J'],
                          'B.Hammond': ['BG', 'OT', 'J'],
                          'Pearce': ['BG', 'OT'],
                          'Rowell': ['OT'],
                          'Meyers': ['BG', 'OT', 'J'],
                          'B.Heron': ['BG', 'OT', 'J'],
                          'Hirschfeld': ['BG'],
                          'S.Heron': ['BG', 'OT', 'J'],
                          'Nelson': ['BG', 'OT', 'J'],
                          'Arcara': ['BG', 'OT'],
                          'B.Stockwell': ['BG'],
                          'Watt': ['BG'],
                          'Richmond': ['BG'],
                          'B.West': ['BG'],
                          'E.West': ['BG'],
                          'Spadone': ['OT'],
                          'Bagg': ['BG', 'J'],
                          'Rouillard': ['OT'],
                          'Holmes': ['BG', 'OT', 'J'],
                          'K.Stockwell': ['BG', 'OT', 'J'],
                          'Marschall': ['BG', 'OT', 'J']
                          }

# Decision variables: teacher assignments and subject assignments
assignment = {}
subject_assignment = {}

for room in rooms:
    for time in time_slots:
        for teacher in teachers:
            assignment[(room, time, teacher)] = model.NewBoolVar(f'{room}_{time}_Teacher_{teacher}')
        for subject in subjects:
            subject_assignment[(room, time, subject)] = model.NewBoolVar(f'{room}_{time}_Subject_{subject}')

# Each class must have between 2 and 4 teachers
for room in rooms:
    for time in time_slots:
        model.Add(
            sum(assignment[(room, time, teacher)] for teacher in teachers) >= min_teachers_per_class
        )
        model.Add(
            sum(assignment[(room, time, teacher)] for teacher in teachers) <= max_teachers_per_class
        )

# Each teacher can only teach up to max_classes_per_teacher classes
for teacher in teachers:
    model.Add(
        sum(assignment[(room, time, teacher)] for room in rooms for time in time_slots) <= max_classes_per_teacher
    )

# Teachers can only teach subjects they are qualified for
for room in rooms:
    for time in time_slots:
        for teacher in teachers:
            qualified_subjects = teacher_qualifications[teacher]
            for subject in subjects:
                if subject not in qualified_subjects:
                    model.AddImplication(assignment[(room, time, teacher)], subject_assignment[(room, time, subject)].Not())

# Ensure each room-time slot has exactly one subject assigned
for room in rooms:
    for time in time_slots:
        model.Add(
            sum(subject_assignment[(room, time, subject)] for subject in subjects) == 1
        )

# Objective: balance teacher assignments (minimize the variance of classes per teacher)
target_classes_per_teacher = len(rooms) * len(time_slots) / len(teachers)

# Create auxiliary variables to capture the absolute deviation from the target
abs_deviation = []
for teacher in teachers:
    total_classes = sum(assignment[(room, time, teacher)] for room in rooms for time in time_slots)
    deviation = model.NewIntVar(0, max_classes_per_teacher, f'deviation_teacher_{teacher}')
    model.AddAbsEquality(deviation, total_classes - int(target_classes_per_teacher))
    abs_deviation.append(deviation)

# Minimize the total absolute deviation across all teachers
model.Minimize(sum(abs_deviation))

# Solver
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Output schedules
grid_schedule = [['Room/Time'] + time_slots]  # Grid schedule header
teacher_schedule = [['Teacher'] + [f'Class {i+1}' for i in range(max_classes_per_teacher)]]  # Teacher schedule header

if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
    # Prepare grid schedule
    for room in rooms:
        room_schedule = [room]  # Row for the current room
        for time in time_slots:
            teachers_in_class = [f'Teacher_{teacher}' for teacher in teachers if solver.Value(assignment[(room, time, teacher)])]
            subjects_in_class = [subject for subject in subjects if solver.Value(subject_assignment[(room, time, subject)])]
            room_schedule.append(f'Subject: {subjects_in_class[0]}, Teachers: {", ".join(teachers_in_class)}')
        grid_schedule.append(room_schedule)

    # Prepare teacher schedule
    for teacher in teachers:
        teacher_row = [f'Teacher_{teacher}']
        assignments = []
        for room in rooms:
            for time in time_slots:
                if solver.Value(assignment[(room, time, teacher)]):
                    subject_in_class = [subject for subject in subjects if solver.Value(subject_assignment[(room, time, subject)])][0]
                    assignments.append(f'Room: {room}, Time: {time}, Subject: {subject_in_class}')
        teacher_row += assignments + [''] * (max_classes_per_teacher - len(assignments))  # Fill empty cells if fewer classes
        teacher_schedule.append(teacher_row)

    # Write grid schedule to CSV
    with open('grid_schedule.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(grid_schedule)

    # Write teacher schedule to CSV
    with open('teacher_assignments.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(teacher_schedule)

    print("Schedules saved to CSV files.")
else:
    print("No feasible solution found.")