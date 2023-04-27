import sys
import cgi
import io
import MolDisplay
import molecule
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib  # code to parse for data
import molsql
import json

# Creating & assigning DB:
dataB = molsql.Database(reset=True)
dataB.create_tables()

# Default elements:
dataB['Elements'] = (1, 'H', 'Hydrogen', 'FFFFFF', '050505', '020202', 25)
dataB['Elements'] = (6, 'C', 'Carbon', '808080', '010101', '000000', 40)
dataB['Elements'] = (7, 'N', 'Nitrogen', '0000FF', '000005', '000002', 40)
dataB['Elements'] = (8, 'O', 'Oxygen', 'FF0000', '050000', '020000', 40)


class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Reading in index.html file:
        if self.path == "/":
            with open("index.html", "r") as file:
                home_page = file.read()
            self.send_response(200)  # OK
            self.send_header("Content-type", "text/html")
            self.send_header("Content-length", len(home_page))
            self.end_headers()
            self.wfile.write(bytes(home_page, "utf-8"))
        # Reading in style.css:

        elif self.path == "/style.css":
            with open("style.css", "r") as file:
                css = file.read()
            self.send_response(200)  # OK
            self.send_header("Content-type", "text/css")
            self.send_header("Content-length", len(css))
            self.end_headers()
            self.wfile.write(bytes(css, "utf-8"))

        # Reading in java script file:
        elif self.path == "/script.js":
            with open("script.js", "r") as file:
                js = file.read()
            self.send_response(200)  # OK
            self.send_header("Content-type", "text/javascript")
            self.send_header("Content-length", len(js))
            self.end_headers()
            self.wfile.write(bytes(js, "utf-8"))

        # GET REQ to send element data (for table display):
        elif self.path == "/grab-Elements":
            # Create tuple holding all element data:

            query = dataB.con.execute("SELECT * FROM Elements;").fetchall()
            # print("hi")
            # print(query)
            elementData = []

            for element in query:
                elementData.append({"Element Number": element[0], "Element Code": element[1], "Element Name": element[2], "Colour 1": element[3],
                                    "Colour 2": element[4], "Colour 3": element[5], "Radius": element[6]})
            # send the elementData to client as a JSON response:
            print(elementData)

            self.send_response(200)  # OK
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(elementData).encode())

        # If it was not one of those 3 files, an error occured (404):
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(bytes("404: not found", "utf-8"))

    def do_POST(self):
        if self.path == "/upload-element-data":

            # this is specific to 'multipart/form-data' encoding used by POST
            content_length = int(self.headers['Content-Length'])
            content_type = self.headers['Content-Type']
            # body = self.rfile.read(content_length)

            postvars = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST',
                         'CONTENT_TYPE': content_type}
            )

            # print(repr(body.decode('utf-8')))

            # Extract the element contents:
            elementNum = int(postvars.getvalue('ElementNum'))
            elementCode = postvars.getvalue('ElementCode')
            elementName = postvars.getvalue('ElementName')
            elementRad = int(postvars.getvalue('ElementRad'))
            color1 = postvars.getvalue('Colour1')
            color2 = postvars.getvalue('Colour2')
            color3 = postvars.getvalue('Colour3')

            # Removing "#" from color values:
            color1 = color1.replace('#', '')
            color2 = color2.replace('#', '')
            color3 = color3.replace('#', '')

            dataB['Elements'] = (elementNum, elementCode,
                                 elementName, color1, color2, color3, elementRad)

            # make sure they were extracted correctly:
            print(elementNum)
            print(elementName)
            print(elementCode)
            print(elementRad)
            print(color1)
            print(color2)
            print(color3)

            # send the svg to the client
            self.send_response(200)  # OK
            self.end_headers()
            self.wfile.write(
                bytes("Uploaded element data successfully!", "utf-8"))

        elif self.path == "/upload-molecule":

            cgi.parse_header(self.headers['Content-Type'])

            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )

            # Recieve file object:
            fItem = form['file']
            MolName = form.getvalue('moleculeName')

            # Recieve file contents:
            contents = fItem.file.read()

            # convert to bytes:
            converted = io.BytesIO(contents)
            data = io.TextIOWrapper(converted)

            # add molecule to database:
            dataB.add_molecule(MolName, data)

            # get ID of last inserted molecule:
            mol_id = dataB.con.execute(
                "SELECT MOLECULE_ID FROM Molecules WHERE NAME = ?", (MolName,)).fetchone()[0]

            atomNum = dataB.con.execute(
                """SELECT COUNT(*) FROM MoleculeAtom WHERE MOLECULE_ID = ?""", (mol_id,)).fetchone()[0]
            bondNum = dataB.con.execute(
                """SELECT COUNT(*) FROM MoleculeBond WHERE MOLECULE_ID = ?""", (mol_id,)).fetchone()[0]

            self.send_response(200)  # OK
            self.send_header('Content-Type', 'application/json')
            self.end_headers()

            # Send response with atom and bond count:
            response = {
                "status": "success",
                "atomCount": atomNum,
                "bondCount": bondNum
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))

        elif self.path == "/display-molecule":
            try:
                MolDisplay.radius = dataB.radius()
                MolDisplay.element_name = dataB.element_name()
                MolDisplay.header += dataB.radial_gradients()
                # this is specific to 'multipart/form-data' encoding used by POST
                content_length = int(self.headers['Content-Length'])
                body = self.rfile.read(content_length)
                data = json.loads(body.decode('utf-8'))
                molecule_name = data.get('molecule')  # recieve mol name

                # Load molecule & generate svg:
                mol = dataB.load_mol(molecule_name)
                mol.sort()
                svg = mol.svg()

                print(svg)

                # Send svg back to client:
                self.send_response(200)  # OK
                self.send_header('Content-type', 'image/svg+xml')
                self.send_header('Content-Length', len(svg))
                self.end_headers()
                self.wfile.write(bytes(svg, "utf-8"))

                # Resetting colours:
                MolDisplay.element_name = ""
                MolDisplay.radius = ""
                MolDisplay.radial_gradients = """<svg version="1.1" width="1000" height="1000" xmlns="http://www.w3.org/2000/svg">"""

            # Error checking:
            except Exception as e:
                print(f"Error while handling display-molecule request: {e}")
                self.send_response(500)  # Internal Server Error
                self.end_headers()

        elif self.path == "/delete-element-data":
            # Parse the data sent by the client
            content_length = int(self.headers['Content-Length'])
            data = self.rfile.read(content_length)
            decoded_data = data.decode('utf-8')
            elementCode = json.loads(data)['ElementCode']

            # Delete row from database:
            query = "DELETE FROM Elements WHERE ELEMENT_CODE = ?"
            dataB.con.execute(query, (elementCode,))
            dataB.con.commit()

            # Send success back to client:
            self.send_response(200)  # OK
            self.end_headers()
            self.wfile.write(bytes("Element successfully deleted", "utf-8"))

        elif self.path == "/change-Angle":
                
            MolDisplay.radius = dataB.radius()
            MolDisplay.element_name = dataB.element_name()
            MolDisplay.header += dataB.radial_gradients()
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))


            # Assigning variables recieved from client:
            molName = data.get('molecule')
            angleX = int(data.get('angleX'))
            angleY = int(data.get('angleY'))
            angleZ = int(data.get('angleZ'))

            print(molName)
            print(angleX)
            print(angleY)
            print(angleZ)

            # Load & sort molecule:
            mole = dataB.load_mol(molName)
            mole.sort()

            # Rotate based on X, Y, & Z Degree values:
            mx = molecule.mx_wrapper(angleX,angleY,angleZ)
            mole.xform( mx.xform_matrix )

            svg = mole.svg()

            # Send svg back to client:
            self.send_response(200)  # OK
            self.send_header('Content-type', 'image/svg+xml')
            self.send_header('Content-Length', len(svg))
            self.end_headers()
            self.wfile.write(bytes(svg, "utf-8"))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(bytes("404: not found", "utf-8"))


# Setting up local host:
httpd = HTTPServer(('localhost', int(sys.argv[1])), MyHandler)
httpd.serve_forever()
