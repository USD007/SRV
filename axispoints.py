import os.path
import xlsxwriter


class CalprmExcelWriter:

    # 1) add_worksheet(worksheetname) to create worksheets
    # 2) add_tablecontents(worksheetname, line) - writes table contents
    # 3) def close_workbook() - writes to excel and closes

    def __init__(self, output_path):
        filename = 'calprm_results.xlsx'
        self.workbook_name = os.path.join(output_path, filename)
        self.workbook = xlsxwriter.Workbook(self.workbook_name)

        # Format cells
        self.general_format = self.workbook.add_format({'bold': True})
        self.table_contents_format = self.workbook.add_format({'text_wrap': True, 'border': True, 'valign': 'vcenter'})

        self.store_worksheet = {}

    def add_worksheet(self, worksheetname):
        try:
            worksheet = self.workbook.add_worksheet(worksheetname)

            # Tool information
            worksheet.write('A1', 'CalPrm Label', self.general_format)
            worksheet.write('B1', 'Type', self.general_format)
            worksheet.write('C1', 'Axis X Max', self.general_format)
            worksheet.write('D1', 'Axis Y Max', self.general_format)
            worksheet.write('E1', 'Axis X', self.general_format)
            worksheet.write('F1', 'Axis Y', self.general_format)
            worksheet.write('G1', 'Longname', self.general_format)
            worksheet.write('H1', 'Address', self.general_format)
            worksheet.write('I1', 'RecordLayout', self.general_format)

            # Add width to columns
            worksheet.set_column(0, 0, 35)
            worksheet.set_column(1, 1, 7)
            worksheet.set_column(2, 2, 10)
            worksheet.set_column(3, 3, 10)
            worksheet.set_column(4, 4, 6)
            worksheet.set_column(5, 5, 5)
            worksheet.set_column(6, 6, 60)
            worksheet.set_column(7, 7, 12)
            worksheet.set_column(8, 8, 20)

            self.store_worksheet[worksheetname] = {'worksheet': worksheet}
            self.store_worksheet[worksheetname].update({'index': 2})

        except:  # When worksheet name already exists
            return

    def add_tablecontents(self, worksheetname, calprm_entry):
        if worksheetname in self.store_worksheet:
            worksheet = self.store_worksheet[worksheetname]['worksheet']
            worksheet_index = self.store_worksheet[worksheetname]['index']

            worksheet_col = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']

            for n, col_name in enumerate(worksheet_col):
                worksheet.write(col_name + str(worksheet_index), calprm_entry[n], self.table_contents_format)

            # Update serial number
            self.store_worksheet[worksheetname].update({'index': worksheet_index + 1})

        else:
            # print(worksheetname + "worksheet not created"
            pass

    def close_workbook(self):
        from general import ensure_excel_closed
        xl_filename = 'calprm_results.xlsx'
        try:
            ensure_excel_closed(xl_filename)
            self.workbook.close()
            if not self.store_worksheet:
                os.remove(self.workbook_name)
            del self.workbook
        except:
            try:
                ensure_excel_closed(xl_filename)
                self.workbook.close()
                if not self.store_worksheet:
                    os.remove(self.workbook_name)
                del self.workbook
            except:
                # print("srvchecker_error.xlsx cannot be created.")
                pass
