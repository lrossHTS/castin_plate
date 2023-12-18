import openpyxl
import os
import xlwings as xw
# from your_module import your_python_function  # Replace 'your_module' and 'your_python_function' with your actual module and function names

def your_python_function(arg1,arg2,arg3,arg4,arg5,arg6,arg7,arg8,arg9,arg10):

    result = arg1 + arg2 + arg3 + arg4 + arg5 + arg6 + arg7 + arg8 + arg9 + arg10

    return result

def read_arguments_from_spreadsheet(file_path):
    wb = xw.Book(file_path)
    sheet = wb.sheets[0]  # Assuming data is on the first sheet

    arguments = []
    for row in sheet.range('B2:K' + str(sheet.cells.last_cell.row)).value:
        arguments.append(row)  # Include the entire row as arguments

    wb.close()
    return arguments

def write_result_to_spreadsheet(file_path, results):
    wb = xw.Book(file_path)
    sheet = wb.sheets[0]  # Assuming data is on the first sheet

    for i, result in enumerate(results, start=2):
        sheet.cells(i, 12).value = result  # Assuming the result should be written in the 12th column

    wb.save()
    wb.close()

def main():
    script_directory = os.path.dirname(os.path.realpath(__file__))
    spreadsheet_path = os.path.join(script_directory, 'input_spreadsheet_with_macro.xlsx')

    arguments = read_arguments_from_spreadsheet(spreadsheet_path)

    results = []    
    for args in arguments:
        # Call your Python function with the unpacked arguments
        result = your_python_function(*args)  # Replace 'your_python_function' with your actual function name
        results.append(result)

    write_result_to_spreadsheet(spreadsheet_path, results)

if __name__ == "__main__":
    main()
