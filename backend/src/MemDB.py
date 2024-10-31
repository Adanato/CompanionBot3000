cd /tmp
git clone --branch v0.8.0 https://github.com/pgvector/pgvector.git
cd pgvector
make
make install # may need sudo



class MemDB():
    __self__init(self):

    self.database = connection
    function store_message(self, message, user):
        """
        Store message in the postgres pgvector for later
        
        """
        self.database.store()
        return
    function retrieve_message_context(self, message, user):
        """
        Use the message to get message context for incontext prompting using the most similar messages to help the model
        """
        
        self.database.retrieve()
        return
    