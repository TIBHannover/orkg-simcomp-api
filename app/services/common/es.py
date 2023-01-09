import os

from elasticsearch import Elasticsearch, TransportError, ApiError

from app.services.common.base import OrkgSimCompApiService


class ElasticsearchService(OrkgSimCompApiService):

    def __init__(self):
        super().__init__(logger_name=__name__)

        self.client = Elasticsearch(hosts=[os.getenv('ORKG_SIMCOMP_API_ES_HOST', 'http://localhost:9200')])

    @staticmethod
    def get_instance():
        return ElasticsearchService()

    def exists(self, index):
        return self.client.indices.exists(index=index)

    def create_index(self, index: str):
        self.logger.debug('Creating index "{}"'.format(index))
        self.client.indices.create(index=index)

    def delete_index(self, index: str):
        self.logger.debug('Deleting index "{}"'.format(index))
        self.client.indices.delete(index=index, allow_no_indices=True, ignore_unavailable=True)

    def index(self, index: str, document_id: str, document: dict):
        self.logger.debug('Indexing document "{}"'.format(document_id))

        if not document:
            return

        self.client.index(index=index, id=document_id, document=document)

    def query(self, index: str, q_key: str, q_value: str, top_k: int):
        if not q_value:
            return {}

        q = self._escape_special_characters(q_value)
        self.logger.debug('Querying index "{}" with q="{}"'.format(index, q))
        query = {
            'match': {
                q_key: {
                    'query': q
                }
            }
        }

        try:
            results = self.client.search(index=index, query=query, size=top_k * 2, track_scores=True)
            similar = {hit["_id"]: hit["_score"] for hit in results["hits"]["hits"]}

            for key in similar.keys():
                similar[key] = similar[key] / results['hits']['max_score']

            return {k: v for k, v in similar.items()}

        except (ApiError, TransportError, KeyError) as e:
            self.logger.warning('An error occurred while querying index "{}".'
                                ' Error: {}'.format(index, str(e)))
            return {}

    @staticmethod
    def _escape_special_characters(q):
        """
        Apply escaping to the passed in query terms escaping special characters like : , etc.
        See `This documentation
         <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-query-string-query.html#_reserved_characters>`_
        for more details.
        """
        escape_rules = {
            '+': r'\\+',
            '-': r'\\-',
            '=': r'\\=',
            '&': r'\\&',
            '|': r'\\|',
            '!': r'\\!',
            '(': r'\\(',
            ')': r'\\)',
            '{': r'\\{',
            '}': r'\\}',
            '[': r'\\[',
            ']': r'\\]',
            '^': r'\\^',
            '"': r'\"',
            '~': r'\\~',
            '*': r'\\*',
            '?': r'\\?',
            ':': r'\\:',
            '\\': r'\\\\',
            '/': r'\\/',
            '>': r' ',
            '<': r' '
        }

        def escaped_seq(term):
            """
            Yield the next string based on the next character (either this char or escaped version.
            """
            for char in term:
                if char in escape_rules.keys():
                    yield escape_rules[char]
                else:
                    yield char

        term = q.replace('\\', r'\\')  # escape \ first
        return "".join([nextStr for nextStr in escaped_seq(term)])
