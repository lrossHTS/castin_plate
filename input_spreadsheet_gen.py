import openpyxl
import random
import os

def generate_input_spreadsheet(file_path, num_rows):
    workbook = openpyxl.Workbook()
    sheet = workbook.active

    # Write header
    header = ["Reference", "Arg1", "Arg2", "Arg3", "Arg4", "Arg5", "Arg6", "Arg7", "Arg8", "Arg9", "Arg10"]
    sheet.append(header)

    # Generate random data for arguments and include a reference in the first column
    for i in range(1, num_rows + 1):
        row_data = [f"Row{i}"] + [random.randint(1, 100) for _ in range(10)]
        sheet.append(row_data)

    # Add a macro (VBA code) to the workbook
    add_macro(sheet)

    # Save the workbook
    workbook.save(file_path)

def add_macro(sheet):
    # Get the script directory
    script_directory = os.path.dirname(os.path.realpath(__file__))

    # Add a macro (VBA code) to the workbook
    vba_code = f'''
Sub RunPythonScript()
    Dim objShell As Object
    Set objShell = VBA.CreateObject("WScript.Shell")
    objShell.Run "python ""{os.path.join(script_directory, 'input_spreadsheet_reader.py')}""", 1, True
    Set objShell = Nothing
End Sub
'''
    sheet.vba_code = vba_code

if __name__ == "__main__":
    script_directory = os.path.dirname(os.path.realpath(__file__))
    input_spreadsheet_path = os.path.join(script_directory, 'input_spreadsheet_with_macro.xlsx')
    num_rows = 10  # Adjust the number of rows as needed

    generate_input_spreadsheet(input_spreadsheet_path, num_rows)
    print(f"Input spreadsheet with macro generated at: {input_spreadsheet_path}")

