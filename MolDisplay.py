import molecule

# radius = {'H': 25,
#           'C': 40,
#           'O': 40,
#           'N': 40,
#           }

# element_name = {'H': 'grey',
#                 'C': 'black',
#                 'O': 'red',
#                 'N': 'blue',
#                 }

header = """<svg version="1.1" width="1000" height="1000" xmlns="http://www.w3.org/2000/svg">"""

footer = """</svg>"""

offsetx = 500

offsety = 500


# ATOM CLASS:
class Atom:

    # Setting values of atom in molecule.c to "self.c_atom"
    # Setting z value of the atom in molecule.c to "self.z"
    def __init__(self, c_atom):
        self.c_atom = c_atom
        self.z = c_atom.z

    # String method used for debugging purposes:
    def __str__(self):
        return f"{self.c_atom.x}, {self.c_atom.y}, {self.c_atom.z}, {self.c_atom.element}"

    # SVG method used to create the position values of the atoms
    def svg(self):

        # Calculating x and y locations with their respecitve offset and scale size:
        x = self.c_atom.x * 100.00 + offsetx
        y = self.c_atom.y * 100.00 + offsety

        # Assigning radius value based on the atom:
        rad = radius[self.c_atom.element]

        # Assigning element colour based on the element:
        col = element_name[self.c_atom.element]

        return '  <circle cx="%.2f" cy="%.2f" r="%d" fill="url(#%s)"/>\n' % (x, y, rad, col)


# BOND CLASS:
class Bond:

    # Setting values of bond in molecule.c to "self.c_bond"
    # Setting z value of the bond in molecule.c to "self.z"
    def __init__(self, c_bond):
        self.c_bond = c_bond
        self.z = c_bond.z

    # String used for debugging purposes:
    def __str__(self):

        return f"{self.c_bond.a1}, {self.c_bond.a2}, {self.c_bond.epairs}"

    # SVG method used to calculate the points of the molecule:

    def svg(self):

        # Setting dx and dy values:
        dx = self.c_bond.dx
        dy = self.c_bond.dy

        # X & Y coordinates of corner 1:
        p1 = self.c_bond.x1 * 100.0 + offsetx - dy * 10
        p2 = self.c_bond.y1 * 100.0 + offsety + dx * 10

        # X & Y coordinates of corner 2:
        p3 = self.c_bond.x1 * 100.0 + offsetx + dy * 10
        p4 = self.c_bond.y1 * 100.0 + offsety - dx * 10

        # X & Y coordinates of corner 3:
        p5 = self.c_bond.x2 * 100.0 + offsetx + dy * 10
        p6 = self.c_bond.y2 * 100.0 + offsety - dx * 10

        # X & Y coordinates of corner 4:
        p7 = self.c_bond.x2 * 100.0 + offsetx - dy * 10
        p8 = self.c_bond.y2 * 100.0 + offsety + dx * 10

        return '  <polygon points="%.2f,%.2f %.2f,%.2f %.2f,%.2f %.2f,%.2f" fill="green"/>\n' % (
            p1, p2,
            p3, p4,
            p5, p6,
            p7, p8
        )


# MOLECULE CLASS:
class Molecule(molecule.molecule):
    # String used for debugging purposes:
    def __str__(self):
        str_atoms = []
        str_bonds = []
        for i in range(self.atom_no):
            str_atoms.append(print(Atom(self.get_atom(i))))
        for j in range(self.bond_no):
            str_bonds.append(print(Bond(self.get_bond(j))))

        return ""

    # SVG method used to create and sort a list of all the atoms and bonds by their respecitve z values, and return the "header + the list + the footer"
    def svg(self):
        # Defined Lists & Variables:
        list_atom = []
        list_bond = []
        sorted_list = []
        temp_body = ""


        # Appending Bonds to bond list:
        for y in range(self.bond_no):
            bond = self.get_bond(y)
            NB = Bond(bond)
            list_bond.append(NB)

        # Appending Atoms to atom list:
        for x in range(self.atom_no):
            atom = self.get_atom(x)
            NA = Atom(atom)
            list_atom.append(NA)

        
        #Printing both lists to test:
        # print(list_atom)
        # print(list_bond)

        x = 0
        y = 0

        while x < self.atom_no and y < self.bond_no:

            if list_bond[y].z > list_atom[x].z:
                sorted_list.append(list_atom[x])
                x += 1
            else:
                sorted_list.append(list_bond[y])
                y += 1
        
        while x < self.atom_no:
            sorted_list.append(list_atom[x])
            x += 1
        while y < self.bond_no:
            sorted_list.append(list_bond[y])
            y += 1
        
        for x in range (len(sorted_list)):
            temp_body += sorted_list[x].svg()
        
        svg = header + temp_body + footer

        return svg

    # Method used to parse through file and append atoms and bonds to molecule object

    def parse(self, file):
        
        # Reading in atom_no & bond_no:
        test = file.readlines()
        if len(test) > 4:
            information = test[3]
            atomNum = int(information.split()[0])
            bondNum = int(information.split()[1])
            # print(information)

            ind = 4
            # 4 - 8
            for i in range(atomNum):
                line = test[ind]
                # print("ind is: ", ind)

                # print(line)
                x = float(line.split()[0])
                y = float(line.split()[1])
                z = float(line.split()[2])
                element = str(line.split()[3])
                # print(element)
                self.append_atom(element, x, y, z)
                ind = ind + 1
                # print("safsdaf")

            flag = atomNum + 4

            for j in range(bondNum):
                line = test[flag]
                print(line)
                a1 = int(line.split()[0])
                a2 = int(line.split()[1])
                epairs = int(line.split()[2])
                self.append_bond(a1 - 1, a2 - 1, epairs)
                flag = flag + 1
