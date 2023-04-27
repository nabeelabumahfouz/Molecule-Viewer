
#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <math.h>
#include <stdlib.h>
#define M_PI 3.14159265358979323846


/*
element is a null-terminated string representing the element name of the atom (e.g. Na for
sodium). x, y, and z are double precision floating point numbers describing the position in
Angstroms (Å) of the atom relative to a common origin for a molecule.
*/
typedef struct atom
{
    char element[3];
    double x, y, z;
} atom;

/*
bond defines a structure that represents a co-valent bond between two atoms. a1 and a2 are
pointers to the two atoms in the co-valent bond. epairs is the number of electron pairs in the
bond (i.e. epairs=2 represents a double bond). The atoms pointed to by a1 and a2 will be
allocated and stored elsewhere, so it will never be necessary to free a1 or a2.
*/
typedef struct bond
{
    unsigned short a1, a2;
    unsigned char epairs;
    atom *atoms;
    double x1, x2, y1, y2, z, len, dx, dy;
} bond;

/*
molecule represents a molecule which consists of zero or more atoms, and zero or more bonds.
atom_max is a non-negative integer that records the dimensionality of an array pointed to by
atoms. atom_no is the number of atoms currently stored in the array atoms. Note atom_no
must never be larger than atom_max. You will be responsible for allocating enough memory to
the atoms pointer. bond_max is a non-negative integer that records the dimensionality of an
array pointed to by bonds. bond_no is the number of bonds currently stored in the array bonds.
Note bond_no must never be larger than bond_max. You will be responsible for allocating
enough memory to the bonds pointer. atom_ptrs and bond_ptrs are arrays of pointers.
Their dimensionalities will correspond to the atoms and bonds arrays, respectively. These
pointers in these pointer arrays will be initialized to point to their corresponding structures.
E.g. atom_ptrs[0] will point to atoms[0]. Later we will sort the order of the pointers to allow
for an alternate traversal (ordering) of the atoms/ bonds.
*/
typedef struct molecule
{
    unsigned short atom_max, atom_no;
    atom *atoms, **atom_ptrs;
    unsigned short bond_max, bond_no;
    bond *bonds, **bond_ptrs;
} molecule;

/*
xform_matrix reprents a 3-d affine transformation matrix (an extension of the 2-d affine
transformation you saw in the first lab).
*/
typedef double xform_matrix[3][3];

typedef struct mx_wrapper
{
  xform_matrix xform_matrix;
} mx_wrapper;
/* This function should copy the values pointed to by element, x, y, and z into the atom stored at
atom. You may assume that sufficient memory has been allocated at all pointer addresses.
Note that using pointers for the function “inputs”, x, y, and z, is done here to match the
function arguments of atomget
*/
void atomset(atom *atom, char element[3], double *x, double *y, double *z);

/*
void atomget( atom *atom, char element[3], double *x, double *y, double *z );
This function should copy the values in the atom stored at atom to the locations pointed to by
element, x, y, and z. You may assume that sufficient memory has been allocated at all pointer
addresses. Note that using pointers for the function “input”, atom, is done here to match the
function arguments of atomset.
*/
void atomget(atom *atom, char element[3], double *x, double *y, double *z);

/*
This function should copy the values a1, a2 and epairs into the corresponding structure
attributes in bond. You may assume that sufficient memory has been allocated at all pointer
addresses. Note you are not copying atom structures, only the addresses of the atom
structures.
*/
void bondset( bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs );
/*
This function should copy the structure attributes in bond to their corresponding arguments:
a1, a2 and epairs. You may assume that sufficient memory has been allocated at all pointer
addresses. Note you are not copying atom structures, only the addresses of the atom
structures
*/
void bondget( bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs );
/*
This function should return the address of a malloced area of memory, large enough to hold a
molecule. The value of atom_max should be copied into the structure; the value of atom_no in
the structure should be set to zero; and, the arrays atoms and atom_ptrs should be malloced
to have enough memory to hold atom_max atoms and pointers (respectively). The value of
bond_max should be copied into the structure; the value of bond_no in the structure should be
set to zero; and, the arrays bonds and bond_ptrs should be malloced to have enough memory
to hold bond_max bonds and pointers (respectively)
*/
molecule *molmalloc(unsigned short atom_max, unsigned short bond_max);

/*
This function should return the address of a malloced area of memory, large enough to hold a
molecule. Additionally, the values of atom_max, atom_no, bond_max, bond_no should be
copied from src into the new structure. Finally, the arrays atoms, atom_ptrs, bonds and
bond_ptrs must be allocated to match the size of the ones in src. You should re-use (i.e. call)
the molmalloc function in this function.
*/
molecule *molcopy(molecule *src);

/*
This function should free the memory associated with the molecule pointed to by ptr. This
includes the arrays atoms, atom_ptrs, bonds, bond_ptrs
*/
void molfree(molecule *ptr);

/* This function should copy the data pointed to by atom to the first “empty” atom in atoms in the
molecule pointed to by molecule, and set the first “empty” pointer in atom_ptrs to the same
atom in the atoms array incrementing the value of atom_no. If atom_no equals atom_max, then
atom_max must be incremented, and the capacity of the atoms, and atom_ptrs arrays
increased accordingly. If atom_max was 0, it should be incremented to 1, otherwise it should be
doubled. Increasing the capacity of atoms, and atom_ptrs should be done using realloc so
that a larger amount of memory is allocated and the existing data is copied to the new location
*/
void molappend_atom(molecule *molecule, atom *atom);

/* This function should operate like that molappend_atom function, except for bonds*/
void molappend_bond(molecule *molecule, bond *bond);

/* This function should sort the atom_ptrs array in place in order of increasing z value. I.e.
atom_ptrs[0] should point to the atom that contains the lowest z value and
atom_ptrs[atom_no-1] should contain the highest z value. It should also sort the bond_ptrs
array in place in order of increasing “ z value”. Since bonds don’t have a z attribute, their z
value is assumed to be the average z value of their two atoms. I.e. bond_ptrs[0] should point
to the bond that has the lowest z value and bond_ptrs[atom_no-1] should contain the highest
z value.Hint: use qsort.
*/
void molsort(molecule *molecule);

/* This function will allocate, compute, and return an affine transformation matrix corresponding
to a rotation of deg degrees around the x-axis. This matrix must be freed by the user when no-
longer needed.
*/
void xrotation(xform_matrix xform_matrix, unsigned short deg);

/* This function will allocate, compute, and return an affine transformation matrix corresponding
to a rotation of deg degrees around the y-axis. This matrix must be freed by the user when no-
longer needed.
*/
void yrotation(xform_matrix xform_matrix, unsigned short deg);

/* This function will allocate, compute, and return an affine transformation matrix corresponding
to a rotation of deg degrees around the z-axis. This matrix must be freed by the user when no-
longer needed. */
void zrotation(xform_matrix xform_matrix, unsigned short deg);

/* This function will apply the transformation matrix to all the atoms of the molecule by
performing a vector matrix multiplication on the x, y, z coordinates*/
void mol_xform(molecule *molecule, xform_matrix matrix);

//Helper function created to aid in Qsort of atom ptrs:
int compareatomptrs(const void *a, const void *b);

//Helper function aided to create in Qsort of bond ptrs:
int bond_comp(const void *a, const void *b);


//A2 ADDITIONS:

/* This function should compute the z, x1, y1, x2, y2, len, dx, and dy values of the bond and set 
them in the appropriate structure member variables*/
void compute_coords( bond *bond );


void mol_xform( molecule *molecule, xform_matrix matrix );


// //A4 ADDITIONS:
// typedef struct rotations
// {
//   molecule *x[72];
//   molecule *y[72];
//   molecule *z[72];
// } rotations;


