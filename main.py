import os
import pandas as pd
from training.argparser import argparser
from training.config import Config
from training.trainer import Trainer
import json
# from data.preprocessing import preprocessor_fn

from data.stanford_sentiment import StanfordSentimentDataset
from data.news_category import NewsCategoryDataset
from data.fake_news import FakeNewsDataset
from data.emotion_affect import EmotionAffectDataset

dataset_map = {
  'stan_sent': StanfordSentimentDataset,
  'news_cat': NewsCategoryDataset,
  'fake_news': FakeNewsDataset,
  'emo_aff': EmotionAffectDataset
}

# Parse arguments
args = argparser()
# print("Command line arguments:")
# print(args)

config = Config(dataset=args.dataset,
                model=args.models,
                feats=args.feats,
                save_path=args.save_path,
                continue_train=args.continue_train,
                load_path=args.load_path,
                test=args.test_only)

# Load clean data
if args.load_clean:
    print("Loading cleaned data")
    # Create the dataset class object
    dataset = dataset_map[args.dataset](do_clean=False)
    data_path = os.path.join(config.model_dir, args.dataset+'_clean.csv')
    if os.path.exists(data_path):
        clean_data = pd.read_csv(data_path).dropna()
        dataset.data = clean_data
    print("Done")
else:
    print("Loading and cleaning data")
    dataset = dataset_map[args.dataset](do_clean=True)

# Split the data
dataset.split_data(
  dataset_ratio=args.split_ratio,
  test_size=args.test_ratio)

if args.save_data:
    print("Saving cleaned data")
    dataset.data.to_csv(os.path.join(config.model_dir, args.dataset+'_clean.csv'), index=False)
    print("Done")

trainer = Trainer(dataset=dataset, models=args.models, transforms=args.feats, cfg=config, grid=False)
# If we only want to test
if args.test_only:
    trainer.load_model(args.models[0], args.feats[0], args.load_path)

# Train
if not(args.test_only):
    trainer.train()
# Get the evaluation metric
# If test only GridSearchCV is not fitted yet -> so set grid to False
if args.test_only:
    metrics = trainer.evaluate()
else:
    metrics = trainer.evaluate()

# Save results
if args.save_results:
    print("Saving results")
    metrics.to_csv(os.path.join(config.model_dir, args.dataset+'_results.csv'), index=False)
    print("Done")

# Save best
if not(args.test_only):
    trainer.save_best(metrics)
    print("Simultaneously training done")
else:
    print("Test result : ")
    print(metrics)
    trainer.logger.info(metrics)


# Sample Usage:
# [Emotion]
# 1. Train
#       python3 main.py --dataset emo_aff --models lr linearsvm gnb --feats bow ngram tfidf --split_ratio 0.8 --test_ratio 0.1 --save_path emo.model
# 2. Test
#       python3 main.py --dataset emo_aff --models linearsvm  --feats ngram  --split_ratio 0.7 --test_ratio 0.3 --load_path emo.model -test_only

# python3 main.py --dataset emo_aff --models lr --feats bow --split_ratio 0.8 --test_ratio 0.1 --save_path emo.model

# [News Category]
# 1. Train
#       python3 main.py --dataset news_cat --models lr linearsvm gnb --feats bow ngram tfidf --split_ratio 0.02 --test_ratio 0.05 --save_path news.model
# 2. Test
#       python3 main.py --dataset news_cat --models lr --feats ngram --split_ratio 0.1 --test_ratio 0.2 --load_path news.model -test_only

# python3 main.py --dataset news_cat --models lr --feats bow --split_ratio 0.02 --test_ratio 0.05 --save_path news.model

# [Fake News]
# 1. Train
#       python3 main.py --dataset fake_news --models lr --feats bow --split_ratio 0.001 --test_ratio 0.001 --save_path fake.model
# 2. Test
#.      python3 main.py --dataset fake_news --models lr --feats bow --split_ratio 0.002 --test_ratio 0.005 --load_path fake.model -test_only

# [Stanford Sentiment]
# 1. Train
#       python3 main.py --dataset stan_sent --models lr --feats bow --split_ratio 0.01 --test_ratio 0.01 --save_path stan.model
# 2. Test
#       python3 main.py --dataset stan_sent --models lr --feats bow --split_ratio 0.1 --test_ratio 0.02 --load_path stan.model -test_only




# Final commands:
# [Emotion]
# nohup python -u main.py --dataset emo_aff --models mnb svm lr xgb rf ada --feats bow ngram tfidf --split_ratio 1.0 --test_ratio 0.2 --save_path emo.model --load_clean --save_results > out_emo.txt &

# [News Category]
# nohup python -u main.py --dataset news_cat --models mnb svm lr xgb rf ada --feats bow ngram tfidf --split_ratio 1.0 --test_ratio 0.2 --save_path news.model --load_clean --save_results > out_news.txt &

# [Fake News]
# nohup python -u main.py --dataset fake_news --models mnb svm lr xgb rf ada --feats bow ngram tfidf --split_ratio 1.0 --test_ratio 0.2 --save_path fake.model --load_clean --save_results > out_fake.txt &

# [Stanford Sentiment]
# nohup python -u main.py --dataset stan_sent --models mnb svm lr xgb rf ada --feats bow ngram tfidf --split_ratio 1.0 --test_ratio 0.2 --save_path stan.model --load_clean --save_results > out_stan.txt &
