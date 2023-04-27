import molecule
import MolDisplay
import sqlite3
import os


class Database:

    def __init__(self, reset=False):

        # If reset is set to true, delete files:
        if reset and os.path.exists("molecules.db"):
            os.remove("molecules.db")
        # Establish fresh database connection:
        self.con = sqlite3.connect("molecules.db")

    def create_tables(self):

        # SETTING UP ALL TABLES WITH THEIR RESPECTIVE VALUES:
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS Elements (
                ELEMENT_NO INTEGER NOT NULL,
                ELEMENT_CODE VARCHAR(3) NOT NULL,
                ELEMENT_NAME VARCHAR(32) NOT NULL,
                COLOUR1 CHAR(6) NOT NULL,
                COLOUR2 CHAR(6) NOT NULL,
                COLOUR3 CHAR(6) NOT NULL,
                RADIUS DECIMAL(3) NOT NULL,
                PRIMARY KEY (ELEMENT_CODE)
            )
            """)

        self.con.execute("""
            CREATE TABLE IF NOT EXISTS Atoms (
                ATOM_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                ELEMENT_CODE VARCHAR(3) NOT NULL,
                X DECIMAL(7, 4) NOT NULL,
                Y DECIMAL(7, 4) NOT NULL,
                Z DECIMAL(7, 4) NOT NULL,
                FOREIGN KEY (ELEMENT_CODE) REFERENCES Elements(ELEMENT_CODE)
            )
            """)

        self.con.execute("""
            CREATE TABLE IF NOT EXISTS Bonds (
                BOND_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                A1 INTEGER NOT NULL,
                A2 INTEGER NOT NULL,
                EPAIRS INTEGER NOT NULL
            )
            """)

        self.con.execute("""
            CREATE TABLE IF NOT EXISTS Molecules (
                MOLECULE_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                NAME TEXT UNIQUE NOT NULL
            )
            """)

        self.con.execute("""
            CREATE TABLE IF NOT EXISTS MoleculeAtom (
                MOLECULE_ID INTEGER NOT NULL,
                ATOM_ID INTEGER NOT NULL,
                PRIMARY KEY (MOLECULE_ID, ATOM_ID),
                FOREIGN KEY (MOLECULE_ID) REFERENCES Molecules(MOLECULE_ID),
                FOREIGN KEY (ATOM_ID) REFERENCES Atoms(ATOM_ID)
            )
            """)

        self.con.execute("""
            CREATE TABLE IF NOT EXISTS MoleculeBond (
                MOLECULE_ID INTEGER NOT NULL,
                BOND_ID INTEGER NOT NULL,
                PRIMARY KEY (MOLECULE_ID, BOND_ID),
                FOREIGN KEY (MOLECULE_ID) REFERENCES Molecules(MOLECULE_ID),
                FOREIGN KEY (BOND_ID) REFERENCES Bonds(BOND_ID)
            )
            """)

        # Commiting changes:
        self.con.commit()

    def __setitem__(self, table, values):
        self.con.execute(f"""INSERT INTO {table} VALUES {values} """)
        # Commiting changes:
        self.con.commit()

    def add_atom(self, molname, atom):

        # Inserting atom attributes into table:
        self.con.execute("INSERT INTO Atoms (ELEMENT_CODE, X, Y, Z) VALUES (?, ?, ?, ?)",
                         (atom.element, atom.x, atom.y, atom.z))
        # Getting atom ID:
        atom_id = self.con.execute(
            "SELECT MAX(ATOM_ID) FROM Atoms WHERE ELEMENT_CODE = ?", (atom.element,)).fetchone()[0]

        # Getting molecule ID:
        mol_id = self.con.execute(
            "SELECT MOLECULE_ID FROM Molecules WHERE NAME = ?", (molname,)).fetchone()[0]

        # print(f" MOL_ID: {mol_id}   ATOM_ID: {atom_id}")

        # linking atom to molecule table so it doesnt get lost:
        self.con.execute(
            "INSERT INTO MoleculeAtom (MOLECULE_ID, ATOM_ID) VALUES (?, ?)", (mol_id, atom_id))

        # Commiting changes:
        self.con.commit()

    def add_bond(self, molname, bond):

        # Inserting atom attributes into table:
        self.con.execute(
            "INSERT INTO Bonds (A1, A2, EPAIRS) VALUES (?, ?, ?)", (bond.a1, bond.a2, bond.epairs))

        # Getting bond ID:
        bond_id = self.con.execute(
            "SELECT BOND_ID FROM Bonds WHERE A1 = ? AND A2 = ? AND EPAIRS = ?", (bond.a1, bond.a2, bond.epairs)).fetchone()[0]

        # Getting molecule ID:
        mol_id = self.con.execute(
            "SELECT MOLECULE_ID FROM Molecules WHERE NAME = ?", (molname,)).fetchone()[0]

        # linking BOND to molecule table so it doesnt get lost:
        self.con.execute(
            "INSERT INTO MoleculeBond (MOLECULE_ID, BOND_ID) VALUES (?, ?)", (mol_id, bond_id))

        # Commiting changes:
        self.con.commit()

    def add_molecule(self, name, fp):

        # Creating moldisplay.molecule object:
        mol = MolDisplay.Molecule()

        # Calling its parse function on fp:
        mol.parse(fp)

        # Adding entry to Molecules table:
        self.con.execute("INSERT INTO Molecules (NAME) VALUES (?)", (name,))

        # Calling add_Atom and add_bond on database for each atom and bond returned
        for i in range(mol.atom_no):
            self.add_atom(name, mol.get_atom(i))

        for i in range(mol.bond_no):
            self.add_bond(name, mol.get_bond(i))

        # Commiting changes:
        self.con.commit()


# PART 2 BEGINS HERE:


    def load_mol(self, name):
        # print(name)

        # create molecule:
        mol = MolDisplay.Molecule()

        # Retrieve all atoms in DB (USING JOINS):
        atoms = self.con.execute("""
                    SELECT Atoms.*
                    FROM Molecules
                    JOIN MoleculeAtom ON Molecules.MOLECULE_ID = MoleculeAtom.MOLECULE_ID
                    JOIN Atoms ON MoleculeAtom.ATOM_ID = Atoms.ATOM_ID
                    WHERE Molecules.NAME = ?
                    ORDER BY Atoms.ATOM_ID ASC
               """, (name,)).fetchall()

        # Append atoms to mol object:
        for value in atoms:
            mol.append_atom(value[1], value[2], value[3], value[4])

        # Retrieve all bonds in DB (USING JOINS):
        bonds = self.con.execute("""
                    SELECT Bonds.*
                    FROM Molecules
                    JOIN MoleculeBond ON Molecules.MOLECULE_ID = MoleculeBond.MOLECULE_ID
                    JOIN Bonds ON MoleculeBond.BOND_ID = Bonds.BOND_ID
                    WHERE Molecules.NAME = ?
                    ORDER BY Bonds.BOND_ID ASC
               """, (name,)).fetchall()

        print(bonds)
        
        # Append atoms to mol object:
        for value in bonds:
            mol.append_bond(value[1], value[2], value[3])
            

        # Commiting changes:
        self.con.commit()

        return mol

    def radius(self):

        # Creating dic:
        rad = {}

        # Assigning all values req for radius dic by query:
        test = self.con.execute("""
                SELECT ELEMENT_CODE, RADIUS
                FROM Elements
                """).fetchall()

        # print(test)

        # Assigning dic values:
        for i in test:
            rad[i[0]] = i[1]
            # print(rad)

        # Commiting changes:
        self.con.commit()

        return rad

    def element_name(self):

        # Creating dic:
        name = {}

        # Assigning all values requred for dic by query:
        get_Values = self.con.execute("""
                    SELECT ELEMENT_CODE, ELEMENT_NAME
                    FROM Elements
                    """).fetchall()

        # Assigning dic values:
        for i in get_Values:
            name[i[0]] = i[1]
            # print(name)

        # Commiting changes:
        self.con.commit()

        return name

    def radial_gradients(self):

        # Query statement:
        get_Values = self.con.execute("""
                SELECT ELEMENT_NAME, COLOUR1, COLOUR2, COLOUR3
                FROM Elements
        """).fetchall()
        strings = []

        # Python String required to return:
        radialGradientSVG = """
            <radialGradient id="%s" cx="-50%%" cy="-50%%" r="220%%" fx="20%%" fy="20%%">
                <stop offset="0%%" stop-color="#%s"/>
                <stop offset="50%%" stop-color="#%s"/>
                <stop offset="100%%" stop-color="#%s"/>
            </radialGradient>"""

        # Iterate through and assign the list of values to radialGradientSVG:
        for value in get_Values:
            temp = radialGradientSVG % (value[0], value[1], value[2], value[3])
            strings.append(temp)

        # Commiting changes:
        self.con.commit()

        return ''.join(strings)


# TESTING
# if __name__ == "__main__":


# # TESTING P1:
# if __name__ == "__main__":
#     db = Database(reset=True)
#     db.create_tables()
#     db['Elements'] = (1, 'H', 'Hydrogen', 'FFFFFF', '050505', '020202', 25)
#     db['Elements'] = (6, 'C', 'Carbon', '808080', '010101', '000000', 40)
#     db['Elements'] = (7, 'N', 'Nitrogen', '0000FF', '000005', '000002', 40)
#     db['Elements'] = (8, 'O', 'Oxygen', 'FF0000', '050000', '020000', 40)
#     fp = open('water-3D-structure-CT1000292221.sdf')
#     db.add_molecule('Water', fp)
#     # display tables
#     print(db.con.execute("SELECT * FROM Elements;").fetchall())
#     print(db.con.execute("SELECT * FROM Molecules;").fetchall())
#     print(db.con.execute("SELECT * FROM Atoms;").fetchall())
#     print(db.con.execute("SELECT * FROM Bonds;").fetchall())
#     print(db.con.execute("SELECT * FROM MoleculeAtom;").fetchall())
#     print(db.con.execute("SELECT * FROM MoleculeBond;").fetchall())


# # TESTING P2:
# if __name__ == "__main__":
#     mole = MolDisplay.Molecule()
#     db = Database(reset=False)  # or use default
#     MolDisplay.radius = db.radius()
#     MolDisplay.element_name = db.element_name()
#     MolDisplay.header += db.radial_gradients()
#     for molecule in ['Water']:
#         mol = db.load_mol(molecule)
#         mol.sort()
#         fp = open(molecule + ".svg", "w")
#         fp.write(mol.svg())
#         fp.close()
