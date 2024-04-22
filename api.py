import requests
from urllib.parse import urljoin
from typing import List, Dict, Any
from utils import DBConfig
from typing import Union, List, Tuple, Optional
from pydantic import BaseModel
from utils import DBConfig
from typing import List, Dict, Any, Literal
from io import BytesIO
import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed


class UrlLoaderContainer(BaseModel):
    urls: list
    db_name: str
    adddtional_metadata: Dict[str, Any]

class GreedyUrlLoaderContainer(BaseModel):
    urls: list
    db_name: str
    depth: int
    adddtional_metadata: Dict[str, Any]
    browser: Literal["selenium", "requests"]

class InfoRetrieverParamsContainer(BaseModel):
    query: str
    recursion_limit: int
    db_names: List[str]
    filters: List[Dict[str, Any]]

class TenStepParamsContainer(BaseModel):
    company_name: str
    # recursion_limit: int
    # db_names: List[str]
    # filters: List[Dict[str, Any]]

class LlamaIndexRetrievalContainer(BaseModel):
    question: str

class ChatSessionContainer(BaseModel):
    session_id: str
    question: str

class ImpaxAIRAAPI:
    endpoint = os.environ.get("AI_ASSISTANT_API_ENDPOINT")
    # endpoint = "http://localhost:8000"
    session = requests.Session()
    default_header = {
        'accept': 'application/json',
        'Content-Type': 'application/json' 
    }

    def _chat(self, session_id: str, question: str):
        url = urljoin(self.endpoint, "/v0/llamaindex/chat/chat/")
        data = {
            "session_id": session_id,
            "question": question
        }
        inputs = ChatSessionContainer(**data)
        result = self.session.post(url, headers=self.default_header, json=inputs.model_dump())
        return result.json()
    
    @classmethod
    def chat(cls, session_id: str, question: str):
        return cls()._chat(session_id=session_id, question=question)
    
    def _clear_chat_session(self, session_id: str):
        url = urljoin(self.endpoint, "/v0/llamaindex/chat/clear-chat-session/")
        data = {
            "session_id": session_id,
            "question": ""
        }
        inputs = ChatSessionContainer(**data)
        result = self.session.post(url, headers=self.default_header, json=inputs.model_dump())
        return result.json()
    
    @classmethod
    def clear_chat_session(cls, session_id: str):
        return cls()._clear_chat_session(session_id=session_id)
    
    def _upload_files(self, session_id: str, files_stream: List[BytesIO]):
        url = urljoin(self.endpoint, f"/v0/local-ingestion/{session_id}/uploadfile/")
        files_stream_ = []
        for stream in files_stream:
            # stream = open(fpath, "rb")
            files_stream_.append(("files", stream))
        response = requests.post(url, files=files_stream_)
        return response

    def _chat_with_uploads(self, session_id: str, question: str, files_stream: List[str]):
        res = self._upload_files(session_id, files_stream)
        url = urljoin(self.endpoint, f"/v0/llamaindex/chat-with-uploads/chat/")
        inputs = ChatSessionContainer(session_id=session_id, question=question)
        response = requests.post(url, json=inputs.model_dump())
        return response.json()
    
    @classmethod
    def chat_with_uploads(cls, session_id: str, question: str, files_stream: List[str]):
        response = cls()._chat_with_uploads(session_id=session_id, question=question, 
                                            files_stream=files_stream)
        return response
    
    def _clear_chat_with_upload_session(self, session_id: str):
        url = urljoin(self.endpoint, "/v0/llamaindex/chat-with-uploads/clear-chat-session/")
        data = {
            "session_id": session_id,
            "question": ""
        }
        inputs = ChatSessionContainer(**data)
        result = self.session.post(url, headers=self.default_header, json=inputs.model_dump())
        return result.json()
    
    @classmethod
    def clear_chat_with_upload_session(cls, session_id: str):
        return cls()._clear_chat_session(session_id=session_id)

    def _write_ten_steps(self, company_name: str):
        inputs = TenStepParamsContainer(company_name=company_name)
        def get_result(endpoint):
            url = urljoin(self.endpoint, endpoint)
            results = self.session.post(url, json=inputs.model_dump())
            return results.json()#, endpoint
        endpoints = {"/v0/langchain/report-writing/ten-step-writer/market-overview/": "Market Overview",
                     "/v0/langchain/report-writing/ten-step-writer/cit-tse/": "CIT and TSE",
                     "/v0/langchain/report-writing/ten-step-writer/business-model/": "Business Model",
                     "/v0/langchain/report-writing/ten-step-writer/competitive-advantage/": "Competitive Advantage" ,
                     "/v0/langchain/report-writing/ten-step-writer/risks/": "Risks",
            }
        # results = []
        # # with ThreadPoolExecutor(max_workers=8) as executor:
        # #     futures = [executor.submit(get_result, endpoint) for endpoint in endpoints.keys()]
        #     for future in as_completed(futures):
        #         result, endpoint = future.result()
        #         title = endpoints.get(endpoint)
        #         results.append((title, result.json()))
        for endpoint, title in endpoints.items():
            result = get_result(endpoint)
            yield (title, result)
    
    @classmethod
    def write_ten_steps(cls, company_name: str):
        return cls()._write_ten_steps(company_name)


    @classmethod
    def simple_search(cls, search_terms: str):
        url = urljoin(cls().endpoint, "/v0/llamaindex/get-simple-answers/")
        inputs = LlamaIndexRetrievalContainer(question=search_terms)
        results = cls().session.post(url, json=inputs.model_dump())
        return results.json()
    
    @classmethod
    def multistep_search(cls, search_terms: str):
        url = urljoin(cls().endpoint, "/v0/llamaindex/get-complex-answers/")
        inputs = LlamaIndexRetrievalContainer(question=search_terms)
        results = cls().session.post(url, json=inputs.model_dump())
        return results.json()
        

    # def _get_answer(self, query: str, db_names: List[str], filters: List[Dict[str, Any]]):
    #     url = urljoin(self.endpoint, "/info-retrieval/get-answer/")
    #     data = {
    #         "query": query,
    #         "db_names": db_names,
    #         "recursion_limit": 20,
    #         "filters": filters
    #     }
    #     inputs = InfoRetrieverParamsContainer(**data)
    #     res = self.session.post(url, json=inputs.model_dump())
    #     result = res.json()
    #     return result
    
    # @classmethod
    # def get_answer(cls, query: str, db_names: List[str], filters: List[Dict[str, Any]]):
    #     return cls()._get_answer(query, db_names, filters)
    
    # def _write_description(self, company_name):
    #     url = urljoin()