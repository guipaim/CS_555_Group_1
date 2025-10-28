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
    print("6. Validate Marriage After 14 (US10)")
    print("7. Validate No Bigamy (US11)")
    print("8. Exit")
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


def display_bigamy_validation_errors(family_list, individual_list):
    """Display bigamy validation errors"""
    errors = validate_bigamy(family_list, individual_list)
    
    if not errors:
        print("\nUS11 Validation: No errors found! No cases of bigamy detected.")
        return
    
    table = PrettyTable()
    table.field_names = ["Person ID", "Person Name", "Role", "First Family", "First Marriage", 
                        "Second Family", "Second Marriage", "Error"]
    
    for error in errors:
        # Handle cases where first marriage might have ended
        first_end = error.get('First End Date', 'Ongoing')
        
        table.add_row([
            error['Person ID'],
            error['Person Name'],
            error['Role'],
            error['First Family ID'],
            error['First Marriage Date'],
            error['Second Family ID'],
            error['Second Marriage Date'],
            error['Error']
        ])
    
    print(f"\nUS11 Validation Errors ({len(errors)} found):")
    print(table)


def display_marriage_age_validation_errors(family_list, individual_list):
    """Display marriage after 14 validation errors"""
    errors = validate_US10_marriage_after_14(family_list, individual_list)
    
    if not errors:
        print("\nUS10 Validation: No errors found! All marriages occurred after both spouses were 14 years old.")
        return
    
    table = PrettyTable()
    table.field_names = ["Family ID", "Spouse ID", "Spouse Name", "Role", "Birth Date", 
                        "Marriage Date", "Age at Marriage", "Error"]
    
    for error in errors:
        table.add_row([
            error['Family ID'],
            error['Spouse ID'],
            error['Spouse Name'],
            error['Role'],
            error['Birth Date'],
            error['Marriage Date'],
            error['Age at Marriage'],
            error['Error']
        ])
    
    print(f"\nUS10 Validation Errors ({len(errors)} found):")
    print(table)
def validate_US10_marriage_after_14(family_list, individual_list):
    """
    US10: Marriage after 14
    Marriage should be at least 14 years after birth of both spouses
    """
    errors = []
    
    for fam in family_list:
        married = fam.get('Married', 'NA')
        husb_id = fam.get('Husband ID', 'NA')
        wife_id = fam.get('Wife ID', 'NA')
        
        if married == 'NA':
            continue
        
        try:
            marry_date = datetime.strptime(married, "%d %b %Y")
            
            # Check husband's age at marriage
            for ind in individual_list:
                if ind.get('ID') == husb_id:
                    birth = ind.get('Birthday', 'NA')
                    if birth != 'NA':
                        birth_date = datetime.strptime(birth, "%d %b %Y")
                        age_at_marriage = (marry_date - birth_date).days / 365.25
                        if age_at_marriage < 14:
                            errors.append({
                                'Family ID': fam.get('ID'),
                                'Spouse ID': husb_id,
                                'Spouse Name': ind.get('Name', 'NA'),
                                'Role': 'Husband',
                                'Birth Date': birth,
                                'Marriage Date': married,
                                'Age at Marriage': round(age_at_marriage, 1),
                                'Error': 'Marriage occurred before spouse was 14 years old'
                            })
                    break
            
            # Check wife's age at marriage
            for ind in individual_list:
                if ind.get('ID') == wife_id:
                    birth = ind.get('Birthday', 'NA')
                    if birth != 'NA':
                        birth_date = datetime.strptime(birth, "%d %b %Y")
                        age_at_marriage = (marry_date - birth_date).days / 365.25
                        if age_at_marriage < 14:
                            errors.append({
                                'Family ID': fam.get('ID'),
                                'Spouse ID': wife_id,
                                'Spouse Name': ind.get('Name', 'NA'),
                                'Role': 'Wife',
                                'Birth Date': birth,
                                'Marriage Date': married,
                                'Age at Marriage': round(age_at_marriage, 1),
                                'Error': 'Marriage occurred before spouse was 14 years old'
                            })
                    break
        except ValueError:
            pass
    
    return errors

def validate_bigamy(family_list, individual_list):
    """
    US11: No bigamy
    Marriage should not occur during marriage to another spouse
    """
    errors = []
    
    # Group families by each individual (both husbands and wives)
    individual_marriages = {}
    
    # Collect all marriages for each individual
    for fam in family_list:
        fam_id = fam.get('ID', 'NA')
        married = fam.get('Married', 'NA')
        divorced = fam.get('Divorced', 'NA')
        husb_id = fam.get('Husband ID', 'NA')
        wife_id = fam.get('Wife ID', 'NA')
        
        if married == 'NA':
            continue
        
        try:
            marry_date = datetime.strptime(married, "%d %b %Y")
            divorce_date = None
            if divorced != 'NA':
                divorce_date = datetime.strptime(divorced, "%d %b %Y")
            
            # Add marriage for husband
            if husb_id != 'NA':
                if husb_id not in individual_marriages:
                    individual_marriages[husb_id] = []
                individual_marriages[husb_id].append({
                    'Family ID': fam_id,
                    'Marriage Date': marry_date,
                    'Divorce Date': divorce_date,
                    'Spouse ID': wife_id,
                    'Role': 'Husband'
                })
            
            # Add marriage for wife
            if wife_id != 'NA':
                if wife_id not in individual_marriages:
                    individual_marriages[wife_id] = []
                individual_marriages[wife_id].append({
                    'Family ID': fam_id,
                    'Marriage Date': marry_date,
                    'Divorce Date': divorce_date,
                    'Spouse ID': husb_id,
                    'Role': 'Wife'
                })
                
        except ValueError:
            continue
    
    # Check for overlapping marriages for each individual
    for person_id, marriages in individual_marriages.items():
        if len(marriages) < 2:
            continue
        
        # Sort marriages by marriage date
        marriages.sort(key=lambda x: x['Marriage Date'])
        
        # Get person's name
        person_name = 'NA'
        for ind in individual_list:
            if ind.get('ID') == person_id:
                person_name = ind.get('Name', 'NA')
                break
        
        # Check for overlapping marriage periods
        for i in range(len(marriages)):
            for j in range(i + 1, len(marriages)):
                marriage1 = marriages[i]
                marriage2 = marriages[j]
                
                # Determine end date of first marriage
                end_date1 = marriage1['Divorce Date']
                if end_date1 is None:
                    # If no divorce, check if person is deceased
                    for ind in individual_list:
                        if ind.get('ID') == person_id and ind.get('Death', 'NA') != 'NA':
                            try:
                                end_date1 = datetime.strptime(ind.get('Death'), "%d %b %Y")
                            except ValueError:
                                pass
                            break
                
                # If first marriage has no end date (still married or alive), 
                # any subsequent marriage is bigamy
                if end_date1 is None:
                    if marriage2['Marriage Date'] > marriage1['Marriage Date']:
                        errors.append({
                            'Person ID': person_id,
                            'Person Name': person_name,
                            'Role': marriage1['Role'],
                            'First Family ID': marriage1['Family ID'],
                            'First Marriage Date': marriage1['Marriage Date'].strftime("%d %b %Y"),
                            'Second Family ID': marriage2['Family ID'],
                            'Second Marriage Date': marriage2['Marriage Date'].strftime("%d %b %Y"),
                            'Error': 'Bigamy - married while still married to another spouse'
                        })
                
                # If first marriage ended after second marriage started, it's bigamy
                elif marriage2['Marriage Date'] < end_date1:
                    errors.append({
                        'Person ID': person_id,
                        'Person Name': person_name,
                        'Role': marriage1['Role'],
                        'First Family ID': marriage1['Family ID'],
                        'First Marriage Date': marriage1['Marriage Date'].strftime("%d %b %Y"),
                        'First End Date': end_date1.strftime("%d %b %Y"),
                        'Second Family ID': marriage2['Family ID'],
                        'Second Marriage Date': marriage2['Marriage Date'].strftime("%d %b %Y"),
                        'Error': 'Bigamy - married before previous marriage ended'
                    })
    
    return errors
def run_menu(individuals, families):
    """Run the interactive menu"""
    while True:
        display_menu()
        choice = input("\nEnter your choice (1-8): ").strip()
        
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
            display_marriage_age_validation_errors(families, individuals)
        elif choice == '7':
            display_bigamy_validation_errors(families, individuals)
        elif choice == '8':
            print("\nExiting program. Goodbye!")
            break
        else:
            print("\nInvalid choice! Please enter a number between 1 and 8.")
        
        input("\nPress Enter to continue...")
    
    
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