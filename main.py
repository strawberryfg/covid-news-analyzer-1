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

# Create the dataset class object
dataset = dataset_map[args.dataset]()
dataset.split_data(train_size=args.split_ratio,test_size=args.test_ratio)

config = Config(dataset=args.dataset,
                model=args.models,
                feats=args.feats,
                save_path=args.save_path,
                continue_train=args.continue_train,
                load_path=args.load_path,
                test=args.test_only)

trainer = Trainer(dataset=dataset, models=args.models, transforms=args.feats, cfg=config)
# Train
trainer.train()
# Test
metrics = trainer.evaluate()
# Save best
trainer.save_best(metrics)
print("Test result (simul) : ")
print(metrics)
print("Simultaneously training done")
print("==================================\n\n\n\n\n\n\n\n\n\n")

# Sample Usage:
# python3 main.py --dataset emo_aff --models lr linearsvm gnb --feats bow ngram tfidf --split_ratio 0.8 --test_ratio 0.1 --save_path best
