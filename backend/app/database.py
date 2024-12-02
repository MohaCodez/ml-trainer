from motor.motor_asyncio import AsyncIOMotorClient
from typing import List
from .models import TrainedModel

class Database:
    client: AsyncIOMotorClient = None

    async def connect_to_database(self, url: str):
        self.client = AsyncIOMotorClient(url)
        
    async def close_database_connection(self):
        if self.client:
            self.client.close()

    async def get_all_models(self) -> List[TrainedModel]:
        models = []
        cursor = self.client.ml_models.trained_models.find({})
        async for document in cursor:
            models.append(TrainedModel(**document))
        return models

    async def get_model(self, model_id: str) -> TrainedModel:
        model = await self.client.ml_models.trained_models.find_one({"id": model_id})
        if model:
            return TrainedModel(**model)
        return None

    async def save_model(self, model: TrainedModel):
        await self.client.ml_models.trained_models.insert_one(model.dict())

db = Database() 