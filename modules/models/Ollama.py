import json
import logging
import textwrap
import uuid

from ollama import Client

from modules.presets import i18n,INITIAL_SYSTEM_PROMPT

from ..index_func import construct_index
from ..utils import count_token
from .base_model import BaseLLMModel


class OllamaClient(BaseLLMModel):
    def __init__(self, model_name, user_name="", ollama_host="", backend_model="") -> None:
        super().__init__(model_name=model_name, user=user_name)
        self.backend_model = backend_model
        self.ollama_host = ollama_host
        self.update_token_limit()

    def get_model_list(self):
        client = Client(host=self.ollama_host)
        return client.list()

    def update_token_limit(self):
        lower_model_name = self.backend_model.lower()
        if "mistral" in lower_model_name:
            self.token_upper_limit = 8*1024
        elif "gemma" in lower_model_name:
            self.token_upper_limit = 8*1024
        elif "codellama" in lower_model_name:
            self.token_upper_limit = 4*1024
        elif "llama2-chinese" in lower_model_name:
            self.token_upper_limit = 4*1024
        elif "llama2" in lower_model_name:
            self.token_upper_limit = 4*1024
        elif "mixtral" in lower_model_name:
            self.token_upper_limit = 32*1024
        elif "llava" in lower_model_name:
            self.token_upper_limit = 4*1024

    # def get_answer_stream_iter(self):
    #     if self.backend_model == "":
    #         return i18n("请先选择Ollama后端模型\n\n")
    #     client = Client(host=self.ollama_host)
    #     response = client.chat(model=self.backend_model, messages=self.history,stream=True)
    #     partial_text = ""
    #     for i in response:
    #         response = i['message']['content']
    #         partial_text += response
    #         yield partial_text
    #     self.all_token_counts[-1] = count_token(partial_text)
    #     yield partial_text

    def construct_text(self,role, text):
        return {"role": role, "content": text}
    def construct_system(self,text):
        return self.construct_text("system", text)
    def get_answer_stream_iter(self, prompt=INITIAL_SYSTEM_PROMPT):
        if self.backend_model == "":
            return i18n("请先选择Ollama后端模型\n\n")

        # 添加 prompt 到历史消息中，作为一个系统或用户消息
        if prompt:
            self.history = [self.construct_system(prompt), *self.history]

        # 创建客户端
        client = Client(host=self.ollama_host)

        # 请求模型返回流式响应
        response = client.chat(model=self.backend_model, messages=self.history, stream=True)

        partial_text = ""

        # 逐步处理每一部分响应
        for i in response:
            # 从每个响应中提取文本内容
            response_content = i['message']['content']
            partial_text += response_content

            # 输出部分结果
            yield partial_text

        # 计算最后的 token 数量
        self.all_token_counts[-1] = count_token(partial_text)

        # 输出完整的文本
        yield partial_text