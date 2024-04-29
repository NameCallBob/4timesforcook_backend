from torch.utils.data import Dataset,DataLoader
import torch
from transformers import BertTokenizerFast

label_all_tokens = False


labels_to_ids = {
        'O': 0,
        "num": 1,
        "B-ING":2,"B-DIS":3,"B-NUT":4,
        "B-ALG":5,"B-STP":6,"B-TME":7,
        "B-UDO":8,"B-TAG":9,"I-ING":10,"I-TAG":11
}

ids_to_labels = {v: k for k, v in labels_to_ids.items()}
tokenizer = BertTokenizerFast.from_pretrained("bert-base-cased")

def align_label(texts, labels):
    tokenized_inputs = tokenizer(texts, padding='max_length', max_length=128, truncation=True,return_tensors="pt")
    # print(texts) ; print(tokenized_inputs)
    word_ids = tokenized_inputs.word_ids()
    previous_word_idx = None
    label_ids = []
    # print(word_ids)
    for word_idx in word_ids:
        if word_idx is None:
            label_ids.append(-100)

        elif word_idx != previous_word_idx:
            try:
                label_ids.append(labels_to_ids[labels[word_idx]])

            except Exception as e:
                label_ids.append(-100)
        else:
            try:
                label_ids.append(labels_to_ids[labels[word_idx]] if label_all_tokens else -100)
            except:
                label_ids.append(-100)
        previous_word_idx = word_idx

    # print(label_ids)
    # import time
    # time.sleep(2)
    return label_ids

class BertNERDataset(Dataset):

    def __init__(self, df):

        lb = df[1]
        txt = df[0]
        # print(zip(txt,lb))
        # print(lb),print(txt)
        self.texts = [tokenizer(str(i),
                               padding='max_length', max_length = 128, truncation=True, return_tensors="pt") for i in txt]
        self.labels = [align_label(i,j) for i,j in zip(txt, lb)]
        # print(self.labels)

    def __len__(self):

        return len(self.labels)

    def get_batch_data(self, idx):

        return self.texts[idx]

    def get_batch_labels(self, idx):

        return torch.LongTensor(self.labels[idx])

    def __getitem__(self, idx):

        batch_data = self.get_batch_data(idx)
        batch_labels = self.get_batch_labels(idx)

        return batch_data, batch_labels



def align_label_example(tokenized_input, labels):

        word_ids = tokenized_input.word_ids()

        previous_word_idx = None
        label_ids = []

        for word_idx in word_ids:

            if word_idx is None:
                label_ids.append(-100)

            elif word_idx != previous_word_idx:
                try:
                  label_ids.append(labels_to_ids[labels[word_idx]])
                except:
                  label_ids.append(-100)

            else:
                label_ids.append(labels_to_ids[labels[word_idx]] if label_all_tokens else -100)
            previous_word_idx = word_idx


        return label_ids

def align_word_ids(texts):

    tokenized_inputs = tokenizer(texts, padding='max_length', max_length=128, truncation=True)

    word_ids = tokenized_inputs.word_ids()

    previous_word_idx = None
    label_ids = []

    for word_idx in word_ids:

        if word_idx is None:
            label_ids.append(-100)

        elif word_idx != previous_word_idx:
            try:
                label_ids.append(0)
            except:
                label_ids.append(-100)
        else:
            try:
                label_ids.append(1 if label_all_tokens else -100)
            except:
                label_ids.append(-100)
        previous_word_idx = word_idx

    return label_ids


def evaluate_one_text(model, sentence):

    use_cuda = torch.cuda.is_available()
    device = torch.device("cuda" if use_cuda else "cpu")

    if use_cuda:
        model = model.cuda()

    text = tokenizer(sentence, padding='max_length', max_length = 128, truncation=True, return_tensors="pt")

    mask = text['attention_mask'].to(device)
    input_id = text['input_ids'].to(device)
    label_ids = torch.Tensor(align_word_ids(sentence)).unsqueeze(0).to(device)

    logits = model(input_id, mask, None)
    logits_clean = logits[0][label_ids != -100]

    predictions = logits_clean.argmax(dim=1).tolist()
    prediction_label = [ids_to_labels[i] for i in predictions]

    return sentence,prediction_label

# evaluate_one_text(model, 'Bill Gates is the founder of Microsoft')

# import pandas as pd
# tokenizer = BertTokenizerFast.from_pretrained("bert-base-cased")

# data = pd.read_excel("./Train_data/trans_result.xlsx")
# data = data.drop(columns=['Unnamed: 0'])
# text = data['text'].tolist()
# entity = [eval(i) for i in data['entity'].tolist()]
# for example in text :
#     text_tokenized = tokenizer(example, padding='max_length', max_length=512, truncation=True, return_tensors="pt")
#     print(text_tokenized)
