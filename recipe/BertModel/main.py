
def modelPredict(sentence:str) -> list:
        """利用訓練好的Bert模型進行實體標記"""
        from recipe.BertModel.dataset import align_word_ids, ids_to_labels, tokenizer
        from recipe.BertModel.model import BertModel
        import torch
        import os

        model_path = os.path.join(os.getcwd(),"recipe","BertModel","trained","model.pth")
        model = BertModel()
        model.load_state_dict(torch.load(model_path))
        model.eval()

        use_cuda = torch.cuda.is_available()
        device = torch.device("cuda" if use_cuda else "cpu")

        if use_cuda:
            model = model.cuda()
        else:
            print("USE CPU PREDICT")

        text = tokenizer(sentence, padding='max_length',
                         max_length=128, truncation=True, return_tensors="pt")
        
        mask = text['attention_mask'].to(device)
        input_id = text['input_ids'].to(device)
        label_ids = torch.Tensor(align_word_ids(sentence)).unsqueeze(0).to(device)

        logits = model(input_id, mask, None)
        logits_clean = logits[0][label_ids != -100]

        predictions = logits_clean.argmax(dim=1).tolist()
        prediction_label = [ids_to_labels[i] for i in predictions]

        return prediction_label