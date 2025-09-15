import sqlite3
import json

from model.parent_module.parent_module_class import ParentModule
from settings.settings import get_question_query, update_questions_query


class Questions(ParentModule):
    def __init__(self, database_file):
        super().__init__(database_file)
        print(f'connected to database: {database_file}')

    def open_json(self):
        with open("questions_extract.json", "r") as file:
            return json.load(file)
    print(f'opened questions_extract.json')

    def import_questions(self, data):
        con, cur = self.connect_to_db()

        for item in data:
            try:
                cur.execute("""INSERT INTO questions (questions_id, question, subject, education_level, school_year, prompts_id)
                VALUES (?, ?, ?, ?, ?, ?)""",(item['question_id'], item['question'], item['vak'], item['onderwijsniveau'], item['leerjaar'], 0))
            except sqlite3.IntegrityError:
                pass
        con.commit()
        print('questions imported')

    def get_questions(self, question_search=None,  niveau=None, school_year=None, subject=None):
        con, cur = self.connect_to_db()
        cur.row_factory = sqlite3.Row


        question_query = get_question_query

        request_question_filters = []
        if subject:
            request_question_filters.append(f"subject = ?")
        if niveau:
            request_question_filters.append(f"niveau = ?")
        if school_year:
            request_question_filters.append(f"school_year = ?")
        if question_search:
            request_question_filters.append(f"question LIKE ?")

        if request_question_filters:
            question_query += " WHERE " + "AND ".join(request_question_filters)

        question_filter_values = []
        if subject:
            question_filter_values.append(subject)
        if niveau:
            question_filter_values.append(niveau)
        if school_year:
            question_filter_values.append(school_year)
        if question_search:
            question_filter_values.append(f"%{question_search}%")



        cur.execute(question_query, question_filter_values)
        all_questions = cur.fetchall()
        print(all_questions)

        con.commit()
        self.disconnect_from_db(con, cur)

        if all_questions:
            questions_list = [
                {
                    "question": question["question"],
                    "education_level": question["education_level"],
                    "school_year": question["school_year"],
                    "subject": question["subject"],
                    "date_created": question["date_created"],
                    "taxonomy_bloom": question["taxonomy_bloom"],
                    "rtti": question["rtti"],
                }
                for question in all_questions
            ]
            return questions_list

        return []
        print('Nothing here')

    def show_questions(self, offset=0, limit=20, question_search=None,  education_level=None, school_year=None, subject=None):
        con, cur = self.connect_to_db()
        cur.row_factory = sqlite3.Row

        # If there's any filers or search query's made by the user the values should end up here via de app route in app.py
        # Below here the code check's which values/ filters have been used by the user
        # if there is any values or filters selected the code adds the right statements to the query to allow the query to filter for those values
        question_query = get_question_query

        request_question_filters = []
        if subject:
            request_question_filters.append(f"subject = ?")
        if education_level:
            request_question_filters.append(f"education_level = ?")
        if school_year:
            request_question_filters.append(f"school_year = ?")
        if question_search:
            request_question_filters.append(f"question LIKE ?")

        if request_question_filters:
            question_query += " WHERE " + "AND ".join(request_question_filters)

        question_query += " LIMIT ? OFFSET ?"

        question_filter_values = []
        if subject:
            question_filter_values.append(subject)
        if education_level:
            question_filter_values.append(education_level)
        if school_year:
            question_filter_values.append(school_year)
        if question_search:
            question_filter_values.append(f"%{question_search}%")

        question_filter_values.extend([limit, offset])




        cur.execute(question_query, question_filter_values)
        questions_list = cur.fetchall()
        con.commit()
        self.disconnect_from_db(con, cur)

        if questions_list:
            questions = [
                {
                    "questions_id": questions["questions_id"],
                    "question": questions["question"],
                    "education_level": questions["education_level"],
                    "school_year": questions["school_year"],
                    "subject": questions["subject"],
                    "date_created": questions["date_created"],
                    "taxonomy_bloom": questions["taxonomy_bloom"],
                    "rtti": questions["rtti"],
                }
                for questions in questions_list
            ]
            return questions

        return []

    def show_single_question(self, questions_id):
        con, cur = self.connect_to_db()
        cur.row_factory = sqlite3.Row
        result = cur.execute('''SELECT * FROM questions WHERE questions_id = ?''',
                             (questions_id,)).fetchone()
        if result:
            return dict(result)
        return None


    def new_update_taxonomy(self, taxonomy_bloom, questions_id):
        con, cur = self.connect_to_db()
        cur.execute('''UPDATE questions SET taxonomy_bloom = ? WHERE questions_id = ?''',
                       (taxonomy_bloom, questions_id))
        con.commit()
        return True

    def update_taxonomy(self, taxonomy_bloom, questions_id, prompt_type, user_id):
        con, cur = self.connect_to_db()

        # User_id invoeren
        cur.execute("""UPDATE questions SET user_id = ? WHERE questions_id = ?""", (user_id, questions_id))

        print(prompt_type)
        if prompt_type == 'Bloom':
            field_name = 'taxonomy_bloom'

        elif prompt_type == 'RTTI':
            field_name = 'rtti'

        else:
            field_name = prompt_type

        update_questions = update_questions_query.replace("{field_name}", field_name)
        print(update_questions)


        cur.execute(update_questions, (taxonomy_bloom, questions_id))
        con.commit()

        self.disconnect_from_db(con, cur)

        return True



        # return cursor.fetchall - als je meerdere resultaten verwacht uit de database
        # return cursor.fetchone - als je 1 resultaat verwacht uit de database
        # return cursor.lastrowid - als je het id terugwilt van de laatst toegevoegde student
        # GEEN return is ook oke als je alleen iets wilt opslaan in de database

    def show_user_questions(self, user_id):
        con, cur = self.connect_to_db()
        cur.row_factory = sqlite3.Row

        result = cur.execute("""SELECT * FROM questions WHERE user_id = ?""", (user_id,)).fetchall()
        return result
