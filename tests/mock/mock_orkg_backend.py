import networkx as nx


class OrkgBackendWrapperServiceMock:

    def __init__(self):
        self.contributions = {
            '123': {
                'subgraph': self.__create_subgraph('123'),
                'details': {
                    'label': 'test label',
                    'paper_id': 'test paper_id',
                    'paper_label': 'test paper_label'
                }
            },
            '234': {
                'subgraph': self.__create_subgraph('234'),
                'details': {
                    'label': 'test label',
                    'paper_id': 'test paper_id',
                    'paper_label': 'test paper_label'
                }
            },
            '345': {
                'subgraph': self.__create_subgraph('345'),
                'details': {
                    'label': 'test label',
                    'paper_id': 'test paper_id',
                    'paper_label': 'test paper_label'
                }
            }
        }

    @staticmethod
    def get_instance():
        return OrkgBackendWrapperServiceMock()

    def get_contribution_ids(self):
        return list(self.contributions.keys())

    def get_subgraph(self, thing_id):
        return self.contributions.get(thing_id, {}).get('subgraph', None)

    def get_contribution_details(self, contribution_id):
        return self.contributions.get(contribution_id, {}).get('details', None)

    @staticmethod
    def __create_subgraph(thing_id):
        subgraph = nx.DiGraph()

        subgraph.add_node(node_for_adding=thing_id, label='Contribution {}'.format(thing_id))
        subgraph.add_node(node_for_adding=thing_id + ' target', label='Contribution {}'.format(thing_id))
        subgraph.add_edge(thing_id, thing_id + ' target', label='Predicate {}'.format(thing_id))

        return subgraph
