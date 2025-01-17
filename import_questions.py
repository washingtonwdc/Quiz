from pymongo import MongoClient
import json
from datetime import datetime, timezone

def import_questions():
    # Conectar ao MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client['questoes']  # Nome do banco de dados
    
    try:
        # Ler o arquivo JSON
        with open('questions.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Extrair informações do concurso
        concurso = data['prova']
        concurso['created_at'] = datetime.now(timezone.utc)
        
        # Inserir concurso
        concurso_id = db.concursos.insert_one(concurso).inserted_id
        print(f"Concurso importado: {concurso['nome']}")
        
        # Preparar questões
        questoes = []
        for q in data['questoes']:
            q['concurso_id'] = concurso_id
            q['created_at'] = datetime.now(timezone.utc)
            questoes.append(q)
        
        # Inserir questões
        if questoes:
            result = db.questoes.insert_many(questoes)
            print(f"Questões importadas: {len(result.inserted_ids)}")
            
    except Exception as e:
        print(f"Erro na importação: {str(e)}")
    finally:
        client.close()

if __name__ == '__main__':
    import_questions()