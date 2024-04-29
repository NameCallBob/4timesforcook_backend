from transformers import BertForTokenClassification
import torch



class BertModel(torch.nn.Module):

    def __init__(self):
        tokenize_type = {

        'O': 0,
        "num": 1,
        "B-ING":2,"B-DIS":3,"B-NUT":4,
        "B-ALG":5,"B-STP":6,"B-TME":7,
        "B-UDO":8,"B-TAG":9,"I-ING":10,"I-TAG":11

        }
        super(BertModel, self).__init__()

        self.bert = BertForTokenClassification.from_pretrained('bert-base-cased', num_labels=len(tokenize_type.keys()))

    def forward(self, input_id, mask, label):

        output = self.bert(input_ids=input_id, attention_mask=mask, labels=label, return_dict=False)

        return output