import pandas as pd
from nltk import sent_tokenize
#W/O these it does not work for me. If it works for you, kindly delete the two lines when executing.
import nltk
nltk.download('punkt')

from scipy import stats
import pickle

from sklearn import preprocessing
from data.emotion_affect import EmotionAffectDataset
from data.fake_news import FakeNewsDataset

import csv

# [IMPORTANT!!!!!!] Note some models require the entire article while others require the concatenation of headline title plus a separating space plus the body text. Make sure your modification aligns with those dataset classes.

def eval_emotion(article_text, article_title):
    # Evaluate emotion
    #   Input: The article
    #   Output: 'angry-disgusted' etc.
    with open('output/model_dump/emo.model', 'rb') as f:
        loaded_pipeline = pickle.load(f)
    sentences = sent_tokenize(article_text)
    sentences.append(article_title)
    pred_emotions = loaded_pipeline.predict(sentences)
    print("Number of sentences: ", len(sentences))
    print("======")
    print(pred_emotions)
    final_emotion = stats.mode(pred_emotions).mode[0]
    return EmotionAffectDataset.emotion_class_dict[final_emotion]

def eval_category(article_title_n_text):
    # Evaluate news category
    #   Input: article title + " " (space) + article body text
    #   Output: category e.g. "POLITICS"
    
    #load the label encoder 
    with open('data/datasets/news_category_dataset/label_encoder.pickle', 'rb') as f:
        news_encoder = pickle.load(f)
    
    with open('output/model_dump/news.model', 'rb') as f:
        loaded_pipeline = pickle.load(f)
    
    pred_cate = loaded_pipeline.predict(article_title_n_text)
    le = news_encoder
    return le.inverse_transform(pred_cate)[0]
    
def eval_fake(article_title_n_text):
    # Evaluate fakeness
    #   Input: same as eval_news title+" "+text
    #   Output: "Fake" or "Authentic"
    with open('output/model_dump/fake.model', 'rb') as f:
        loaded_pipeline = pickle.load(f)
    
    pred_fake = loaded_pipeline.predict(article_title_n_text)
    return FakeNewsDataset.fake_class_dict[pred_fake[0]]

def eval_sent(article_text, article_title):
    # Evaluate sentiment
    #   Input: same as eval_emotion: the entire article
    #   Output: sentiment score 0-4
    with open('output/model_dump/stan.model', 'rb') as f:
        loaded_pipeline = pickle.load(f)
    
    sentences = sent_tokenize(article_text)
    sentences.append(article_title)
    pred_sent = loaded_pipeline.predict(sentences)
    final_sent = pred_sent.mean()
    return final_sent

def evaluate_all(article_title, article_text):
    # Load all 4 models
    # Run predictions on all 4 models
    # Return a dictonary 
    # { "emotion": pred_emotion, "category": pred_category, "fake": pred_fake, "sentiment": pred_sentiment }
    # All pred_ are text strings except sentiment (a score \in [0, 4])
    
    # Special handling regarding title and text
    title_n_text = article_title + " " + article_text
    pred_emotion = eval_emotion(article_text, article_title)
    #pred_category = eval_category([title_n_text]) #Don't delete []; required by sklearn
    pred_fake = eval_fake([title_n_text])
    #pred_sentiment = eval_sent(article_text, article_title)
    
    pred_category = []
    
    pred_sentiment = []
    return { "Emotion 1-7": pred_emotion, "Categories": pred_category, "Fakeness (0,1)": pred_fake, "Sentiments (0-4)": pred_sentiment }
    
    
if __name__=="__main__":
    data = pd.read_csv('covid19_articles/val_set/covid_19_articles.csv')
    csv_columns = ['Fakeness (0,1)','Sentiments (0-4)','Emotion 1-7','Categories']
    eval_dict_all = []
    for i in range(20):
        print(' Article ', i)
        # Load all at once
        eval_cur = evaluate_all(data['title'][i], data['text'][i])
        eval_dict_all.append(eval_cur)
        print(eval_cur)
        
        print("--------------------------------------------\n")
        
        # 1. Emotion
        print(' 1. Emotion ')
        print(eval_cur["Emotion 1-7"])
        
        # 2. News Category
        print(' 2. News Category')
        print(eval_cur["Categories"])
        
        # 3. Fake News
        print(' 3. Fake News')
        print(eval_cur["Fakeness (0,1)"])
        
        # 4. Sentiment
        print(' 4. Sentiment')
        print(eval_cur["Sentiments (0-4)"])
        print("============================================\n\n\n")
    
    # Output the dictionary to csv
    csv_file = "output/result/val_results.csv"
    with open(csv_file, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in eval_dict_all:
            writer.writerow(data)
    csvfile.close()
    
    