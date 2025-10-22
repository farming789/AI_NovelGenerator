#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from abc import ABC, abstractmethod
from typing import List

import requests
from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings


class BaseEmbeddingAdapter(ABC):
    """Embedding 适配器基类"""

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """对一组文本进行 embedding"""
        pass

    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """对单个查询文本进行 embedding"""
        pass


class OpenAIEmbeddingAdapter(BaseEmbeddingAdapter):
    """
    基于 OpenAIEmbeddings（或兼容接口）的适配器
    """

    def __init__(self, api_key: str, base_url: str, model_name: str):
        self._embedding = OpenAIEmbeddings(
            model=model_name,
            openai_api_base=base_url,
            openai_api_key=api_key
        )

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._embedding.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        return self._embedding.embed_query(text)


class AzureOpenAIEmbeddingAdapter(BaseEmbeddingAdapter):
    """
    基于 AzureOpenAIEmbeddings（或兼容接口）的适配器
    """

    def __init__(self, api_key: str, base_url: str, model_name: str):
        # 注意：Azure OpenAI 的 base_url 通常包含部署名称，这里假设用户已正确配置
        self._embedding = AzureOpenAIEmbeddings(
            model=model_name,
            azure_endpoint=base_url,
            api_key=api_key
        )

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._embedding.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        return self._embedding.embed_query(text)


class OllamaEmbeddingAdapter(BaseEmbeddingAdapter):
    """
    基于 Ollama 的适配器
    """

    def __init__(self, model_name: str, base_url: str):
        # Ollama 的 LangChain 集成可能需要特定版本的库
        from langchain_community.embeddings import OllamaEmbeddings
        self._embedding = OllamaEmbeddings(model=model_name, base_url=base_url)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._embedding.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        return self._embedding.embed_query(text)


class MLStudioEmbeddingAdapter(BaseEmbeddingAdapter):
    """
    基于 ML Studio（本地部署）的适配器
    """

    def __init__(self, api_key: str, base_url: str, model_name: str):
        self.api_key = api_key
        self.base_url = f"{base_url.rstrip('/')}/v1/embeddings"
        self.model_name = model_name
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._embed_single(text) for text in texts]

    def embed_query(self, query: str) -> List[float]:
        return self._embed_single(query)

    def _embed_single(self, text: str) -> List[float]:
        payload = {
            "model": self.model_name,
            "input": text
        }
        try:
            response = requests.post(self.base_url, json=payload, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return data['data'][0]['embedding']
        except requests.exceptions.RequestException as e:
            logging.error(f"ML Studio API request failed: {e}")
        except (KeyError, IndexError) as e:
            logging.error(f"Failed to parse ML Studio API response: {e}")
        return []


class GeminiEmbeddingAdapter(BaseEmbeddingAdapter):
    """
    基于 Google Gemini 的适配器
    """

    def __init__(self, api_key: str, model_name: str, base_url: str = None):
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        self.model_name = model_name

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        import google.generativeai as genai
        result = genai.embed_content(model=self.model_name, content=texts, task_type="retrieval_document")
        return result['embedding']

    def embed_query(self, text: str) -> List[float]:
        import google.generativeai as genai
        result = genai.embed_content(model=self.model_name, content=text, task_type="retrieval_query")
        return result['embedding']


class SiliconFlowEmbeddingAdapter(BaseEmbeddingAdapter):
    """
    基于 SiliconFlow 的适配器
    """

    def __init__(self, api_key: str, base_url: str, model_name: str):
        self._embedding = OpenAIEmbeddings(
            model=model_name,
            openai_api_base=base_url,
            openai_api_key=api_key
        )

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._embedding.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        return self._embedding.embed_query(text)


class DashScopeEmbeddingAdapter(BaseEmbeddingAdapter):
    """
    基于阿里百炼 DashScope 的适配器
    专门处理 DashScope 的 OpenAI 兼容接口
    """

    def __init__(self, api_key: str, base_url: str, model_name: str):
        self.api_key = api_key
        self.base_url = f"{base_url.rstrip('/')}/embeddings"
        self.model_name = model_name
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._embed_single(text) for text in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._embed_single(text)

    def _embed_single(self, text: str) -> List[float]:
        payload = {
            "model": self.model_name,
            "input": text
        }
        try:
            response = requests.post(self.base_url, json=payload, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return data['data'][0]['embedding']
        except requests.exceptions.RequestException as e:
            logging.error(f"DashScope API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    logging.error(f"DashScope API error detail: {error_detail}")
                except:
                    logging.error(f"DashScope API response text: {e.response.text}")
        except (KeyError, IndexError) as e:
            logging.error(f"Failed to parse DashScope API response: {e}")
        return []


def create_embedding_adapter(
    interface_format: str,
    api_key: str,
    base_url: str,
    model_name: str
) -> BaseEmbeddingAdapter:
    """
    工厂函数：根据 interface_format 返回不同的 embedding 适配器实例
    """
    fmt = interface_format.strip().lower()
    if fmt == "openai":
        return OpenAIEmbeddingAdapter(api_key, base_url, model_name)
    elif fmt == "azure openai":
        return AzureOpenAIEmbeddingAdapter(api_key, base_url, model_name)
    elif fmt == "ollama":
        return OllamaEmbeddingAdapter(model_name, base_url)
    elif fmt == "ml studio":
        return MLStudioEmbeddingAdapter(api_key, base_url, model_name)
    elif fmt == "gemini":
        return GeminiEmbeddingAdapter(api_key, model_name, base_url)
    elif fmt == "siliconflow":
        return SiliconFlowEmbeddingAdapter(api_key, base_url, model_name)
    elif fmt == "dashscope":
        return DashScopeEmbeddingAdapter(api_key, base_url, model_name)
    else:
        raise ValueError(f"Unknown embedding interface_format: {interface_format}")
