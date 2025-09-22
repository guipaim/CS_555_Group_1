from prettytable import PrettyTable


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

def parse_line(line):
    parts = line.strip().split(' ', 2)
    level = parts[0]
    tag = parts[1]
    valid = 'Y' if tag in supported_tags else 'N'
    arguments = parts[2] if len(parts) > 2 else ''

    return level, tag, valid, arguments

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
ind_table.field_names = ["ID", "Name", "Sex", "Birth", "Death"]

for ind in individuals:
    ind_table.add_row([
        ind.get('ID', ''),
        ind.get('NAME', ''),
        ind.get('SEX', ''),
        ind.get('BIRT', ''),
        ind.get('DEAT', '')
    ])

print("\nIndividuals:")
print(ind_table)

fam_table = PrettyTable()
fam_table.field_names = ["ID", "Husband", "Wife", "Marriage", "Divorce", "Children"]

for fam in families:

    children = fam.get('CHIL', [])
    children_str = '{' + ', '.join(children) + '}' if children else '{}'

    fam_table.add_row([
        fam.get('ID', ''),
        fam.get('HUSB', ''),
        fam.get('WIFE', ''),
        fam.get('MARR', ''),
        fam.get('DIV', ''),
        children_str
    ])

print("\nFamilies:")
print(fam_table)

