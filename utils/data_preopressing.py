from datasets import load_dataset
data_set = load_dataset("xlangai/spider") 
train_data=data_set["train"]
validation_data=data_set["validation"]


#print(train_data["question"][0])
#print(train_data["query"][0])
# print(train_data["query_toks_no_value"][0])
#print(train_data["query_toks"][0])
