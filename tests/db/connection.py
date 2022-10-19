""" Dummy classes and functions for test mocking """
import datetime
import uuid


class Session:

    def add(self, instance):
        pass

    def commit(self):
        pass

    @staticmethod
    def refresh(instance):
        instance.id = uuid.uuid4()

    @staticmethod
    def query(instance):
        instances = Query.create_instances(instance, 10)
        return Query(instances)

    def close(self):
        pass


class Query:

    def __init__(self, instances):
        self.instances = instances

    @staticmethod
    def create_instances(instance, number_of_instances):
        instances = []

        for i in range(number_of_instances):
            instance_obj = instance()

            for column in instance_obj.__mapper__.mapper.columns:
                cls = column.type.python_type
                value = Query.instantiate_value(cls)
                instance_obj.__setattr__(column.name, value)

            instances.append(instance_obj)

        return instances

    @staticmethod
    def instantiate_value(cls):

        if cls is uuid.UUID:
            return uuid.uuid4()

        if cls is datetime.datetime:
            return datetime.datetime.utcnow()

        return cls()

    def offset(self, skip):
        return self

    def limit(self, limit):
        return self

    def all(self):
        return self.instances


def override_get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
