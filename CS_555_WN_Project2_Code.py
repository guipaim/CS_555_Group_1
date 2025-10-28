from datetime import datetime, timedelta
from prettytable import PrettyTable


def parse_line(line):  
    
    supported_tags = {
    'INDI', 'NAME', 'SEX', 'BIRT', 'DEAT', 'FAMC', 'FAMS',
    'FAM', 'MARR', 'HUSB', 'WIFE', 'CHIL', 'DIV', 'DATE',
    'HEAD', 'TRLR', 'NOTE'
    }
    
    parts = line.strip().split(' ', 2)
    level = parts[0]
    tag = parts[1]
    valid = 'Y' if tag in supported_tags else 'N'
    arguments = parts[2] if len(parts) > 2 else ''

    return level, tag, valid, arguments


def is_bday_in_past(bday_str):
    bday_str = datetime.strptime(bday_str, "%d %b %Y")
    today_date_str = datetime.today()
    
    if bday_str < today_date_str:
        return True
    else:
        return False

def readGedcomFile(filename):
    
    individuals = []
    families = []

    curr_indiv = None
    curr_fam = None
    birth = False
    death = False
    marriage = False
    divorce = False
    #start
    with open(filename, 'r') as file:
        for line in file:
            level, tag, valid, arguments = parse_line(line)

            if level == '0':
                if 'INDI' in line:
                    if curr_indiv:
                        individuals.append(curr_indiv)
                    curr_indiv = {'ID': tag.strip().replace('@', '')}
                elif 'FAM' in line:
                    if curr_fam:
                        families.append(curr_fam)
                    curr_fam = {'ID': tag.strip().replace('@', '')}
            elif level == '1':
                if tag == 'NAME' and curr_indiv is not None:
                    curr_indiv['NAME'] = arguments
                elif tag == 'SEX' and curr_indiv is not None:
                    curr_indiv['SEX'] = arguments
                elif tag == 'BIRT':
                    birth = True
                elif tag == 'DEAT':
                    death = True
                elif tag == 'MARR':
                    marriage = True
                elif tag == 'DIV':
                    divorce = True
                elif tag == 'HUSB' and curr_fam is not None:
                    curr_fam['HUSB'] = arguments.strip().replace('@', '')
                elif tag == 'WIFE' and curr_fam is not None:
                    curr_fam['WIFE'] = arguments.strip().replace('@', '')
                elif tag == 'CHIL' and curr_fam is not None:
                    curr_fam.setdefault('CHIL', []).append(arguments.strip().replace('@', ''))
            elif level == '2' and tag == 'DATE':
                if birth and curr_indiv is not None:
                    curr_indiv['BIRT'] = arguments
                    birth = False
                elif death and curr_indiv is not None:
                    curr_indiv['DEAT'] = arguments
                    death = False
                elif marriage and curr_fam is not None:
                    curr_fam['MARR'] = arguments
                    marriage = False
                elif divorce and curr_fam is not None:
                    curr_fam['DIV'] = arguments
                    divorce = False

        if curr_indiv:
            individuals.append(curr_indiv)
        if curr_fam:
            families.append(curr_fam)
        
    return individuals, families
    
    
def organizeFamilyData(family_list, individual_list):
    #Reorganize family data to match order and add spouse names for families:
    for fam in family_list:
        fam_id = fam.get('ID', 'NA')
        married=fam.get('MARR', 'NA')
        divorced=fam.get('DIV', 'NA')
        husb_id=fam.get('HUSB', 'NA')
        wife_id=fam.get('WIFE', 'NA')
        children=fam.get('CHIL', [])
        #find spouse names 
        husb_name = 'NA'
        wife_name = 'NA'

        if husb_id != 'NA':
            for ind in individual_list:
                if ind.get('ID') == husb_id:
                    husb_name = ind.get('NAME', 'NA')
                    break

        if wife_id != 'NA':
            for ind in individual_list:
                if ind.get('ID') == wife_id:
                    wife_name = ind.get('NAME', 'NA')
                    break

        #reorganize family in desired order
        fam.clear()
        fam['ID'] = fam_id
        fam['Married'] = married
        fam['Divorced'] = divorced
        fam['Husband ID'] = husb_id
        fam['Husband Name'] = husb_name
        fam['Wife ID'] = wife_id
        fam['Wife Name'] = wife_name
        fam['Children'] = children
    
    return family_list


def organizeIndividualData(family_list, individual_list):
    #sort individuals by ID 

    individual_list.sort(key=lambda x: x.get('ID', ''))

    #reorganize individual data to match order of table
    for ind in individual_list:
        ind_id = ind.get('ID', 'NA')
        name = ind.get('NAME', 'NA')
        gender = ind.get('SEX', 'NA')
        bday = ind.get('BIRT', 'NA')

        #get the age
        bday_copy = bday
        if is_bday_in_past(bday_copy):
            # Convert birth string to datetime
            bday_copy = datetime.strptime(bday_copy, "%d %b %Y")

            death = ind.get('DEAT', 'NA')

            if 'DEAT' in ind:


                death_copy = death
                death_copy = datetime.strptime(death_copy, "%d %b %Y")

                age = death_copy.year - bday_copy.year - ((death_copy.month, death_copy.day) < (bday_copy.month, bday_copy.day))
            else:
                today = datetime.today()
                age = today.year - bday_copy.year - ((today.month, today.day) < (bday_copy.month, bday_copy.day))

            alive = 'False' if 'DEAT' in ind else 'True'


            spouse = 'NA' if 'FAMS' not in ind else ind.get('FAMS', [])


            children = []

            for fam in family_list:
                if fam.get('Husband ID') == ind_id or fam.get('Wife ID') == ind_id:
                    children = 'NA' if 'Children' not in fam else fam.get('Children', [])

                    if fam.get('Husband ID') == ind_id:
                        spouse = fam.get('Wife ID', 'NA')
                    elif fam.get('Wife ID') == ind_id:
                        spouse = fam.get('Husband ID', 'NA')

                    break
                
            ind.clear()
            ind['ID'] = ind_id
            ind['Name'] = name
            ind['Gender'] = gender
            ind['Birthday'] = bday
            ind['Age'] = age
            ind['Alive'] = alive
            ind['Death'] = death
            ind['Children'] = children
            ind['Spouse'] = spouse
    
    return individual_list

def createTable(family_list, individual_list):
    #start
    individual_list.sort(key=lambda x: x['ID'])
    family_list.sort(key=lambda x: x['ID'])

    ind_table = PrettyTable()
    ind_table.field_names = ["ID", "Name", "Gender", "Birthday", "Age", "Alive", "Death", "Children", "Spouse"]

    for ind in individual_list:
        # Format Children with curly braces
        children = ind.get('Children', [])
        if children == 'NA' or not children:
            children_display = "NA"
        elif isinstance(children, list):
            children_display = "{" + ", ".join([f"'{c}'" for c in children]) + "}"
        else:
            children_display = f"{{'{children}'}}"
        
        # Format Spouse with curly braces
        spouse = ind.get('Spouse', 'NA')
        if spouse == 'NA':
            spouse_display = "NA"
        else:
            spouse_display = f"{{'{spouse}'}}"

        ind_table.add_row([
            ind.get('ID', ''),
            ind.get('Name', ''),
            ind.get('Gender', ''),
            ind.get('Birthday', ''),
            ind.get('Age', ''),
            ind.get('Alive', ''),
            ind.get('Death', ''),
            children_display,
            spouse_display
        ])

    print("\nIndividuals:")
    print(ind_table)

    fam_table = PrettyTable()
    fam_table.field_names = ["ID", "Married", "Divorced", "Husband ID", "Husband Name", "Wife ID", "Wife Name", "Children"]

    for fam in family_list:
        # Format Children with curly braces for families too
        children = fam.get('Children', [])
        if not children:
            children_display = "NA"
        else:
            children_display = "{" + ", ".join([f"'{c}'" for c in children]) + "}"

        fam_table.add_row([
            fam.get('ID', ''),
            fam.get('Married', ''),
            fam.get('Divorced', ''),
            fam.get('Husband ID', ''),
            fam.get('Husband Name', ''),
            fam.get('Wife ID', ''),
            fam.get('Wife Name', ''),
            children_display
        ])

    print("\nFamilies:")
    print(fam_table)

def verifyAge(individual_list):
    for ind in individual_list:
        if ind['Age'] < 0:
            print("Error: " + ind['Name'] + " died before they were born")
            individual_list.remove(ind)

def list_deceased(individual_list):
    """List all deceased individuals"""
    deceasedList = []
    
    for ind in individual_list:
        if ind.get('Alive') == 'False':
            deceasedList.append(ind)

    return deceasedList

def list_living_married(individual_list):
    """List all living married individuals"""
    living_married_list = []

    for ind in individual_list:
        if ind.get('Alive') == 'True' and ind.get('Spouse') != 'NA':
            living_married_list.append(ind)
            
    return living_married_list

def list_recent_deaths(individual_list, days=3650):
    """US36: List all deaths that occurred within the last 10 years"""
    recent_deaths_list = []
    today = datetime.today()
    thirty_days_ago = today - timedelta(days=30)

    for ind in individual_list:
        death_date_str = ind.get('Death', 'NA')
        if death_date_str != 'NA':
            try:
                death_date = datetime.strptime(death_date_str, "%d %b %Y")
                days_since_death = (today - death_date).days

                if days_since_death <= days:
                    recent_deaths_list.append(ind)
            except ValueError:
                pass
    
    return recent_deaths_list

def validate_marriage_before_death(family_list, individual_list):
    """US05: Marriage should occur before death of either spouse"""
    errors = []
    
    for fam in family_list:
        married = fam.get('Married', 'NA')
        husb_id = fam.get('Husband ID', 'NA')
        wife_id = fam.get('Wife ID', 'NA')
        
        if married == 'NA':
            continue
        
        try:
            marry_date = datetime.strptime(married, "%d %b %Y")
            
            # Check husband's death
            for ind in individual_list:
                if ind.get('ID') == husb_id:
                    death = ind.get('Death', 'NA')
                    if death != 'NA':
                        death_date = datetime.strptime(death, "%d %b %Y")
                        if marry_date >= death_date:
                            errors.append({
                                'Family ID': fam.get('ID'),
                                'Spouse ID': husb_id,
                                'Spouse Name': ind.get('Name', 'NA'),
                                'Role': 'Husband',
                                'Marriage Date': married,
                                'Death Date': death,
                                'Error': 'Marriage date must be before death date'
                            })
                    break
            
            # Check wife's death
            for ind in individual_list:
                if ind.get('ID') == wife_id:
                    death = ind.get('Death', 'NA')
                    if death != 'NA':
                        death_date = datetime.strptime(death, "%d %b %Y")
                        if marry_date >= death_date:
                            errors.append({
                                'Family ID': fam.get('ID'),
                                'Spouse ID': wife_id,
                                'Spouse Name': ind.get('Name', 'NA'),
                                'Role': 'Wife',
                                'Marriage Date': married,
                                'Death Date': death,
                                'Error': 'Marriage date must be before death date'
                            })
                    break
                    
        except ValueError:
            pass
    
    return errors


def validate__divorce_before_death(family_list, individual_list):
    """US06: Divorce can only occur before death of both spouses"""
    errors = []
    
    for fam in family_list:
        divorced = fam.get('Divorced', 'NA')
        husb_id = fam.get('Husband ID', 'NA')
        wife_id = fam.get('Wife ID', 'NA')
        
        if divorced == 'NA':
            continue
        
        try:
            divorce_date = datetime.strptime(divorced, "%d %b %Y")
            
            # Check husband's death
            for ind in individual_list:
                if ind.get('ID') == husb_id:
                    death = ind.get('Death', 'NA')
                    if death != 'NA':
                        death_date = datetime.strptime(death, "%d %b %Y")
                        if divorce_date >= death_date:
                            errors.append({
                                'Family ID': fam.get('ID'),
                                'Spouse ID': husb_id,
                                'Spouse Name': ind.get('Name', 'NA'),
                                'Role': 'Husband',
                                'Divorce Date': divorced,
                                'Death Date': death,
                                'Error': 'Divorce date must be before death date'
                            })
                    break
            
            # Check wife's death
            for ind in individual_list:
                if ind.get('ID') == wife_id:
                    death = ind.get('Death', 'NA')
                    if death != 'NA':
                        death_date = datetime.strptime(death, "%d %b %Y")
                        if divorce_date >= death_date:
                            errors.append({
                                'Family ID': fam.get('ID'),
                                'Spouse ID': wife_id,
                                'Spouse Name': ind.get('Name', 'NA'),
                                'Role': 'Wife',
                                'Divorce Date': divorced,
                                'Death Date': death,
                                'Error': 'Divorce date must be before death date'
                            })
                    break
                    
        except ValueError:
            pass
    
    return errors

def validate_birth_before_marriage(individual_list, family_list):
    """Check that birth date precedes marriage date, otherwise throw error"""

    for ind in individual_list:
        
        spouse = ind.get('Spouse')
        birthday = ind.get('Birthday')

        if spouse == 'NA' or birthday == 'NA' or birthday is None:
            continue

        birth_date = datetime.strptime(birthday, "%d %b %Y")

        for fam in family_list:
            if fam.get('Husband ID') == ind.get('ID') or fam.get('Wife ID') == ind.get('ID'):
                married = fam.get('Married')
                
                if married == 'NA' or married is None:
                    continue

                marriage_date = datetime.strptime(married, "%d %b %Y")

                if birth_date > marriage_date:
                    raise ValueError(
                        f"ERROR: Individual {ind.get('ID')} ({ind.get('Name')}) "
                        f"was born ({ind.get('Birthday')}) after marriage ({fam.get('Married')})"
                    )
    return True


def display_menu():
    """Display the main menu options"""
    print("\n" + "="*60)
    print(" GEDCOM Analysis Menu")
    print("="*60)
    print("1. Display All Individuals and Families")
    print("2. List Deceased Individuals")
    print("3. List Living Married Individuals")
    print("4. Validate Marriage Before Death (US05)")
    print("5. Validate Divorce Before Death (US06)")
    print("6. List All Single Individuals Over 30 Years Old")
    print("7. List Individuals with the Same Birthday")
    print("10. Exit")
    print("="*60)


def display_deceased_table(individual_list):
    """Display deceased individuals in a formatted table"""
    deceased = list_deceased(individual_list)
    
    if not deceased:
        print("\nNo deceased individuals found.")
        return
    
    table = PrettyTable()
    table.field_names = ["ID", "Name", "Gender", "Birthday", "Age", "Death", "Children", "Spouse"]
    
    for ind in deceased:
        children = ind.get('Children', [])
        if children == 'NA' or not children:
            children_display = "NA"
        elif isinstance(children, list):
            children_display = "{" + ", ".join([f"'{c}'" for c in children]) + "}"
        else:
            children_display = f"{{'{children}'}}"
        
        spouse = ind.get('Spouse', 'NA')
        if spouse == 'NA':
            spouse_display = "NA"
        else:
            spouse_display = f"{{'{spouse}'}}"
        
        table.add_row([
            ind.get('ID', ''),
            ind.get('Name', ''),
            ind.get('Gender', ''),
            ind.get('Birthday', ''),
            ind.get('Age', ''),
            ind.get('Death', ''),
            children_display,
            spouse_display
        ])
    
    print(f"\nDeceased Individuals ({len(deceased)} found):")
    print(table)


def display_living_married_table(individual_list):
    """Display living married individuals in a formatted table"""
    living_married = list_living_married(individual_list)
    
    if not living_married:
        print("\nNo living married individuals found.")
        return
    
    table = PrettyTable()
    table.field_names = ["ID", "Name", "Gender", "Birthday", "Age", "Children", "Spouse"]
    
    for ind in living_married:
        children = ind.get('Children', [])
        if children == 'NA' or not children:
            children_display = "NA"
        elif isinstance(children, list):
            children_display = "{" + ", ".join([f"'{c}'" for c in children]) + "}"
        else:
            children_display = f"{{'{children}'}}"
        
        spouse = ind.get('Spouse', 'NA')
        if spouse == 'NA':
            spouse_display = "NA"
        else:
            spouse_display = f"{{'{spouse}'}}"
        
        table.add_row([
            ind.get('ID', ''),
            ind.get('Name', ''),
            ind.get('Gender', ''),
            ind.get('Birthday', ''),
            ind.get('Age', ''),
            children_display,
            spouse_display
        ])
    
    print(f"\nLiving Married Individuals ({len(living_married)} found):")
    print(table)


def display_marriage_validation_errors(family_list, individual_list):
    """Display marriage before death validation errors"""
    errors = validate_marriage_before_death(family_list, individual_list)
    
    if not errors:
        print("\nUS05 Validation: No errors found! All marriages occurred before death.")
        return
    
    table = PrettyTable()
    table.field_names = ["Family ID", "Spouse ID", "Spouse Name", "Role", "Marriage Date", "Death Date", "Error"]
    
    for error in errors:
        table.add_row([
            error['Family ID'],
            error['Spouse ID'],
            error['Spouse Name'],
            error['Role'],
            error['Marriage Date'],
            error['Death Date'],
            error['Error']
        ])
    
    print(f"\nUS05 Validation Errors ({len(errors)} found):")
    print(table)


def display_divorce_validation_errors(family_list, individual_list):
    """Display divorce before death validation errors"""
    errors = validate__divorce_before_death(family_list, individual_list)
    
    if not errors:
        print("\nUS06 Validation: No errors found! All divorces occurred before death.")
        return
    
    table = PrettyTable()
    table.field_names = ["Family ID", "Spouse ID", "Spouse Name", "Role", "Divorce Date", "Death Date", "Error"]
    
    for error in errors:
        table.add_row([
            error['Family ID'],
            error['Spouse ID'],
            error['Spouse Name'],
            error['Role'],
            error['Divorce Date'],
            error['Death Date'],
            error['Error']
        ])
    
    print(f"\nUS06 Validation Errors ({len(errors)} found):")
    print(table)


def run_menu(individuals, families):
    """Run the interactive menu"""
    while True:
        display_menu()
        choice = input("\nEnter your choice (1-7): ").strip()
        
        if choice == '1':
            createTable(families, individuals)
        elif choice == '2':
            display_deceased_table(individuals)
        elif choice == '3':
            display_living_married_table(individuals)
        elif choice == '4':
            display_marriage_validation_errors(families, individuals)
        elif choice == '5':
            display_divorce_validation_errors(families, individuals)
        elif choice == '6':
            single_individuals = listAllSingleIndividuals(individuals)
            if not single_individuals:
                print("No single individuals found.")
            else:
                print("\nList of Single Individuals (Age > 30):")
                for ind in single_individuals:
                    print(f" - {ind.get('Name')} (ID: {ind.get('ID')}, Age: {ind.get('Age')})")
        elif choice == '7':
            print("\nList of Individuals That Have The Same Birthday:" )
            bday_list = listMultipleBdays(individuals)
            for ind in bday_list:
                print(f" - {ind.get('Name')} (ID: {ind.get('ID')}, Birthday: {ind.get('Birthday')})")
        elif choice == '10':
            print("\nExiting program. Goodbye!")
            break
        else:
            print("\nInvalid choice! Please enter a number between 1 and 7.")

        input("\nPress Enter to continue...")
  
def listAllSingleIndividuals(individual_list):
    single_individuals = []
    for ind in individual_list:
        if ind.get('Spouse') == 'NA' and ind.get('Alive') == 'True' and ind.get('Age', 0) > 30:
            single_individuals.append(ind)
    return single_individuals

def listMultipleBdays(individual_list):
    bday_map = {}
    shared_bdays = []
    
    for ind in individual_list:
        bday = ind.get('Birthday', 'NA')
        parts = bday.split()
        if len(parts) >= 2:
            bday_key = f"{parts[0]} {parts[1]}" 
        else:
            bday_key = bday  
        if bday_key in bday_map:
            shared_bdays.append(ind)
            
            first_person = bday_map[bday_key]
            if first_person not in shared_bdays:
                shared_bdays.append(first_person)
        else:
            bday_map[bday_key] = ind
    if not shared_bdays:
        print("No individuals share the same birthday.")
    
    return shared_bdays
            
        


if __name__ == "__main__":
    #readGedFile
    individuals, families = readGedcomFile("Gedcom-file.ged")
    
    #organize fam data
    families = organizeFamilyData(families, individuals)
    
    #organize individual
    individuals = organizeIndividualData(families, individuals)
    verifyAge(individuals)
    
    # Run the interactive menu
    run_menu(individuals, families)