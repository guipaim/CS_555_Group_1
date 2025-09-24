from datetime import datetime
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
            print(f'--> {line.strip()}')
            level, tag, valid, arguments = parse_line(line)
            print(f'<-- {level}|{tag}|{valid}|{arguments}')

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


if __name__ == "__main__":
    #readGedFile
    individuals, families = readGedcomFile("Gedcom-file.ged")
    
    #organize fam data
    families = organizeFamilyData(families, individuals)
    
    #organize individual
    individuals = organizeIndividualData(families, individuals)
    
    
    #print individuals and families
    ''' 
    print('\nIndividuals:')
    for ind in individuals:
        print(ind)

    print('\nFamilies:')
    for fam in families:
        print(fam)
    '''
    
    createTable(families, individuals)