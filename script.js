$(document).ready(function () {
    console.log("JQUERY LOADED SUCCESSFULLY")
    function showError(input, message) {
        alert(message);
        input.focus();
    }

    //Checks for pos integer ONLY:
    function isPosInt(input) {
        return /^\d+$/.test(input.val()) && parseInt(input.val()) > 0;
    }

    //Checks for pos integer AND FLOAT:
    function isPosIntandFloat(input) {
        return /^\d+(\.\d+)?$/.test(input.val()) && parseFloat(input.val()) > 0;
    }

    //Checks to see if isalpha:
    function isText(input) {
        return /^[A-Za-z]+$/.test(input.val());
    }


    //Checks for pos integer AND FLOAT:
    function isPosIntandFloatUPDATED(input) {
        return /^\d+(\.\d+)?$/.test(input.val()) && parseFloat(input.val()) >= 0;
    }




    //Class for getting all element info, validating it, and providing it to server:
    $('#elementForm').submit(function (event) {

        //Prevents the form from submitting by default:
        event.preventDefault();

        //Input Values:
        var elementFormData = new FormData();
        let elementNumInput = $("#ElementNum");
        let elementCodeInput = $("#ECode");
        let elementNameInput = $("#EName");
        let elementRadInput = $("#ERad");
        let color1_Input = $("#EC1");
        let color2_Input = $("#EC2");
        let color3_Input = $("#EC3");

        //Checking to see if element num is valid:
        if (!isPosInt(elementNumInput)) {
            showError(elementNumInput, "Element number must be an integer >= 1!");
            return;
        }

        //Checking to see if element name is a valid input:
        if (!isText(elementNameInput)) {
            showError(elementNameInput, "Element name cannot be left blank! Please try again.");
            return;
        }

        //Checking to see if element code is a valid 
        if (!isText(elementCodeInput)) {
            showError(elementCodeInput, "Element code cannot be left blank! Please try again.");
            return;
        }

        //Checking to see if radius value is > 0:
        if (!isPosIntandFloat(elementRadInput)) {
            showError(elementRadInput, "Radius must be a number and cannot be <= 0! Please enter in a valid entry.");
            return;
        }




        //If all the inputs (i.e input validation) were correct and nothing has returned, then continue with ajax req:
        //Append all values to elementFormData:
        elementFormData.append('ElementNum', elementNumInput.val());
        elementFormData.append('ElementCode', elementCodeInput.val());
        elementFormData.append('ElementName', elementNameInput.val());
        elementFormData.append('ElementRad', elementRadInput.val());
        elementFormData.append('Colour1', color1_Input.val());
        elementFormData.append('Colour2', color2_Input.val());
        elementFormData.append('Colour3', color3_Input.val());


        // console.log(elementFormData)




        $.ajax({
            url: "/upload-element-data",
            type: "POST",
            data: elementFormData,
            processData: false,
            contentType: false,
            success: function (response) {
                console.log("Upload Sucessful");
                console.log(response);

                // console.log(color1_Input.val().substring(1))
                // console.log(color2_Input.val().substring(1))
                // console.log(color3_Input.val().substring(1))
                // Create a new row with the submitted data
                var newRow = $('<tr>');
                newRow.append($('<td>').text(elementNumInput.val()));
                newRow.append($('<td>').text(elementCodeInput.val()));
                newRow.append($('<td>').text(elementNameInput.val()));
                newRow.append($('<td>').text(color1_Input.val().substring(1)));
                newRow.append($('<td>').text(color2_Input.val().substring(1)));
                newRow.append($('<td>').text(color3_Input.val().substring(1)));
                newRow.append($('<td>').text(elementRadInput.val()));
                newRow.append($('<td>').html('<button class="delete-row">X</button>'));
                $('#ElementTable tbody').on('click', '.delete-row', function () {
                    $(this).closest('tr').remove();
                });
                // Append the new row to the table
                $('#ElementTable tbody').append(newRow);

            },
            error: function (xhr, status, error) {
                console.log('Upload error!');
                console.log('Status:', status);
                console.log('Error:', error);
                console.log('XHR:', xhr);
                console.log('XHR Response:', xhr.responseText);
            }
        })


    });



    //ROTATING MOLECULE:
    $('#input-angle').submit(function (event) {

        console.log("TESTTTTTTTTTTTTTTTTTTTTTTT")
        //Prevents the form from submitting by default:
        event.preventDefault();

        //Input Values:
        var angleX = $("#angleX");
        var angleY = $("#angleY");
        var angleZ = $("#angleZ");


        //Error checking:
        if (!isPosIntandFloatUPDATED(angleX) || angleX.val() > 360.00) {
            alert("Invalid angle X val! Please enter an angle value between 0-360 degrees.");
            return;
        }
        if (!isPosIntandFloatUPDATED(angleY) || angleY.val() > 360.00) {
            alert("Invalid angle Y val! Please enter an angle value between 0-360 degrees.");
            return;
        }
        if (!isPosIntandFloatUPDATED(angleZ) || angleZ.val() > 360.00) {
            alert("Invalid angle Z val! Please enter an angle value between 0-360 degrees.");
            return;
        }

        var moleculeName = $("#MoleculeList").val();

        console.log(angleX.val())
        console.log(angleY.val())
        console.log(angleZ.val())
        console.log(moleculeName)

        //if data is good then get ready to send to server:

        //GET REQUEST FOR DYNAMIC TABLE:
        $.ajax({
            url: '/change-Angle',
            type: "POST",
            data: JSON.stringify({
                angleX: angleX.val(),
                angleY: angleY.val(),
                angleZ: angleZ.val(),
                molecule: moleculeName
            }),
            success: function (response) {
                console.log("Angle Changed Sucessfully");
                console.log(response);


                const svg = new XMLSerializer().serializeToString(response);
                //Display image in display-svg:
                $('#display-svg').html(svg);

            },
            error: function (xhr, status, error) {
                console.log('Error changing angle!');
                console.log(xhr.responseText);
            }
        })




    })


    //Functionality for uploading file & providing molecule name:
    $('#Upload').submit(function (event) {

        //Prevents the form from submitting by default:
        event.preventDefault();

        //Initializing Values:
        var formData = new FormData();
        var selectedFile = $('#SDFUpload')[0].files[0];
        var moleculeName = $("#MoleculeName")
        // formData.append('file', selectedFile);


        //Checking to see if file ends in .sdf:
        if (!selectedFile.name.endsWith('.sdf')) {
            showError(selectedFile, 'File must be in SDF format!');
            return;
        }
        //Checking to see if moleculeName has been entered:
        if (!isText(moleculeName)) {
            showError(moleculeName, "Molecule Name cannot be left blank! Please try again.");
            return;
        }


        // console.log(selectedFile); // logs the file name to the console
        // console.log(moleculeName.val())

        //Populating formData with file and molecule name:
        formData.append('file', selectedFile);
        formData.append('moleculeName', moleculeName.val());

        //Making sure form data includes both molecule and filename:
        console.log(formData)


        $.ajax({
            url: "/upload-molecule",
            type: "POST",
            data: formData,
            processData: false,
            contentType: false,
            success: function (response) {
                console.log("Upload Sucessful");
                console.log(response);

                if (response.status === 'success') { //"===" is same value AND type

                    var atomNum = response.atomCount;
                    var bondNum = response.bondCount;

                    //Append Molecule name, bond number, & atom number to drop down menu:
                    $('#MoleculeList').append($('<option>', {
                        value: moleculeName.val(),
                        text: moleculeName.val() + " (Number of Atoms: " + atomNum + ", Number of Bonds: " + bondNum + ")"
                    }));
                }
                else {
                    console.log("ERROR WHILE UPLOADING MOLECULE!!!");
                }
            },
            error: function (xhr, status, error) {
                console.log('Upload error!');
                console.log(xhr.responseText);
            }
        })



    });

    // make another ahndler for the select menu

    // receive the current selected molecule
    // if its on caffeine, receive caffeine using .val

    // make a post request pasing the molecule name
    // use load_mol witht he molecule name to receive the molecule from the db - mol = loadmol
    // get the svg for the molecule by doing mol = mol.svg()
    // send the svg back to server make sure content header is there with imag/svg+xml
    // use the .html method to convert the svg to html code


    $('#MoleculeList').change(function (event) {

        //Prevents the form from submitting by default:
        event.preventDefault();

        //Get molecule name (val):
        moleculeName = $("#MoleculeList").val();

        console.log(moleculeName)

        $.ajax({
            url: "/display-molecule",
            type: "POST",
            data: JSON.stringify({ molecule: moleculeName }),
            contentType: 'application/json',
            success: function (response) {
                console.log("Upload Sucessful");

                const svg = new XMLSerializer().serializeToString(response);
                //Display image in display-svg:
                $('#display-svg').html(svg);

            },
            error: function (xhr, status, error) {
                console.log('Upload error!');
                console.log(xhr.responseText);
            }
        })


    });


    // jQuery request to remove a row from the table and database
    $('#ElementTable tbody').on('click', '.delete-row', function () {

        console.log("BEFORE AJAX REQUEST");

        var row = $(this).closest('tr');
        var elementCode = row.find('td:eq(1)').text(); // Get the element number from the 2nd cell of the row

        // Send an AJAX request to delete the row from the database
        $.ajax({
            url: '/delete-element-data',
            type: 'POST',
            data: JSON.stringify({ 'ElementCode': elementCode }),
            contentType: 'application/json; charset=utf-8',
            success: function (response) {
                console.log('Element data deleted successfully!');
                row.remove(); // Remove the row from the table
            },
            error: function (xhr, status, error) {
                console.log('Error deleting element data:', error);
            }
        });

        console.log("AFTER AJAX REQUEST");
    });


    //GET REQUEST FOR DYNAMIC TABLE:
    $.ajax({
        url: "/grab-Elements",
        type: "GET",
        success: function (response) {
            console.log("Upload Sucessful");
            console.log(response);


            //Clear existing rows from table
            $('#ElementTable tbody tr').remove();

            //Append new rows for each element
            $.each(response, function (index, element) {
                var row = $('<tr>');
                row.append($('<td>').text(element['Element Number']));
                row.append($('<td>').text(element['Element Code']));
                row.append($('<td>').text(element['Element Name']));
                row.append($('<td>').text(element['Colour 1']));
                row.append($('<td>').text(element['Colour 2']));
                row.append($('<td>').text(element['Colour 3']));
                row.append($('<td>').text(element['Radius']));
                row.append($('<td>').html('<button class="delete-row">X</button>')); // Add 'delete-row' class to the button
                $('#ElementTable tbody').append(row);
            });

        },
        error: function (xhr, status, error) {
            console.log('Upload error! HEREEEE');
            console.log(xhr.responseText);
        }
    })


    //END OF DOC:
})





