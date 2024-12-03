




class MemDB():
"""
A postgres database with vector support
"""
    def __init__(self):

        self.database = connection

    def store_message(self, message, user):
        """
        Store message in the postgres pgvector and sentiment analytics for later
        """
        extract sentiment
        extract intent
        extract subject
        
        self.database.store(message)
        return


    def retrieve_message_context(self, message, user):
        """
        Use the message to get message context for incontext prompting using the most similar messages to help the model
        """
        
        self.database.retrieve(message)
        return
    