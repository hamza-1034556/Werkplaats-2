from application.model.parent_module.parent_module_class import ParentModule

# This is a template for a module to use as a reference or to coppy paste if you are making a new kind of module
class ModuleName(ParentModule):
    def __init__(self, database_file):
        super().__init__(database_file)

    # You can have multiple functions in one class so there's no need to make a new class for every function that does something else
    def some_function(self, a_bunch_of_variables ):
        con, cur = self.connect_to_db()
        cur.execute(" a sql query (a_bunch_of_variables) VALUES (?, ?, ?, ?)", #the number of question marks needs to be the same as the number of variables
                    (a_bunch_of_variables))
        con.commit()




        self.disconnect_from_db(con, cur)
        return a_bunch_of_variables

        # return cursor.fetchall - als je meerdere resultaten verwacht uit de database
        # return cursor.fetchone - als je 1 resultaat verwacht uit de database
        # return cursor.lastrowid - als je het id terugwilt van de laatst toegevoegde student
        # GEEN return is ook oke als je alleen iets wilt opslaan in de database