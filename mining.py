import pandas as pd
from nltk.sentiment import SentimentIntensityAnalyzer
from gensim import corpora
from gensim.models import LdaModel
from gensim.models.coherencemodel import CoherenceModel

# Configurar análise de sentimentos
def analyzeSentiment(top_posts):
    sia = SentimentIntensityAnalyzer()
    sentiments = []

    for text in top_posts['texto_original']:
        if text:
            sentiment = sia.polarity_scores(text)
            sentiments.append(sentiment)
        else:
            sentiments.append({"neg": 0, "neu": 0, "pos": 0, "compound": 0})

    sentiment_df = pd.DataFrame(sentiments)
    top_posts = pd.concat([top_posts.reset_index(drop=True), sentiment_df], axis=1)
    return top_posts

# Configurar modelagem de tópicos
def topicModeling(top_posts, num_topics=5, passes=10):
    if isinstance(top_posts['tokens'].iloc[0], str):
        top_posts['tokens'] = top_posts['tokens'].apply(eval)

    texts = top_posts['tokens'].tolist()
    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]

    lda_model = LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=passes, random_state=42)
    topics = lda_model.print_topics(num_words=5)
    return topics
