import sqlite3

from model.parent_module.parent_module_class import ParentModule
from settings.settings import multiple_prompts_query


class PromptModules(ParentModule):
    def __init__(self, database_file):
        super().__init__(database_file)


    # The function below here is used to insert the prompt the user has made in to the database,
    # before the prompt is actually saved a check is made to see if the prompt the user is trying to add doesnt already exist
    # if this is the case the prompt wil not be added and a print statement is made, the print statement should be replaced with a error message
    # or should be replaced with a flash message that possibily contains the prompt name of the prompt with the same question for indexing
    # the code currently only goes of if the prompts are a 100% match ignoring upper and lower case.
    def save_new_prompt(self, user_id, prompt_name, prompt, prompt_type, questions_count=0, questions_correct=0, succes_rating=0):
        con, cur = self.connect_to_db()

        try:
            cur.execute("SELECT COUNT(*) FROM prompts WHERE LOWER(prompt) = LOWER(?)", (prompt,))
            if cur.fetchone()[0] > 0:
                print(f"prompt '{prompt}' already exists inside of the database.")
                return None

            # This piece of code is meant to make sure the prompt
            # cant be added if the user isn't logged in and somehow made it to the page to add prompt
            if user_id == None:
                return None

            # This is where the prompt is actually inserted in to the database
            cur.execute("INSERT INTO prompts (user_id, prompt_name, prompt, questions_count, questions_correct, succes_rating, prompt_type) VALUES(?, ?, ?, ?, ?, ?, ?)",
                        (user_id, prompt_name, prompt, questions_count, questions_correct, succes_rating, prompt_type))
            con.commit()
            return cur.lastrowid

        finally:
            self.disconnect_from_db(con, cur)


    # This function updates the values according to the input by the user and the api,
    # if succes is True it wil add 1 to both questions_count and questions_correct
    # if this is not the case it will add 1 to the questions_count
    # in the function below this one the succes rating is calculated which is then used here to update said succes rating
    def update_prompt_success_count(self, prompts_id, success=False):
        con, cur = self.connect_to_db()

        cur.execute("SELECT questions_count, questions_correct FROM prompts WHERE prompts_id = ?", (prompts_id,))

        if success:
            cur.execute("UPDATE prompts SET questions_count = questions_count + 1, questions_correct = questions_correct + 1 WHERE prompts_id = ?", ( prompts_id ))
        else:
            cur.execute("UPDATE prompts SET questions_count = questions_count + 1 WHERE prompts_id = ?", (prompts_id ))
        con.commit()

        # requests the newly updated values used to calculate the succes rating
        cur.execute("SELECT questions_count, questions_correct FROM prompts WHERE prompts_id = ?", ( prompts_id ))
        questions_values = cur.fetchone()

        questions_count, questions_correct = questions_values
        succes_rating = self.calculate_succes_rating(questions_count, questions_correct)

        cur.execute("UPDATE prompts SET succes_rating = ? WHERE prompts_id = ?", (succes_rating, prompts_id))
        con.commit()

        self.disconnect_from_db(con, cur)


    # This functions calculates the prompts succes rating based on the questions_count and the questions_correct
    # if there's no value or if the value is zero the code should return zero to avoid a error caused by deviding zero by zero
    def calculate_succes_rating(self, questions_count, questions_correct):
        if questions_count == 0:
            succes_rating = 0
        else:
            succes_rating = (questions_correct/questions_count) * 100
        return succes_rating




    # This function it meant to remove prompts if that is needed
    # currently this doesnt do anything but its here if in the future it is decided that the option to remove prompts should be added
    # note that the current version doesnt have anything in place to solve the database integerety issues caused by removing a prompt
    # the prompt may be referenced to in the questions table if the questions where the prompt was used are in the database.
    def remove_prompt(self, prompt_id):
        con, cur = self.connect_to_db()

        cur.execute("DELETE FROM prompts WHERE prompts_id = ?", (prompt_id,))

        con.commit()

        self.disconnect_from_db(con, cur)


    # This function requests every prompt in the database,
    # there is also functionality for a filter in the function to allow for filtering on alpabetical order,
    # the succes percentage of a prompt and the amount of questions that have been indexed with a prompt.
    def show_multiple_prompts(self, filter_by_alphabetical_order=False, filter_by_succes_rating=None, filter_by_questions_count=None, filter_by_prompt_type=None ):
        con, cur = self.connect_to_db()
        cur.row_factory = sqlite3.Row

        prompts_query = multiple_prompts_query

        request_prompt_filters = []
        if filter_by_alphabetical_order:
            request_prompt_filters.append("p.prompt_name ASC")
        if filter_by_succes_rating:
            request_prompt_filters.append("p.succes_rating DESC")
        if filter_by_questions_count:
            request_prompt_filters.append("p.questions_count DESC")
        if filter_by_prompt_type:
            request_prompt_filters.append("p.prompt_type ASC")

        # The piece of code below here is where the filters are applied in to the query
        # if there is more then one filter selected the other ones will be overwritten by the one higher in the list
        if request_prompt_filters:
            prompts_query += "ORDER BY " + ", ".join(request_prompt_filters)

        cur.execute(prompts_query)
        prompts = cur.fetchall()
        print(prompts)

        con.commit()
        self.disconnect_from_db(con, cur)


        if prompts:
            prompts_list = [
                {
                    "display_name": prompt["display_name"],
                    "user_id": prompt["user_id"],
                    "prompt_name":prompt["prompt_name"],
                    "prompts_id": prompt["prompts_id"],
                    "prompt": prompt["prompt"],
                    "questions_count": prompt["questions_count"],
                    "questions_correct": prompt["questions_correct"],
                    "succes_rating": prompt["succes_rating"],
                    "prompt_type": prompt["prompt_type"],
                    "date_created": prompt["date_created"],
                }
                for prompt in prompts
            ]
            return prompts_list

        return []


    # This function is used to show the prompts related to the type of indexing you want to do
    def show_prompt_type(self, prompt_type):
        con, cur = self.connect_to_db()
        cur.row_factory = sqlite3.Row

        cur.execute("SELECT * FROM prompts WHERE prompt_type = ?", (prompt_type,))
        prompts = cur.fetchall()
        print(prompts)

        con.commit()
        self.disconnect_from_db(con, cur)

        if prompts:
            prompts_list = [
                {
                    "prompt_name":prompt["prompt_name"],
                    "prompts_id": prompt["prompts_id"],
                    "prompt": prompt["prompt"],
                    "questions_count": prompt["questions_count"],
                    "succes_rating": prompt["succes_rating"],
                    "prompt_type": prompt["prompt_type"],
                }
                for prompt in prompts
            ]
            return prompts_list

        return []



    # This function is used to select information of a single prompt after giving the id of the prompt you want to view or request.
    def show_prompt(self, prompt_id):
        con, cur = self.connect_to_db()

        cur.row_factory = sqlite3.Row

        cur.execute("""SELECT p.prompts_id, p.user_id, p.prompt_name, 
            p.prompt, p.questions_count, p.questions_correct, 
            p.succes_rating, p.date_created, u.display_name, p.prompt_type
            FROM prompts p
            JOIN users u ON p.user_id = u.user_id
            WHERE prompts_id = ?""", (prompt_id,))

        fetch_prompt=cur.fetchone()

        con.commit()
        self.disconnect_from_db(con, cur)

        if fetch_prompt:
            return {
                "display_name": fetch_prompt["display_name"],
                "user_id": fetch_prompt["user_id"],
                "prompt_name": fetch_prompt["prompt_name"],
                "prompts_id": fetch_prompt["prompts_id"],
                "prompt": fetch_prompt["prompt"],
                "questions_count": fetch_prompt["questions_count"],
                "questions_correct": fetch_prompt["questions_correct"],
                "succes_rating": fetch_prompt["succes_rating"],
                "prompt_type": fetch_prompt["prompt_type"],
                "date_created": fetch_prompt["date_created"],
            }

        return None
