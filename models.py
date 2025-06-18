from dataclasses import dataclass

@dataclass
class Trainer:
    id: int
    name: str
    telegram_id: int
    priority: int
    clients_count: int

@dataclass
class Client:
    id: int
    name: str
    phone: str
    date: str
    assigned_trainer_id: int
