#include "mol.h"

void atomset(atom *atom, char element[3], double *x, double *y, double *z)
{

    strcpy(atom->element, element);
    atom->x = *x;
    atom->y = *y;
    atom->z = *z;
}

void atomget(atom *atom, char element[3], double *x, double *y, double *z) // HOW TO TEST:
{
    strcpy(element, atom->element);
    *x = atom->x;
    *y = atom->y;
    *z = atom->z;
}

void bondset(bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs)
{
    bond->atoms = *atoms;
    bond->a1 = *a1;
    bond->a2 = *a2;
    bond->epairs = *epairs;
    compute_coords(bond);
}

void bondget(bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs)
{
    *atoms = bond->atoms;
    *a1 = bond->a1;
    *a2 = bond->a2;
    *epairs = bond->epairs;
}

molecule *molmalloc(unsigned short atom_max, unsigned short bond_max)
{

    molecule *newMolecule = (molecule *)malloc(sizeof(molecule));

    // Error checking newMolecule:
    if (newMolecule == NULL)
    {

        printf("ERROR! Something went wrong mallocing memory to newMolecule (molmalloc)!");
        return NULL;
    }

    newMolecule->atom_max = atom_max;
    newMolecule->atom_no = 0;
    newMolecule->atoms = malloc(sizeof(atom) * atom_max);
    newMolecule->atom_ptrs = malloc(sizeof(atom *) * atom_max);

    newMolecule->bond_max = bond_max;
    newMolecule->bond_no = 0;
    newMolecule->bonds = malloc(sizeof(bond) * bond_max);
    newMolecule->bond_ptrs = malloc(sizeof(bond *) * bond_max);

    // Error checking atoms:
    if (newMolecule->atoms == NULL)
    {

        printf("ERROR! Something went wrong mallocing memory to newMolecule->atoms (molmalloc)!");
        return NULL;
    }

    // Error checking atom_ptrs:
    if (newMolecule->atom_ptrs == NULL)
    {

        printf("ERROR! Something went wrong mallocing memory to newMolecule->atom_ptrs (molmalloc)!");
        return NULL;
    }

    // Error checking bonds:
    if (newMolecule->bonds == NULL)
    {

        printf("ERROR! Something went wrong mallocing memory to newMolecule->bonds (molmalloc)!");
        return NULL;
    }

    // Error checking bond_ptrs:
    if (newMolecule->bond_ptrs == NULL)
    {

        printf("ERROR! Something went wrong mallocing memory to newMolecule->bond_ptrs (molmalloc)!");
        return NULL;
    }

    return newMolecule;
}

molecule *molcopy(molecule *src)
{

    molecule *newMol = molmalloc(src->atom_max, src->bond_max);

    if (newMol == NULL)
    {

        printf("ERORR: Something went wrong mallocing memory (molcopy)!");
        return NULL;
    }

    // Values of atom_max, atom_no, bond_max, bond_no, copied from src
    newMol->atom_max = src->atom_max;
    newMol->bond_max = src->bond_max;

    // add atoms and bonds from src to newMol:
    for (int i = 0; i < src->atom_no; i++)
    {
        molappend_atom(newMol, &src->atoms[i]);
    }

    for (int i = 0; i < src->bond_no; i++)
    {
        molappend_bond(newMol, &src->bonds[i]);
    }

    return newMol;
}

void molfree(molecule *ptr)
{

    free(ptr->atoms);
    free(ptr->atom_ptrs);
    free(ptr->bonds);
    free(ptr->bond_ptrs);
    free(ptr);
}

void molappend_atom(molecule *molecule, atom *atom)
{

    // check if atom_max is 0; if it is then set atom_max = 1:
    if (molecule->atom_max == 0)
    {

        molecule->atom_max = 1;
    }

    // Checking to see if the array is full, then doubling the size if it has reached the maximum size: //LOOOOK INTO
    else if (molecule->atom_max <= molecule->atom_no)
    {

        molecule->atom_max *= 2;
    }

    // Reallocate memory for atoms & atom_ptrs array

    // Checking atoms
    molecule->atoms = realloc(molecule->atoms, sizeof(*atom) * molecule->atom_max);

    // Checking if something went wrong:
    if (molecule->atoms == NULL)
    {

        printf("ERROR: SOMETHING WENT WRONG REALLOCATING MEMORY FOR ATOMS!!");
        // Exit if something went wrong:
        exit(1);
    }

    // Checking atoms_ptrs:
    molecule->atom_ptrs = realloc(molecule->atom_ptrs, sizeof(*atom) * molecule->atom_max);

    if (molecule->atom_ptrs == NULL)
    {

        printf("ERROR: SOMETHING WENT WRONG REALLOCATING MEMORY FOR ATOMS!!");
        // Exit if something went wrong:
        exit(1);
    }

    // UPDATED!!!! After reallocing enough memory for atom_ptrs, pointers set to point to new corresponding atoms in atoms array (old ones may have been freed):
    for (int i = 0; i < molecule->atom_no; i++)
    {

        molecule->atom_ptrs[i] = &molecule->atoms[i];
    }

    // Adding new atom to the atom array & incrementing the atom number:
    atomset(molecule->atoms + molecule->atom_no, atom->element, &atom->x, &atom->y, &atom->z);
    // getting addresses:
    molecule->atom_ptrs[molecule->atom_no] = &(molecule->atoms[molecule->atom_no]);
    molecule->atom_no++;
}

void molappend_bond(molecule *molecule, bond *bond)
{

    // check if bond_max is 0; if it is then set bond_max = 1:
    if (molecule->bond_max == 0)
    {

        molecule->bond_max = 1;
    }

    // Checking to see if the array is ful, then doubling the size if it has reached the maximum size:
    else if (molecule->bond_max <= molecule->bond_no)
    {

        molecule->bond_max *= 2;
    }

    // Reallocate memory for bonds & bond_ptrs array
    // Checking bonds
    molecule->bonds = realloc(molecule->bonds, sizeof(*bond) * molecule->bond_max);

    // Checking if something went wrong:
    if (molecule->bonds == NULL)
    {

        printf("ERROR: SOMETHING WENT WRONG REALLOCATING MEMORY FOR ATOMS!!");
        // Exit if something went wrong:
        exit(1);
    }

    // Checking bonds_ptrs:
    molecule->bond_ptrs = realloc(molecule->bond_ptrs, sizeof(*bond) * molecule->bond_max);

    // UPDATED!!!! After reallocing enough memory for bonds_ptrs, pointers set to point to new corresponding bonds in bond array (old ones may have been freed):
    for (int i = 0; i < molecule->bond_no; i++)
    {

        molecule->bond_ptrs[i] = &molecule->bonds[i];
    }

    // Checking if something went wrong:
    if (molecule->bond_ptrs == NULL)
    {

        printf("ERROR: SOMETHING WENT WRONG REALLOCATING MEMORY FOR ATOMS_PTR!!");
        // Exit if something went wrong:
        exit(1);
    }

    // Adding new bond to the bond array & incrementing the bond number:
    bondset(&molecule->bonds[molecule->bond_no], &bond->a1, &bond->a2, &bond->atoms, &bond->epairs);
    // getting addresses:
    molecule->bond_ptrs[molecule->bond_no] = &(molecule->bonds[molecule->bond_no]);
    molecule->bond_no++;
}

int compareatomptrs(const void *a, const void *b)
{
    atom **atom_x = (atom **)a;
    atom **atom_y = (atom **)b;

    // Used to compare A and B

    return (*atom_x)->z - (*atom_y)->z;
}

int bond_comp(const void *a, const void *b)
{

    // Find the average z value of bonds by taking average z value of 2 atoms:

    // Deference values of a and b into bond x and bond y:
    bond **bond_x = (bond **)a;
    bond **bond_y = (bond **)b;

    // Find average z value of each bond using a1 & a2:
    double avgBondA = ((*bond_x)->z + ((*bond_x)->z)) / 2;
    double avgBondB = ((*bond_y)->z + ((*bond_y)->z)) / 2;

    // Check if average z value of a is less than (-1), greater than (1), or equal to (0) the z value of bond b:
    return avgBondA - avgBondB;
}

void molsort(molecule *molecule)
{
    qsort(molecule->atom_ptrs, molecule->atom_no, sizeof(atom *), compareatomptrs);
    qsort(molecule->bond_ptrs, molecule->bond_no, sizeof(bond *), bond_comp);
}

void xrotation(xform_matrix xform_matrix, unsigned short deg)
{

    xform_matrix[0][0] = 1;
    xform_matrix[1][0] = 0;
    xform_matrix[2][0] = 0;
    xform_matrix[0][1] = 0;
    xform_matrix[1][1] = cos((deg) * (M_PI / 180));
    xform_matrix[2][1] = sin((deg) * (M_PI / 180));
    xform_matrix[0][2] = 0;
    xform_matrix[1][2] = -sin((deg) * (M_PI / 180));
    xform_matrix[2][2] = cos((deg) * (M_PI / 180));
}

void yrotation(xform_matrix xform_matrix, unsigned short deg)
{

    xform_matrix[0][0] = cos((deg) * (M_PI / 180));
    xform_matrix[1][0] = 0;
    xform_matrix[2][0] = -sin((deg) * (M_PI / 180));
    xform_matrix[0][1] = 0;
    xform_matrix[1][1] = 1;
    xform_matrix[2][1] = 0;
    xform_matrix[0][2] = sin((deg) * (M_PI / 180));
    xform_matrix[1][2] = 0;
    xform_matrix[2][2] = cos((deg) * (M_PI / 180));
}

void zrotation(xform_matrix xform_matrix, unsigned short deg)
{

    xform_matrix[0][0] = cos((deg) * (M_PI / 180));
    xform_matrix[1][0] = sin((deg) * (M_PI / 180));
    xform_matrix[2][0] = 0;
    xform_matrix[0][1] = -sin((deg) * (M_PI / 180));
    xform_matrix[1][1] = cos((deg) * (M_PI / 180));
    xform_matrix[2][1] = 0;
    xform_matrix[0][2] = 0;
    xform_matrix[1][2] = 0;
    xform_matrix[2][2] = 1;
}

void mol_xform(molecule *molecule, xform_matrix matrix)
{
    double x, y, z;
    for (int i = 0; i < molecule->atom_no; i++)
    {
        // Setting up temp values for x,y,z to not constantly keep updating the current ones (took me awhile to find out this mistake.)
        x = molecule->atoms[i].x;
        y = molecule->atoms[i].y;
        z = molecule->atoms[i].z;

        molecule->atoms[i].x = (x * matrix[0][0]) + (y * matrix[0][1]) + (z * matrix[0][2]);
        molecule->atoms[i].y = (x * matrix[1][0]) + (y * matrix[1][1]) + (z * matrix[1][2]);
        molecule->atoms[i].z = (x * matrix[2][0]) + (y * matrix[2][1]) + (z * matrix[2][2]);
    }

    //Applying compute_coords to each bond in molecule:
    for (int i = 0; i < molecule->bond_no; i++)
        compute_coords(&molecule->bonds[i]);
}

void compute_coords(bond *bond){


    atom *tempAtom1 = &bond->atoms[bond->a1];
    atom *tempAtom2 = &bond->atoms[bond->a2];


    bond->x1 = tempAtom1->x;
    bond->x2 = tempAtom2->x;

    bond->y1 = tempAtom1->y;
    bond->y2 = tempAtom2->y;

    bond->z = (tempAtom1->z + tempAtom2->z) / 2; //avg of both atoms z values
    bond->len = sqrt( pow(tempAtom2->x - tempAtom1->x, 2) + pow(tempAtom2->y - tempAtom1->y, 2) );

    bond->dx = (tempAtom2->x - tempAtom1->x) / bond->len;
    bond->dy = (tempAtom2->y - tempAtom1->y) / bond->len;

}
