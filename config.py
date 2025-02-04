import os
from omegaconf import OmegaConf
from dotenv import load_dotenv
load_dotenv(override=True)

def get_agent_config() -> OmegaConf:
    cfg = OmegaConf.create({
        'customer_id': str(os.environ['VECTARA_CUSTOMER_ID']),
        'corpus_id': str(os.environ['VECTARA_CORPUS_ID']),
        'api_key': str(os.environ['VECTARA_API_KEY'])
    })
    return cfg