from model.parent_module.parent_module_class import ParentModule

class Feedback(ParentModule):
    def __init__(self, database_file):
        super().__init__(database_file)

    def save_feedback(self, feedback_title, feedback_text):
        con, cur = self.connect_to_db()
        data = cur.execute('''INSERT INTO feedback (feedback_title, feedback_text) VALUES (?, ?)''',
                       (feedback_title, feedback_text ))
        con.commit()
        return data
