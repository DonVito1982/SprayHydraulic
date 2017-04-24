from xlrd import open_workbook

book = open_workbook('../test_resources/test_network.xlsx')
print book.nsheets

for index in range(book.nsheets):
    print book.sheet_by_index(index)
    # print book.sheet_by_index(index).__class__

print book.sheet_names()

for sheet_name in book.sheet_names():
    print sheet_name

nozzle_sheet = book.sheet_by_name('Nozzle')

col_width = []
for col_index in range(nozzle_sheet.ncols):
    col_width.append(len(nozzle_sheet.cell_value(0, col_index)))

for row_index in range(nozzle_sheet.nrows):
    print ''
    for col_index in range(nozzle_sheet.ncols):
        arrange = "%-" + "%d" % (col_width[col_index] + 1) + "s"
        print arrange % str(nozzle_sheet.cell_value(row_index, col_index)),
