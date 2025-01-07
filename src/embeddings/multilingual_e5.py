from transformers import AutoTokenizer, AutoModel
import torch.nn.functional as F
import torch

class EmbeddingGenerator:
    def __init__(self):
        # Khởi tạo tokenizer và model
        self.tokenizer = AutoTokenizer.from_pretrained("intfloat/multilingual-e5-large")
        self.model = AutoModel.from_pretrained("intfloat/multilingual-e5-large")

    def generate_embedding(self, text):
        inputs = self.tokenizer(text, max_length=512, padding=True, truncation=True, return_tensors="pt")
        outputs = self.model(**inputs)
        embedding = outputs.last_hidden_state.mean(dim=1)
        normalized_embedding = F.normalize(embedding, p=2, dim=1)
        return normalized_embedding.detach().numpy()[0]  # Đảm bảo kết quả là mảng 1 chiều
