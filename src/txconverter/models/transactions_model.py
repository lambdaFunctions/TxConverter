from pydantic import BaseModel, ConfigDict


class TransactionsModel(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: int
    description: str
    amount: str
    date: str
    created_at: str

    def get_id(self) -> str:
        return str(self.id)
