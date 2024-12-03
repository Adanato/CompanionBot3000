
from textblob import TextBlob
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from gensim import corpora
from gensim.models import LdaModel
from sklearn.feature_extraction.text import TfidfVectorizer
from transformers import pipeline



class TextAnalyzer:

    def __init__(self):
        self.sentiment = 

    def extract_features(self, text):
        sentiment = self.extract_sentiment(text)
        word_count = self.extract_word_count( text)
        intent = self.extract_intent(text)
        emotion = self.extract_emotion(text)
        mental_state = (sentiment, word_count, intent, emotion)
        return mental_state
    
    def extract_long_term_features(self,conversation_history):
        """ 
        Entire conversation history or past sessions should be inputted.
        """

        topics = self.topic_modeling(text)
        tf_idf = self.extract_TF_IDF(text)

        return (topics)

    def extract_sentiment(self, text):
        

        blob = TextBlob(text)
        sentiment = blob.sentiment
        sid = SentimentIntensityAnalyzer()
        sentiment2 = sid.polarity_scores(text)
        return (sentiment, sentiment2)

    def extract_topic_modeling(self, text):
        
        texts = [["sample", "text", "feature", "extraction"]]
        dictionary = corpora.Dictionary(texts)
        corpus = [dictionary.doc2bow(text) for text in texts]
        lda = LdaModel(corpus, num_topics=2, id2word=dictionary)
        topics = lda.print_topics()
        return topics

    def extract_TF_IDF(self, text):
        
        # Initialize TF-IDF vectorizer and fit-transform
        tfidf = TfidfVectorizer()
        tfidf_matrix = tfidf.fit_transform([text])

        # Print the TF-IDF matrix
        print(tfidf_matrix.toarray())
        print(tfidf.get_feature_names_out())
        return tfidf_matrix
        
    def extract_emotion(self,text):
        # Load an emotion classification model
        emotion_classifier = pipeline("text-classification", model="bhadresh-savani/distilbert-base-uncased-emotion")


        emotions = emotion_classifier(text)
        return