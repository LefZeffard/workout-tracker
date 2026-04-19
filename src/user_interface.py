from database import Database

class UserInterface:
    def __init__(self):
        self.database = Database()
        self.database.create_tables()
        #self.last_session_id = self.database.get_last_session_id()
        #self.last_session_split_id = self.database.get_last_session_split_id()
    
    def add_splits(self):
        splits_to_add = []
        i = len(self.database.get_splits()) + 1
        while True:
            to_add = input(f"Add day {i} of your workout split (0 - finish): ").strip()
            if to_add == "0":
                if i == 1:
                    print("You haven't added anything.")
                    continue
                elif not splits_to_add:
                    print("No splits added.")
                    return
                else:
                    while True:
                        print("Days to add:")
                        for workout in splits_to_add:
                            print(workout)   
                        confirm = input("(y) - confirm, (n) - restart: ").strip().lower()
                        if confirm == "y":
                            self.database.add_workout_split(splits_to_add)
                            print("Workout splits have been added.")
                            return
                        elif confirm == "n":
                            splits_to_add = []
                            i = len(self.database.get_splits()) + 1
                            break
                        else:
                            print("input (y) or (n).")
                            continue
                continue
            if not to_add:
                print("Split name can't be empty.")
                continue
            normalized_splits = ["".join(split_day.split()).lower() for split_day in splits_to_add]
            normalized_added = "".join(to_add.split()).lower()
            if normalized_added in normalized_splits:
                print("That split day is already in the list.")
                continue
            i += 1
            splits_to_add.append(to_add.strip())

    def add_exercises(self):
        for split in self.database.get_splits():
            split_id = split[0]
            split_name = split[1]
            exercises_to_add = []
            while True:
                to_add = input(f"Add exercise to day {split_name} (0 - finish): ").strip()
                if to_add == "0":
                    if not exercises_to_add:
                        print("You haven't added anything.")
                        continue  
                    print(f"Exercises to add to {split_name}:")
                    for workout in exercises_to_add:
                        print(workout)
                    while True:    
                        confirm = input("(y) - confirm, (n) - restart: ").strip().lower()
                        if confirm == "y":
                            self.database.add_exercises(exercises_to_add, split_id)
                            print(f"Exercises have been added to {split_name}.")
                            break
                        elif confirm == "n":
                            exercises_to_add = []
                            break
                        else:
                            print("Input y or n.")
                    if not exercises_to_add:
                        continue
                    break
                elif not to_add:
                    print("Exercise name can't be empty.")
                    continue
                normalized_exercises = ["".join(exercise.split()).lower() for exercise in exercises_to_add]
                normalized_to_add = "".join(to_add.split()).lower()
                if normalized_to_add in normalized_exercises:
                    print("That exercise is already in the list.")
                    continue
                exercises_to_add.append(to_add)
            
    def parse_splits(self):
        for split in self.database.get_splits():
            split_id = split[0]
            split_name = split[1]
            print(f"{split_id} - {split_name}")
    
    def print_sets_logged(self, session_id: int):
        for row in self.database.get_sets_logged(session_id):
            name = row[1]
            weight = row[2]
            reps = row[3]
            print(f"{name}: {weight} - {reps} reps")
    
    def add_sets(self, split_choose: int):
        while True:
            options = self.database.get_split_exercises(split_choose)
            options_parsed = [f"{i} - {s}" for i, s in enumerate(options, start=1)]
            for option in options_parsed:
                print(option)
            try:
                exercise_log = int(input("Pick an exercise number to log (0 - exit) (100 - log another exercise): ").strip())
            except ValueError:
                print("Only input numbers.")
                continue
            if exercise_log == 0:
                if self.database.get_sets_logged(self.database.get_last_session_split_id()):
                    print("Sets logged:")
                    self.print_sets_logged(self.database.get_last_session_split_id())
                else:
                    print("No sets Logged.")
                print("Exiting...")
                return
            elif exercise_log == 100:
                exercise_name = input("Name of unlisted exercise to log: ").strip()
                confirm = input(f"Confirm {exercise_name} will be added to this session? (y/n): ").strip()
                if confirm.lower() != "y":
                    print("Exercise not added.")
                    continue
                normalized_options = ["".join(exercise.lower().split()) for exercise in options]
                normalized_name = "".join(exercise_name.lower().split())
                if normalized_name in normalized_options:
                    print("Exercise already in split.")
                    continue
            elif not 1 <= exercise_log <= len(options): 
                print("Exercise doesn't exist.")
                continue
            else:
                exercise_name = options[exercise_log - 1]
            i = 1
            weight_reps = {}
            while True:
                print(f"Set {i}: {exercise_name}")
                try:
                    weight = int(input("Weight (0 - finish): ").strip())
                except ValueError:
                    print("Only input numbers.")
                    continue
                if weight == 0:
                    if weight_reps:
                        print("Sets to be logged:")
                        for key, value in weight_reps.items():
                            data_weight = value[0]
                            data_reps = value[1]
                            print(f"{key}: {data_weight} - {data_reps} reps")
                        while True:    
                            confirm = input("Confirm? (y/n): ").strip()
                            if confirm.lower() == "y":
                                for key, value in weight_reps.items():
                                    data_weight = value[0]
                                    data_reps = value[1]
                                    self.database.add_set(self.database.get_last_session_id(), exercise_name, data_weight, data_reps)
                                self.database.add_unique_exercise(exercise_name, self.database.get_last_session_split_id())
                                print("Sets logged.")
                                break
                            elif confirm.lower() == "n":
                                i = 1
                                weight_reps = {}
                                print("Restarting...")
                                break
                            else:
                                print("Input y or n.")
                                continue
                        if weight_reps:
                            break
                        else:
                            continue
                    else:
                        print("No sets have been logged.")
                        break  
                try:
                    reps = int(input("Reps: ").strip())
                except ValueError:
                    print("Only Input Numbers.")
                weight_reps[f"Set {i}"] = [weight, reps]
                i += 1   
    
    def edit_last_session(self): 
        if not self.database.get_last_session_split_id() or not self.database.get_last_session_split_id():
            print("You haven't started any sessions.")
            return
        while True:
            print("EDIT MODE")
            print("0 - Exit")
            print("1 - Add a new set")
            print("2 - Edit a set")
            print("3 - Delete a set")   
            command = input("Command: ").strip()
            if command == "0":
                print("Exiting...")
                return
            elif command == "1":
                self.add_sets(self.database.get_last_session_split_id())
            elif command == "2":
                if self.database.get_sets_logged(self.database.get_last_session_id()):
                    i = 1
                    for row in self.database.get_sets_logged(self.database.get_last_session_id()):
                        name = row[1]
                        weight = row[2]
                        reps = row[3]
                        print(f"{i}: {name} - {weight} - {reps} reps")
                        i += 1
                    try:
                        edit = int(input("Which number set to edit? (0 - Exit): ").strip())
                    except ValueError:
                        print("Only input numbers.")
                        continue
                    if edit == 0:
                        print("Nothing edited.")
                    elif not 1 <= edit <= len(self.database.get_sets_logged(self.database.get_last_session_id())):
                        print("Set doesn't exist.")
                    else:
                        while True:
                            try:
                                newweight = int(input("New weight: ").strip())
                                newreps = int(input("New reps: ").strip())
                            except ValueError:
                                print("Only input numbers.")
                                continue
                            set_id = self.database.get_sets_logged(self.database.get_last_session_id())[edit - 1][0]
                            self.database.edit_set(set_id, newweight, newreps)
                            print("Set changed.")
                            break            
                else:
                    print("You haven't added any sets to the session.")
            elif command == "3":
                if self.database.get_sets_logged(self.database.get_last_session_id()):    
                    i = 1
                    for row in self.database.get_sets_logged(self.database.get_last_session_id()):
                        name = row[1]
                        weight = row[2]
                        reps = row[3]
                        print(f"{i}: {name} - {weight} - {reps} reps")
                        i += 1
                    try:
                        delete = int(input("Which number set to delete? (0 - Exit): ").strip())
                    except ValueError:
                        print("Only input numbers.")
                        continue
                    if delete == 0:
                        print("Nothing deleted.")
                    elif not 1 <= delete <= len(self.database.get_sets_logged(self.database.get_last_session_id())):
                        print("Set doesn't exist.")
                    else:
                        set_id = self.database.get_sets_logged(self.database.get_last_session_id())[delete - 1][0]
                        self.database.delete_set(set_id)
                        print("Set deleted.")
                else:
                    print("You haven't added any sets to the session.")
            else:
                print("Only input 0 1 2 or 3...")
                
    def delete_all_splits(self):
        command = input("Delete all splits? This will delete all exercises as well. (y/n): ").strip().lower()
        if command == "y":
            self.database.delete_all_splits()
            print("Splits have been deleted.")
            return
        print("Splits not deleted.")

    def add_session(self, split_id: int):
        session = self.database.add_session(split_id)
        if session:
            name = session[0]
            date = session[1]
            print(f"{name} at {date} started.")
            print()
            return True
        else:
            print("Workout day doesn't exist.")
            print()
            return False

    def help(self):
        print("MAIN MENU")
        print("0 - Exit")
        print("1 - Start new session")
        print("2 - Edit last session")
        print("9 - Delete all splits")
        
    def execute(self):
        while True:
            if not self.database.get_splits():
                self.add_splits()
            if not self.database.get_all_exercises():
                self.add_exercises()
            self.help()
            command = input("command: ")
            if command == "0":
                break
            elif command == "1":
                if self.database.get_last_session_id():
                    command = input("Start new session? Your last session will finalized and uneditable. (y/n): ").strip().lower()
                    if command != "y":
                        print("Exiting...")
                        continue
                self.parse_splits()
                try:
                    split_choose = int(input("Which number workout to start? (0 - Exit): "))
                    if split_choose == 0:
                        print("Exiting...")
                        continue
                    if self.add_session(split_choose):
                        self.add_sets(split_choose)
                except ValueError:
                    print("Only input numbers.")
            elif command == "2":
                self.edit_last_session()
            elif command == "9":
                self.delete_all_splits()


UserInterface().execute()
