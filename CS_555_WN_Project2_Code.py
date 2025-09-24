from prettytable import PrettyTable
from datetime import datetime

# Supported GEDCOM tags
supported_tags = {
    'INDI', 'NAME', 'SEX', 'BIRT', 'DEAT', 'FAMC', 'FAMS',
    'FAM', 'MARR', 'HUSB', 'WIFE', 'CHIL', 'DIV', 'DATE',
    'HEAD', 'TRLR', 'NOTE'
}

# Data storage
individuals = []
families = []

# Parsing state variables
curr_indiv = None
curr_fam = None
birth = False
death = False
marriage = False
divorce = False

def parse_line(line):
    """Parse a GEDCOM line into level, tag, valid, and arguments"""
    parts = line.strip().split(' ', 2)
    level = parts[0]
    tag = parts[1]
    valid = 'Y' if tag in supported_tags else 'N'
    arguments = parts[2] if len(parts) > 2 else ''
    
    return level, tag, valid, arguments

def normalize_name(name):
    """Return 'Given /Surname/' with duplicated surname removed from the given part."""
    if not name or name == 'NA':
        return 'NA'
    s = name.strip()
    if '/' in s:
        parts = s.split('/')
        if len(parts) >= 3:
            given = parts[0].strip()
            surname = parts[1].strip()
            if surname:
                given_tokens = given.split()
                surname_tokens = surname.split()
                if len(given_tokens) >= len(surname_tokens) and given_tokens[-len(surname_tokens):] == surname_tokens:
                    given = ' '.join(given_tokens[:-len(surname_tokens)]).strip()
            if given:
                return f"{given} /{surname}/"
            else:
                return f"/{surname}/"
    return s

def organizeFamilyData(family_list, individual_list):
    """Organize family data with spouse names"""
    for fam in family_list:
        fam_id = fam.get('ID', 'NA')
        married = fam.get('MARR', 'NA')
        divorced = fam.get('DIV', 'NA')
        husb_id = fam.get('HUSB', 'NA')
        wife_id = fam.get('WIFE', 'NA')
        children = fam.get('CHIL', [])

        husb_name = 'NA'
        wife_name = 'NA'

        if husb_id != 'NA':
            for ind in individual_list:
                if ind.get('ID') == husb_id:
                    husb_name = normalize_name(ind.get('NAME', 'NA'))
                    break

        if wife_id != 'NA':
            for ind in individual_list:
                if ind.get('ID') == wife_id:
                    wife_name = normalize_name(ind.get('NAME', 'NA'))
                    break

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
    """Organize individual data with calculated fields"""
    individual_list.sort(key=lambda x: x.get('ID', ''))

    for ind in individual_list:
        ind_id = ind.get('ID', 'NA')
        name_raw = ind.get('NAME', 'NA')
        name = normalize_name(name_raw)
        gender = ind.get('SEX', 'NA')
        bday = ind.get('BIRT', 'NA')

        # Parse birthday
        if bday != 'NA':
            try:
                bday_copy = datetime.strptime(bday, "%d %b %Y")
            except ValueError:
                bday_copy = None
        else:
            bday_copy = None

        death = ind.get('DEAT', 'NA')

        # Calculate age
        if bday_copy is None:
            age = 'NA'
        else:
            if death != 'NA':
                try:
                    death_copy = datetime.strptime(death, "%d %b %Y")
                    age = death_copy.year - bday_copy.year - ((death_copy.month, death_copy.day) < (bday_copy.month, bday_copy.day))
                except ValueError:
                    age = 'NA'
            else:
                today = datetime.today()
                age = today.year - bday_copy.year - ((today.month, today.day) < (bday_copy.month, bday_copy.day))

        alive = 'False' if death != 'NA' else 'True'

        # Find spouse and children families
        spouse = 'NA'
        child_families = []  # Families where this person is a parent
        
        for fam in family_list:
            # If this person is husband or wife, they have a spouse
            if fam.get('Husband ID') == ind_id:
                spouse = fam.get('Wife ID', 'NA')
                child_families.append(fam.get('ID'))  # This family has their children
            elif fam.get('Wife ID') == ind_id:
                spouse = fam.get('Husband ID', 'NA')  
                child_families.append(fam.get('ID'))  # This family has their children

        ind.clear()
        ind['ID'] = ind_id
        ind['Name'] = name
        ind['Gender'] = gender
        ind['Birthday'] = bday
        ind['Age'] = age
        ind['Alive'] = alive
        ind['Death'] = death
        ind['Children'] = child_families  # Family IDs where they are parents
        ind['Spouse'] = spouse

    return individual_list

def createTable(family_list, individual_list):
    """Create and print formatted tables"""
    individual_list.sort(key=lambda x: x['ID'])
    family_list.sort(key=lambda x: x['ID'])

    # Individuals table
    ind_table = PrettyTable()
    ind_table.field_names = ["ID", "Name", "Gender", "Birthday", "Age", "Alive", "Death", "Child", "Spouse"]

    for ind in individual_list:
        children_list = ind.get('Children', [])
        children_display = "{" + ", ".join([f"'{c}'" for c in children_list]) + "}" if children_list else "NA"

        ind_table.add_row([
            ind.get('ID', ''),
            ind.get('Name', ''),
            ind.get('Gender', ''),
            ind.get('Birthday', ''),
            ind.get('Age', ''),
            ind.get('Alive', ''),
            ind.get('Death', ''),
            children_display,
            ind.get('Spouse', '')
        ])

    print("\nIndividuals")
    print(ind_table)

    # Families table
    fam_table = PrettyTable()
    fam_table.field_names = ["ID", "Married", "Divorced", "Husband ID", "Husband Name", "Wife ID", "Wife Name", "Children"]

    for fam in family_list:
        children_list = fam.get('Children', [])
        children_display = "{" + ", ".join([f"'{c}'" for c in children_list]) + "}" if children_list else "NA"

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

    print("\nFamilies")
    print(fam_table)

# Main parsing logic
with open('Gedcom-file.ged', 'r') as file:
    for line in file:
        print(f'--> {line.strip()}')
        level, tag, valid, arguments = parse_line(line)
        print(f'<-- {level}|{tag}|{valid}|{arguments}')

        if level == '0':
            if arguments == 'INDI' and tag.startswith('@'):
                if curr_indiv:
                    individuals.append(curr_indiv)
                curr_indiv = {'ID': tag.strip().replace('@', '')}
            elif arguments == 'FAM' and tag.startswith('@'):
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

# Add the last individual and family
if curr_indiv:
    individuals.append(curr_indiv)
if curr_fam:
    families.append(curr_fam)

# Process and display data
print(f'\nNumber of Individuals: {len(individuals)}')
print(f'Number of Families: {len(families)}')

# Organize the data
families = organizeFamilyData(families, individuals)
individuals = organizeIndividualData(families, individuals)

# Create and display tables
createTable(families, individuals)