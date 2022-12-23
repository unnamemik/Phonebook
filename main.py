import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from PyQt5.QtWidgets import QDialog

import confirm_mod as c_mod
import about_mod as a_mod
import log_rw
import logs_mod as l_mod
import help_mod as h_mod
import new_mod as n_mod
import phonebook as pb
from log_rw import write_log, read_log


def confirm_to_save():
    c_mod_save_dlg = ConfModDlg()
    c_mod_save_dlg.exec()


def confirm_to_del():
    c_mod_del_dlg = ConfModDlg()
    c_mod_del_dlg.exec()


def show_help():
    h_mod_dlg = HelpModDlg()
    h_mod_dlg.exec()


def show_about():
    a_mod_dlg = AboutModDlg()
    a_mod_dlg.exec()


def show_logs():
    l_mod_dlg = LogsModDlg()
    l_mod_dlg.exec()


def add_new_contact():
    n_mod_dlg = NewModDlg()
    n_mod_dlg.exec()


class ConfModDlg(QDialog, c_mod.Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)


class AboutModDlg(QDialog, a_mod.Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)


class LogsModDlg(QDialog, l_mod.Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.textBrowser.setText(log_rw.read_log())


class HelpModDlg(QDialog, h_mod.Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)


class NewModDlg(QDialog, n_mod.Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)


class CustomTableView(QtWidgets.QTableView):
    def __init__(self, parent=None):
        super(CustomTableView, self).__init__(parent)
        self.setSortingEnabled(True)

    # def KeyPressEvent(self, event: QtGui.QKeyEvent):
    #     if event.key() == QtCore.Qt.Key_Enter:
    #         print("Key_Enter ")
    #     elif event.key() == QtCore.Qt.Key_Return:
    #         print("Key_Return ")


class NumberSortModel(QtCore.QSortFilterProxyModel):
    def lessThan(self, left_index: "QModelIndex",
                 right_index: "QModelIndex") -> bool:
        left_var: str = left_index.data(QtCore.Qt.EditRole)
        right_var: str = right_index.data(QtCore.Qt.EditRole)
        try:
            return float(left_var) < float(right_var)
        except (ValueError, TypeError):
            pass
        try:
            return left_var < right_var
        except TypeError:
            return True


class MainWindow(QtWidgets.QMainWindow, pb.Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        font = QtGui.QFont("Curier", 10)
        self.setFont(font)
        prim_table_view = self.tableView
        sec_table_view = self.tableView_2

        prim_grid_layout = QtWidgets.QGridLayout()
        prim_table_view.setLayout(prim_grid_layout)
        sec_grid_layout = QtWidgets.QGridLayout()
        sec_table_view.setLayout(sec_grid_layout)

        self.prim_model = QtGui.QStandardItemModel(self)
        self.prim_model.setHorizontalHeaderLabels(["Фамилия Имя Отчество"])
        self.sec_model = QtGui.QStandardItemModel(self)
        self.sec_model.setHorizontalHeaderLabels(["Телефон", "Компания", "Комментарий"])

        self.prim_proxy = NumberSortModel()
        self.prim_proxy.setSourceModel(self.prim_model)
        self.sec_proxy = NumberSortModel()
        self.sec_proxy.setSourceModel(self.sec_model)

        self.prim_table = CustomTableView(self)
        self.prim_table.setModel(self.prim_proxy)
        self.sec_table = CustomTableView(self)
        self.sec_table.setModel(self.sec_proxy)

        prim_horisontal_layout = QtWidgets.QHBoxLayout()
        prim_grid_layout.addLayout(prim_horisontal_layout, 0, 0)
        prim_grid_layout.addWidget(self.prim_table, 1, 0)

        sec_horisontal_layout = QtWidgets.QHBoxLayout()
        sec_grid_layout.addLayout(sec_horisontal_layout, 0, 0)
        sec_grid_layout.addWidget(self.sec_table, 1, 0)

        self.lineEdit.textEdited.connect(self.on_search)
        self.actionAbout.triggered.connect(show_about)
        self.actionHelp.triggered.connect(show_help)
        self.actionLogs.triggered.connect(show_logs)
        self.pushButton_3.clicked.connect(self.show_selected)

        con = QSqlDatabase.addDatabase("QSQLITE")
        con.setDatabaseName('pb_db.db')
        con.open()
        query = QSqlQuery()
        query.exec('SELECT * FROM prim_tab')
        query_lst = []
        self.prim_table.setColumnWidth(0, 800)
        if query.isActive():
            query.first()
            while query.isValid():
                query_lst.append(str(query.value('prim_id')) + " " + str(query.value('contact_name')))
                self.prim_model.appendRow([QtGui.QStandardItem(str(query.value('contact_name')))])
                query.next()
        for el in query_lst: print(el)
        con.close()

        prim_update_button = QtWidgets.QPushButton("Добавить")
        prim_update_button.clicked.connect(self.prim_on_update)
        sec_update_button = QtWidgets.QPushButton("Добавить")
        sec_update_button.clicked.connect(self.sec_on_update)

        self.qlineedit_name = QtWidgets.QLineEdit()
        self.qlineedit_name.resize(24, 80)
        self.qlineedit_name.setText("Новый контакт")
        self.qlineedit_name.selectAll()
        self.qlineedit_phone = QtWidgets.QLineEdit()
        self.qlineedit_phone.resize(24, 80)
        self.qlineedit_phone.setText("Телефон")
        self.qlineedit_phone.selectAll()
        self.qlineedit_company = QtWidgets.QLineEdit()
        self.qlineedit_company.resize(24, 80)
        self.qlineedit_company.setText("Компания")
        self.qlineedit_company.selectAll()
        self.qlineedit_comment = QtWidgets.QLineEdit()
        self.qlineedit_comment.resize(24, 80)
        self.qlineedit_comment.setText("Комментарий")
        self.qlineedit_comment.selectAll()

        prim_horisontal_layout.addWidget(self.qlineedit_name, stretch=1)
        prim_horisontal_layout.addWidget(prim_update_button)
        prim_horisontal_layout.setAlignment(QtCore.Qt.AlignRight)

        sec_horisontal_layout.addWidget(self.qlineedit_phone, stretch=1)
        sec_horisontal_layout.addWidget(self.qlineedit_company, stretch=1)
        sec_horisontal_layout.addWidget(self.qlineedit_comment, stretch=1)
        sec_horisontal_layout.addStretch(1)
        sec_horisontal_layout.addWidget(sec_update_button)
        sec_horisontal_layout.setAlignment(QtCore.Qt.AlignRight)

    def show_selected(self):
        self.sec_table.setColumnWidth(0, 200)
        self.sec_table.setColumnWidth(1, 250)
        self.sec_table.setColumnWidth(2, 250)
        self.sec_model.setRowCount(0)
        row = (self.prim_table.currentIndex().row()) + 1
        con = QSqlDatabase.addDatabase("QSQLITE")
        con.setDatabaseName('pb_db.db')
        con.open()
        query = QSqlQuery()
        query_str1 = f"SELECT COUNT(cont_id) from sec_tab where cont_id= {row}"
        query.exec(query_str1)
        query.first()
        counter = int(query.value(0))
        query_str2 = f"SELECT * FROM sec_tab JOIN prim_tab ON sec_tab.cont_id = {row}"
        query.exec(query_str2)
        write_log(query_str1)
        write_log(query_str2)
        query_lst = []

        if query.isActive():
            query.first()
            while counter > 0:
                query_lst.append(str(query.value('sec_id')) + ' ' + str(query.value('cont_id')) + ' ' +
                                 str(query.value('number')) + ' ' + str(query.value('company')) + ' ' +
                                 str(query.value('comment')))
                self.sec_model.appendRow([QtGui.QStandardItem(str(query.value('number'))),
                                          QtGui.QStandardItem(str(query.value('company'))),
                                          QtGui.QStandardItem(str(query.value('comment')))])
                query.next()
                counter -= 1
        for el in query_lst: print(el)
        con.close()

    def on_search(self):
        search_str = self.lineEdit.text()
        r = 0
        # print(self.model.item(r, 0).text())
        rows = self.prim_table.model().rowCount()
        while rows > 0:
            font = QtGui.QFont("Curier", 10)
            self.prim_model.item(r, 0).setFont(font)
            if search_str in self.prim_model.item(r, 0).text() and search_str != '':
                print(self.prim_model.item(r, 0).text())
                font = QtGui.QFont("Curier", 12, QtGui.QFont.Bold)
                self.prim_model.item(r, 0).setFont(font)
            rows -= 1
            r += 1

    def prim_on_update(self):
        name = self.qlineedit_name.text().strip() if self.qlineedit_name.text().strip() else '0'
        if not name:
            msg = QtWidgets.QMessageBox.information(self, 'ВНИМАНИЕ', 'Заполните поле ввода ФИО!')
            return
        rows = self.prim_table.model().rowCount()
        add_record = True
        for row in range(rows):
            if name == self.prim_proxy.data(self.prim_proxy.index(row, 0)):
                add_record = False
                row_edit = row
                break
        if add_record:  # add
            if self.prim_table.selectedIndexes():
                row = self.prim_table.selectedIndexes()[-1].row()
                self.prim_model.insertRow(row + 1, [QtGui.QStandardItem(name)])
            else:
                self.prim_model.appendRow([QtGui.QStandardItem(name)])
        else:
            self.prim_model.setData(self.prim_model.index(row_edit, 1), name, QtCore.Qt.EditRole)
        arg_lst = [name]
        self.prim_do_update_query(arg_lst)

    def sec_on_update(self):
        phone = self.qlineedit_phone.text().strip()
        company = self.qlineedit_company.text().strip() if self.qlineedit_company.text().strip() else '0'
        comment = self.qlineedit_comment.text().strip()
        if not phone.isdigit():
            msg = QtWidgets.QMessageBox.information(self, 'ВНИМАНИЕ', 'Заполните правильно поле ввода Телефон!')
            return
        if not company:
            msg = QtWidgets.QMessageBox.information(self, 'ВНИМАНИЕ', 'Заполните поле ввода Компания!')
            return
        if not comment:
            msg = QtWidgets.QMessageBox.information(self, 'ВНИМАНИЕ', 'Заполните поле ввода Комментарий!')
            return
        rows = self.sec_table.model().rowCount()
        add_record = True
        for row in range(rows):
            if company == self.sec_proxy.data(self.sec_proxy.index(row, 0)):
                add_record = False
                row_edit = row
                break

        if add_record:  # add
            if self.sec_table.selectedIndexes():
                row = self.sec_table.selectedIndexes()[-1].row()
                self.sec_model.insertRow(row + 1, [QtGui.QStandardItem(company),
                                                   QtGui.QStandardItem(phone),
                                                   QtGui.QStandardItem(comment)])
            else:
                self.sec_model.appendRow([QtGui.QStandardItem(phone),
                                          QtGui.QStandardItem(company),
                                          QtGui.QStandardItem(comment)])
        else:  # update
            self.sec_model.setData(self.sec_model.index(row_edit, 1), phone, QtCore.Qt.EditRole)
            self.sec_model.setData(self.sec_model.index(row_edit, 2), comment, QtCore.Qt.EditRole)

    def prim_do_update_query(self, args):
        con = QSqlDatabase.addDatabase("QSQLITE")
        con.setDatabaseName('pb_db.db')
        con.open()
        query = QSqlQuery()
        res = f"UPDATE prim_tab SET contact_name = {args[0]} WHERE prim_tab.prim_id=0"
        query.exec(res)
        con.close()

    def sec_do_update_query(self, args):
        con = QSqlDatabase.addDatabase("QSQLITE")
        con.setDatabaseName('pb_db.db')
        con.open()
        query = QSqlQuery()
        res = f"UPDATE sec_tab " \
              f"SET number={args[0]}, company={args[1]}, comment={args[2]} " \
              f"WHERE cont_id={args[0]}"
        con.close()

if __name__ == "__main__":
    application = QtWidgets.QApplication([])
    window = MainWindow()
    window.setWindowTitle("Phonebook")
    window.setMinimumSize(500, 500)
    window.show()
    sys.exit(application.exec_())
