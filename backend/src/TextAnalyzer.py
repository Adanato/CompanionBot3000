from textblob import TextBlob
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from gensim import corpora, models
from sklearn.feature_extraction.text import TfidfVectorizer
from transformers import pipeline
import nltk

class TextAnalyzer:
    def __init__(self):
        self.sid = SentimentIntensityAnalyzer()
        self.emotion_classifier = pipeline("text-classification", 
                                        model="bhadresh-savani/distilbert-base-uncased-emotion",
                                        return_all_scores=True)

        nltk.download('punkt')
        nltk.download('averaged_perceptron_tagger')

    def extract_features(self, text):
        return {
            'sentiment': self.extract_sentiment(text),
            'word_count': self.extract_word_count(text),
            'emotion': self.extract_emotion(text)
        }

    def extract_long_term_features(self, conversation_history):
        return {
            'topics': self.extract_topic_modeling(conversation_history),
            'tf_idf': self.extract_TF_IDF(conversation_history)
        }

    def extract_sentiment(self, text):
        blob = TextBlob(text)
        return {
            'textblob': {'polarity': blob.sentiment.polarity, 
                        'subjectivity': blob.sentiment.subjectivity},
            'vader': self.sid.polarity_scores(text)
        }

    def extract_word_count(self, text):
        words = text.split()
        sentences = nltk.sent_tokenize(text)
        return {
            'total_words': len(words),
            'unique_words': len(set(words)),
            'sentence_count': len(sentences),
            'avg_words_per_sentence': len(words) / max(len(sentences), 1)
        }

    def extract_emotion(self, text):
        emotions = self.emotion_classifier(text)[0]
        return {emotion['label']: emotion['score'] for emotion in emotions}

    def extract_topic_modeling(self, texts):
        tokenized_texts = [text.lower().split() for text in texts]
        dictionary = corpora.Dictionary(tokenized_texts)
        corpus = [dictionary.doc2bow(text) for text in tokenized_texts]
        lda = models.LdaModel(corpus, num_topics=min(3, len(texts)), 
                             id2word=dictionary, passes=10)
        return lda.print_topics()

    def extract_TF_IDF(self, texts):
        tfidf = TfidfVectorizer(max_features=100)
        tfidf_matrix = tfidf.fit_transform(texts)
        return {
            'feature_names': tfidf.get_feature_names_out().tolist(),
            'feature_scores': tfidf_matrix.toarray().tolist()
        }