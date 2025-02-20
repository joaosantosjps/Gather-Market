import os
import sqlalchemy as sal
from decimal import Decimal
from sqlalchemy.engine import url
from sqlalchemy.orm import sessionmaker
from Markt_Database.models import Base



class SQLAlchemyDataPipeline:
    """
    SQLAlchemy Data Pipeline Class
    """

    def __init__(self):
        self.session = self.connect_engine()

    def connect_engine(self):

        connect_url = url.URL(
            drivername=os.getenv("PSQL_TYPE"),
            username="postgres",
            password=os.getenv("PSQL_PASSWORD"),
            host=os.getenv("PSQL_HOST"),
            database="postgres",
            port=5432,
            query={}
        )

        engine = sal.create_engine(connect_url)
        print(engine)
        Base.metadata.create_all(engine)

        session = sessionmaker(autoflush=True)
        session.configure(bind=engine)

        return session()
    

class SQLAlchemyMethods(SQLAlchemyDataPipeline):
    exclude_fields = ["_sa_instance_state", "password", "created_at"]

    def __exclude_data(self, query, properties):
        data = {}
        raw = query.__dict__

        for key in raw.keys():
            if key not in self.exclude_fields:
                data[key] = self.__process_data(raw[key])

        if not properties:
            return data
        else:
            filtered_data = {}
            for property in properties:
                filtered_data[property] = data[property]
            return filtered_data

    def __process_data(self, data):
        if isinstance(data, Decimal):
            return float(data)
        elif isinstance(data, int):
            return int(data)
        elif not data:
            return None
        else:
            return str(data)
        
    def __process_query_data(self, query, properties, join=False):
        if not isinstance(query, list):
            return self.__exclude_data(query, properties)

        if not join:
            data = list(map(lambda row: self.__exclude_data(row, properties), query))
        else:
            data = []

            for table in query:
                dict = {}
                for row in table:
                    dict[str(row.__table__)] = self.__exclude_data(row, properties)
                data.append(dict.copy())

        return data
    
    def insert_one(self, item):
        self.session.add(item)
        self.session.commit()

        return {
            "id": item.id
        }
    
    def select_one(self, model, filter, properties=[]):
        query = self.session.query(model).filter(filter).first()

        if not query:
            return None

        data = self.__process_query_data(query, properties)

        return data
    
    def select_one_with_update(self, model, filter):
        return self.session.query(model).filter(filter).with_for_update().one()
    
    def select_all(self, model, filter, properties=None):
        query = self.session.query(model).filter(filter).all()

        if not query:
            return []

        return self.__process_query_data(query, properties)
    
    def select_all_with_join(self, models, joins, filter, properties=[]):
        query = self.session.query(*models)

        for join in joins:
            query = query.join(*join)

        query = query.filter(filter).all()

        return self.__process_query_data(query, properties, True)