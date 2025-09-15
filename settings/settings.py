#if the location of the database file or the database file itself changes rename the path in between the apostrof
database = 'databases/database.db'



multiple_prompts_query = """SELECT p.prompts_id, p.user_id, p.prompt_name,
            p.prompt, p.questions_count, p.questions_correct, 
            p.succes_rating, p.prompt_type, p.date_created, u.display_name
            FROM prompts p
            JOIN users u ON p.user_id = u.user_id
            """


get_question_query = """SELECT questions_id, question, education_level, school_year, subject, date_created, taxonomy_bloom, rtti FROM questions"""

update_questions_query = """UPDATE questions SET {field_name} = ? WHERE questions_id = ?"""