from prettytable import PrettyTable
from datetime import datetime, date


supported_tags = {
    'INDI', 'NAME', 'SEX', 'BIRT', 'DEAT', 'FAMC', 'FAMS',
    'FAM', 'MARR', 'HUSB', 'WIFE', 'CHIL', 'DIV', 'DATE',
    'HEAD', 'TRLR', 'NOTE'
}

individuals = []
families = []

curr_indiv = None
curr_fam = None
birth = False
death = False
marriage = False
divorce = False

def na_if_empty(value):
    return value if value not in (None, '', [], {}) else 'N/A'

def parse_line(line):
    parts = line.strip().split(' ', 2)
    level = parts[0]
    tag = parts[1]
    valid = 'Y' if tag in supported_tags else 'N'
    arguments = parts[2] if len(parts) > 2 else ''

    return level, tag, valid, arguments

def calculate_age(birth_str, death_str=None):
    try:
        birth_date = datetime.strptime(birth_str, "%d %b %Y").date()
    except:
        return ''
    if death_str:
        try:
            death_date = datetime.strptime(death_str, "%d %b %Y").date()
        except:
            return '' 
        return death_date.year - birth_date.year - ((death_date.month, death_date.day) < (birth_date.month, birth_date.day))
    else:
        today = date.today()
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                
with open('Gedcom-file.ged', 'r') as file:
    for line in file:
        
        level, tag, valid, arguments = parse_line(line)
        
        if level == '0':
            if 'INDI' in line:
                if curr_indiv:
                    individuals.append(curr_indiv)
                indiv_id = tag.strip('@') if tag.startswith('@') else arguments.strip('@')    
                curr_indiv = { 
                    'ID': indiv_id,
                    'NAME': arguments.split()[0]}
            elif 'FAM' in line:
                if curr_fam:
                    families.append(curr_fam)
                fam_id = tag.strip('@') if tag.startswith('@') else arguments.strip('@')
                curr_fam = { 
                    'ID': fam_id,
                    'NAME': arguments.split()[0]}
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
                curr_fam['HUSB'] = arguments
            elif tag == 'WIFE' and curr_fam is not None:
                curr_fam['WIFE'] = arguments
            elif tag == 'CHIL' and curr_fam is not None:
                curr_fam.setdefault('CHIL', []).append(arguments)
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

individuals.sort(key=lambda x: x['ID'])
families.sort(key=lambda x: x['ID'])

ind_table = PrettyTable()
ind_table.field_names = ["ID", "Name", "Sex", "Birth", "Death", "Age", "Alive", "Children", "Spouse"]


for ind in individuals:
    age = calculate_age(ind.get('BIRT', ''), ind.get('DEAT', ''))
    alive = 'True'if not ind.get('DEAT') else 'False'
    id_to_name = {ind['ID']: na_if_empty(ind.get('NAME', '')) for ind in individuals}


    children_ids = []
    spouse_ids = []

    for fam in families:
        if fam.get('HUSB', '').strip('@') == ind['ID']:
            children_ids.extend([c.strip('@') for c in fam.get('CHIL', [])])
            spouse_ids.append(fam.get('WIFE', '').strip('@'))
        elif fam.get('WIFE', '').strip('@') == ind['ID']:
            children_ids.extend(fam.get('CHIL', []))
            spouse_ids.append(fam.get('HUSB', '').strip('@'))

    children_str = '{' + ', '.join(children_ids) + '}' if children_ids else '{}'
    spouse_str = '{' + ', '.join(spouse_ids) + '}' if spouse_ids else '{}'


    ind_table.add_row([
        ind.get('ID', ''),
        ind.get('NAME', ''),
        ind.get('SEX', ''),
        ind.get('BIRT', ''),
        ind.get('DEAT', ''),
        age,
        alive,
        children_str,
        spouse_str
    ])

print("\nIndividuals:")
print(ind_table)

fam_table = PrettyTable()
fam_table.field_names = ["ID", "Married", "Divorced", "Husband ID", "Husband Name", "Wife ID", "Wife Name", "Children"]


for fam in families:

    children = [c.strip('@') for c in fam.get('CHIL', [])]
    children_str = '{' + ', '.join(children) + '}' if children else 'N/A'

    husband_id = fam.get('HUSB', '').strip('@')
    wife_id = fam.get('WIFE', '').strip('@')


    fam_table.add_row([
        na_if_empty(fam.get('ID', '')),
        na_if_empty(fam.get('MARR', '')),
        na_if_empty(fam.get('DIV', '')),
        na_if_empty(husband_id),
        id_to_name.get(husband_id, 'N/A'),
        na_if_empty(wife_id),
        id_to_name.get(wife_id, 'N/A'),
        children_str
    ])

print("\nFamilies:")
print(fam_table)

