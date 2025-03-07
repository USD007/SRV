import os.path
import xlsxwriter


class ExcelWriter:

    # 1) add_worksheet(worksheetname) to create worksheets
    # 2) add_tablecontents(worksheetname, line) - writes table contents
    # 3) def close_workbook() - writes to excel and closes

    def __init__(self, output_path, options, default_options):
        from version import VERSION
        from appinfo import APPNAME
        from datetime import datetime
        from general import ALM_MSG

        now = datetime.now()
        self.date_time = now.strftime("%d-%m-%Y     %H:%M:%S")
        self.toolname = APPNAME
        self.version = VERSION

        filename = 'srvchecker_log.xlsx'
        self.workbook_name = os.path.join(output_path, filename)
        self.workbook = xlsxwriter.Workbook(self.workbook_name)

        # Format cells
        self.general_format = self.workbook.add_format({'bold': True})
        self.table_general_format = self.workbook.add_format({'bold': True, 'border': True})
        self.table_header_format = self.workbook.add_format({'bold': True, 'bg_color': '#B8BFC1', 'text_wrap': True,
                                                             'border': True, 'align': 'center', 'valign': 'vcenter'})
        self.table_contents_format = self.workbook.add_format({'text_wrap': True, 'border': True, 'valign': 'vcenter'})
        self.help_format = self.workbook.add_format({'text_wrap': True, 'color': 'blue',
                                                     'underline': True, 'border': True, 'valign': 'top'})
        self.warning_format = self.workbook.add_format({'color': 'red', 'border': True, 'valign': 'vcenter'})
        self.label_format = self.workbook.add_format({'align': 'left'})
        self.execution_success_format = self.workbook.add_format({'bold': True, 'color': 'green'})
        self.execution_failure_format = self.workbook.add_format({'bold': True, 'color': 'red'})
        self.wrong_label_format = self.workbook.add_format({'bold': True, 'color': 'red', 'border': True})
        self.table_failure_format = self.workbook.add_format({'bold': True, 'color': 'red'})
        self.general_num_format = self.workbook.add_format({'bold': True, 'align': 'left'})

        self.store_worksheet = {}
        self.options = options
        self.default_options = default_options
        self.tableheader_rownum = 0  # Change if Tool Information changes and rows number are affected.
        self.alm_msg = ALM_MSG
        self.label_index = 0
        self.summary_worksheet = self.add_summarysheet()
        self.summary_worksheet_num = 10
        self.is_mic = False
        self.wrong_hexfiles_path = None
        self.srvchecker_exec_status = ''
        self.err_msg = None
        self.source_num = 0
        self.impacted_hex_num = 0
        self.hex_files_count = False
        self.reduced_hex_file_count = 0

    def add_summarysheet(self):
        worksheet = self.workbook.add_worksheet("summary")
        # Tool information
        worksheet.write('A2', 'Tool Name and Version', self.general_format)
        worksheet.write('A3', 'Tool invocation Information', self.general_format)
        worksheet.write('A4', 'Time of generation', self.general_format)
        worksheet.write('A5', 'Default values of parameter considered', self.general_format)
        worksheet.write('A7', 'Execution Status', self.general_format)

        # Update worksheet generation time
        worksheet.write('D2', self.toolname + ' - ' + self.version)
        worksheet.write('D3', self.options)
        worksheet.write('D4', self.date_time)
        worksheet.write('D5', self.default_options)

        # Add width to columns
        worksheet.set_column(0, 0, 5)
        worksheet.set_column(1, 1, 15)
        worksheet.set_column(2, 2, 30)

        return worksheet

    def add_worksheet(self, worksheetname, hexname=None):
        try:
            worksheet = self.workbook.add_worksheet(worksheetname)

            # Tool information
            worksheet.write('A2', 'Tool Name and Version', self.general_format)
            worksheet.write('A3', 'Tool invocation Information', self.general_format)
            worksheet.write('A4', 'Time of generation', self.general_format)
            worksheet.write('A5', 'Default values of parameter considered', self.general_format)
            index = 6
            if hexname is not None:
                self.reduced_hex_file_count += 1
                worksheet.write('A' + str(index), 'Hex filename:', self.general_format)
                worksheet.write('D' + str(index), hexname)
                listname = hexname.replace('.hex', '_srvchecker_impact.lst')
                index += 1
            else:
                hexname = 'NA'
                listname = worksheetname + ".lst"
            label_index = index
            # write result to D6 or D7
            worksheet.write('A' + str(index), 'Total number of impacted labels', self.general_format)
            if self.is_mic:
                worksheet.write('A' + str(index+2), self.alm_msg, self.warning_format)
                self.tableheader_rownum = index + 4
            else:
                self.tableheader_rownum = index + 2

            # Update worksheet generation time
            worksheet.write('D2', self.toolname + ' - ' + self.version)
            worksheet.write('D3', self.options)
            worksheet.write('D4', self.date_time)
            worksheet.write('D5', self.default_options)

            # Add width to columns
            worksheet.set_column(0, 0, 5)
            worksheet.set_column(1, 1, 15)
            worksheet.set_column(2, 2, 40)
            worksheet.set_column(3, 3, 60)
            worksheet.set_column(4, 4, 50)

            self.store_worksheet[worksheetname] = {'worksheet': worksheet}
            self.store_worksheet[worksheetname].update({'serial_num': 1})
            self.store_worksheet[worksheetname].update({'index': label_index})
            self.store_worksheet[worksheetname].update({'hexname': hexname})
            self.store_worksheet[worksheetname].update({'listname': listname})

        except:  # When worksheet name already exists
            return

    def add_tablecontents(self, worksheetname, line):
        if worksheetname in self.store_worksheet:
            worksheet = self.store_worksheet[worksheetname]['worksheet']
            serial_num = self.store_worksheet[worksheetname]['serial_num']
            worksheet_row_num = serial_num + self.tableheader_rownum

            if serial_num == 1:
                # Table header
                if worksheetname == 'srvchecker_scan':
                    impact_header = 'Maps/ Curves with invalid direct call'
                else:
                    impact_header = 'Impacted Map(s)/Curve(s)'
                worksheet.write('A' + str(self.tableheader_rownum), 'Sl. No.', self.table_header_format)
                worksheet.write('B' + str(self.tableheader_rownum), 'Error code', self.table_header_format)
                worksheet.write('C' + str(self.tableheader_rownum), impact_header, self.table_header_format)
                worksheet.write('D' + str(self.tableheader_rownum), 'Description', self.table_header_format)
                worksheet.write('E' + str(self.tableheader_rownum), 'Help', self.table_header_format)

            # Write line to the table
            worksheet.write_number('A' + str(worksheet_row_num), serial_num, self.table_contents_format)
            worksheet.write('B' + str(worksheet_row_num), line[0], self.table_contents_format)
            worksheet.write('C' + str(worksheet_row_num), line[1], self.table_contents_format)
            worksheet.write('D' + str(worksheet_row_num), line[2], self.table_contents_format)
            worksheet.write_url('E' + str(worksheet_row_num), line[3], self.help_format)

            # Update serial number
            self.store_worksheet[worksheetname].update({'serial_num': serial_num + 1})

        else:
            # print(worksheetname + "worksheet not created"
            pass

    # Updates the number of labels in each worksheet
    def labels_num_update(self):
        for worksheetname in self.store_worksheet:
            worksheet = self.store_worksheet[worksheetname]['worksheet']
            serial_num = self.store_worksheet[worksheetname]['serial_num'] - 1
            index = self.store_worksheet[worksheetname]['index']
            hexfilename = self.store_worksheet[worksheetname]['hexname']
            listname = self.store_worksheet[worksheetname]['listname']
            worksheet.write_number('D' + str(index), serial_num, self.label_format)
            self.update_summary_entry(worksheetname, serial_num, hexfilename, listname)

    def update_summary_entry(self, worksheetname, no_of_labels, hexfilename, listname):
        if self.summary_worksheet_num == 10:
            self.summary_worksheet.write('A9', 'Sl. No.', self.table_header_format)
            self.summary_worksheet.write('B9', 'Worksheet Name', self.table_header_format)
            if self.reduced_hex_file_count:
                self.summary_worksheet.write('C9', 'Hex Filename', self.table_header_format)
                self.summary_worksheet.write('D9', 'Output List', self.table_header_format)
                self.summary_worksheet.write('E9', 'Number of labels', self.table_header_format)
                self.summary_worksheet.set_column(3, 3, 30)
                self.summary_worksheet.set_column(4, 4, 20)
            else:
                self.summary_worksheet.write('C9', 'Output List', self.table_header_format)
                self.summary_worksheet.write('D9', 'Number of labels', self.table_header_format)
                self.summary_worksheet.set_column(3, 3, 20)

        index = str(self.summary_worksheet_num)
        sl_no = self.summary_worksheet_num - 9

        if no_of_labels > 0:
            table_content_frmt = self.table_general_format
            label_frmt = self.wrong_label_format
            if hexfilename != 'NA':
                self.impacted_hex_num += 1
        else:
            label_frmt = table_content_frmt = self.table_contents_format

        self.summary_worksheet.write('A' + index, sl_no, table_content_frmt)
        self.summary_worksheet.write('B' + index, worksheetname, table_content_frmt)
        if self.reduced_hex_file_count:
            self.summary_worksheet.write('C' + index, hexfilename, table_content_frmt)
            self.summary_worksheet.write('D' + index, listname, table_content_frmt)
            self.summary_worksheet.write_number('E' + index, no_of_labels, label_frmt)
        else:
            self.summary_worksheet.write('C' + index, listname, table_content_frmt)
            self.summary_worksheet.write_number('D' + index, no_of_labels, label_frmt)
        self.summary_worksheet_num += 1

    def update_summary(self):
        frmt = self.execution_success_format if self.srvchecker_exec_status == 'SUCCESS' else self.execution_failure_format
        self.summary_worksheet.write('D7', self.srvchecker_exec_status, frmt)

        # Updating A6, D6
        if self.err_msg is not None:
            self.summary_worksheet.write('A6', 'Failure Message', self.general_format)
            self.summary_worksheet.write('D6', self.err_msg, self.execution_failure_format)
        else:
            if self.reduced_hex_file_count:
                self.summary_worksheet.write('A6', 'No. of hex files considered with reduced axis points', self.general_format)
                self.summary_worksheet.write_number('D6', self.reduced_hex_file_count, self.general_num_format)
                self.summary_worksheet.write('A' + str(self.summary_worksheet_num + 1),
                                             str(self.impacted_hex_num) + ' hex file(s) impacted.',
                                             self.execution_failure_format if self.impacted_hex_num else self.execution_success_format)
                self.summary_worksheet_num += 2
            # TODO - Config creation from options - Add comment accordingly, now only reduced axis info written.
            elif self.hex_files_count and not self.reduced_hex_file_count:
                self.summary_worksheet.write('A6', 'No. of hex files considered with reduced axis points', self.general_format)
                self.summary_worksheet.write_number('D6', 0, self.general_num_format)
                self.summary_worksheet.write('A' + str(self.summary_worksheet_num + 1),
                                             'No reduced axispoints found in hex file(s) and it is not impacted.',
                                             self.execution_success_format)
            else:
                self.summary_worksheet.write('A6', 'Numbers of source files scanned', self.general_format)
                self.summary_worksheet.write_number('D6', self.source_num)

        if self.wrong_hexfiles_path is not None:
            self.write_wrong_hexfiles_path()

        if self.is_mic:
            self.summary_worksheet.write('A' + str(self.summary_worksheet_num + 1), self.alm_msg, self.general_format)

    def write_wrong_hexfiles_path(self):
        self.summary_worksheet_num += 1
        self.summary_worksheet.write('A' + str(self.summary_worksheet_num), "List of wrong hex files path: "
                                     + str(len(self.wrong_hexfiles_path)), self.general_format)
        for filename in self.wrong_hexfiles_path:
            self.summary_worksheet_num += 1
            self.summary_worksheet.write('A' + str(self.summary_worksheet_num), filename)

    def set_is_mic(self, is_mic):
        self.is_mic = is_mic

    def set_exec_status(self, status):
        self.err_msg, self.srvchecker_exec_status = status

    def set_input_hexfile(self, input_hex_count):
        self.hex_files_count = input_hex_count

    def set_wrong_hexfilespath(self, wrong_hexfiles):
        self.wrong_hexfiles_path = wrong_hexfiles

    def set_sourcefile_num(self, num):
        self.source_num = num

    def close_workbook(self):
        from general import ensure_excel_closed
        xl_filename = 'srvchecker_error.xlsx'
        try:
            self.labels_num_update()
            self.update_summary()
            ensure_excel_closed(xl_filename)
            self.workbook.close()
            del self.workbook
        except:
            try:
                ensure_excel_closed(xl_filename)
                self.workbook.close()
                del self.workbook
            except:
                # print("srvchecker_log.xlsx cannot be created.")
                pass
