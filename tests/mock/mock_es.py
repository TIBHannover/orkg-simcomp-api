# -*- coding: utf-8 -*-
import random


class ElasticsearchServiceMock:
    def __init__(self):
        self.db = {}

    @staticmethod
    def get_instance():
        yield ElasticsearchServiceMock()

    def exists(self, index):
        return index in self.db

    def delete_index(self, index):
        pass

    def create_index(self, index):
        pass

    def index(self, index, document_id, document):
        if index not in self.db:
            self.db[index] = {}

        self.db[index][document_id] = document

    def query(self, index, q_key, q_value, top_k):
        similarities = {}
        found = False

        if index in self.db:
            for key, value in self.db[index].items():
                if {q_key: q_value} == value:
                    found = True

                similarities[key] = random.random()

        if found:
            return similarities

        return None
