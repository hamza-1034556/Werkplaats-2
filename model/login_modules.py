from application.model.parent_module.parent_module_class import ParentModule


class Login(ParentModule):
    def __init__(self, database_file):
        super().__init__(database_file)


    def some_function(self, a_bunch_of_variables ):
        con, cur = self.connect_to_db()
        cur.execute(" a sql query (a_bunch_of_variables) VALUES (?, ?, ?, ?)", #the number of question marks needs to be the same as the number of variables
                    (a_bunch_of_variables))
        con.commit()




        self.disconnect_from_db(con, cur)
        return a_bunch_of_variables