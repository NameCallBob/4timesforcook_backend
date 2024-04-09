<<<<<<< HEAD

from torchtext.legacy.data import TabularDataset, Field, BucketIterator

# 讀取CSV文件
df = pd.read_csv('your_data_path/recipes.csv')

# 資料前處理
source_field = Field(tokenize='spacy', init_token='<sos>', eos_token='<eos>', lower=True)
target_field = Field(tokenize='spacy', init_token='<sos>', eos_token='<eos>', lower=True)

fields = {'name': ('src', source_field), 'steps': ('trg', target_field)}

# 使用TabularDataset載入資料
train_data = TabularDataset(
    path='your_data_path/recipes.csv',
    format='csv',
    fields=fields
)

# 建立字典
source_field.build_vocab(train_data, min_freq=2)
target_field.build_vocab(train_data, min_freq=2)

# 定義Seq2Seq模型
class Seq2SeqModel(nn.Module):
    def __init__(self, input_dim, output_dim, hidden_dim, n_layers, dropout):
        super(Seq2SeqModel, self).__init__()
        self.embedding = nn.Embedding(input_dim, hidden_dim)
        self.rnn = nn.LSTM(hidden_dim, hidden_dim, num_layers=n_layers, dropout=dropout)
        self.fc_out = nn.Linear(hidden_dim, output_dim)
        self.dropout = nn.Dropout(dropout)

    def forward(self, src, trg):
        embedded = self.dropout(self.embedding(src))
        output, hidden = self.rnn(embedded)
        prediction = self.fc_out(hidden[0].squeeze(0))
        return prediction

# 初始化模型、優化器和損失函數
INPUT_DIM = len(source_field.vocab)
OUTPUT_DIM = len(target_field.vocab)
HIDDEN_DIM = 256
N_LAYERS = 2
DROPOUT = 0.5

model = Seq2SeqModel(INPUT_DIM, OUTPUT_DIM, HIDDEN_DIM, N_LAYERS, DROPOUT)
optimizer = optim.Adam(model.parameters())
criterion = nn.CrossEntropyLoss()

# 定義設備
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# 將模型和損失函數移到設備上
model = model.to(device)
criterion = criterion.to(device)

# 建立BucketIterator
train_iterator, valid_iterator, test_iterator = BucketIterator.splits(
    (train_data, valid_data, test_data),
    batch_size=32,
    device=device
)

# 訓練模型（參考之前提供的訓練迴圈）
# ...
=======

from torchtext.legacy.data import TabularDataset, Field, BucketIterator

# 讀取CSV文件
df = pd.read_csv('your_data_path/recipes.csv')

# 資料前處理
source_field = Field(tokenize='spacy', init_token='<sos>', eos_token='<eos>', lower=True)
target_field = Field(tokenize='spacy', init_token='<sos>', eos_token='<eos>', lower=True)

fields = {'name': ('src', source_field), 'steps': ('trg', target_field)}

# 使用TabularDataset載入資料
train_data = TabularDataset(
    path='your_data_path/recipes.csv',
    format='csv',
    fields=fields
)

# 建立字典
source_field.build_vocab(train_data, min_freq=2)
target_field.build_vocab(train_data, min_freq=2)

# 定義Seq2Seq模型
class Seq2SeqModel(nn.Module):
    def __init__(self, input_dim, output_dim, hidden_dim, n_layers, dropout):
        super(Seq2SeqModel, self).__init__()
        self.embedding = nn.Embedding(input_dim, hidden_dim)
        self.rnn = nn.LSTM(hidden_dim, hidden_dim, num_layers=n_layers, dropout=dropout)
        self.fc_out = nn.Linear(hidden_dim, output_dim)
        self.dropout = nn.Dropout(dropout)

    def forward(self, src, trg):
        embedded = self.dropout(self.embedding(src))
        output, hidden = self.rnn(embedded)
        prediction = self.fc_out(hidden[0].squeeze(0))
        return prediction

# 初始化模型、優化器和損失函數
INPUT_DIM = len(source_field.vocab)
OUTPUT_DIM = len(target_field.vocab)
HIDDEN_DIM = 256
N_LAYERS = 2
DROPOUT = 0.5

model = Seq2SeqModel(INPUT_DIM, OUTPUT_DIM, HIDDEN_DIM, N_LAYERS, DROPOUT)
optimizer = optim.Adam(model.parameters())
criterion = nn.CrossEntropyLoss()

# 定義設備
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# 將模型和損失函數移到設備上
model = model.to(device)
criterion = criterion.to(device)

# 建立BucketIterator
train_iterator, valid_iterator, test_iterator = BucketIterator.splits(
    (train_data, valid_data, test_data),
    batch_size=32,
    device=device
)

# 訓練模型（參考之前提供的訓練迴圈）
# ...
>>>>>>> 4fb6132b440573c7d93c50e4eca66ea6abe7f5e3
