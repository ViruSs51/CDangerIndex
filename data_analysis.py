import json
import openai

from config import SECRET_TOKEN

class AnalysisData:
    def __init__(self, secret_token: str):
        openai.api_key = secret_token

        self.dataset = {}

    def gpt_request(self, prompt: str, model: str, tokens: int=1000):
        response = openai.ChatCompletion.create(
            model=model,  
            messages=[
              {"role": "system", "content": prompt}
            ],
            max_tokens=tokens
        )
        return response

    def open_json(self, file: str) -> dict:
        try:
            with open(file, 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)
        except FileNotFoundError:
            data = {}

        return data
    
    def get_danger_level(self, title: str, location: str, description: str, category: str):
        response_danger_level = self.gpt_request(
            prompt=f'''Evaluează nivelul de pericol al știrii pe o scară de la 0.01 pana la 100.0
                de la cel mai mic pericol pana la cel mai mare pericol

                Ia in considerarea ca pericolul se masoara cat de periculos este in zona unde e stirea data pentru un copil sau femeie
                Ia în considerare titlul, categoria, locația și descrierea evenimentului pentru a face evaluarea. 
                
                Returnează DOAR un numar (de la 0.01 pana la 100.0) și nimic altceva! 

                Iată detaliile: Titlu: {title}, Locație: {location}, Descriere: {description}, {category}''',
            model='gpt-4o',
            tokens=4096
        )

        return float(response_danger_level['choices'][0]['message']['content'])

    def generate_dataset(self):
        data = self.open_json(file='data/news_markdown_data.json')
        news_list = []

        for url in data:
            for page in data[url]:
                print(url)

                response_category = self.gpt_request(
                    prompt=f'''Clasifică știrea după categoriile date: 
                        Traffic Accident,
                        Violence,
                        Animal Attack,
                        Flood,
                        Murder,
                        Building Collapse,
                        Kidnapping,
                        Arson,
                        Industrial Accident,
                        Sexual Harassment,
                        Protest,
                        Nuclear Power Plant Accident,
                        Fire,
                        Terrorism,
                        Robbery, 
                        Assault,
                        Bomb Threat,
                        Gas Leak,
                        Road Block,
                        Riots,

                        Dacă nu se încadrează în niciuna dintre categoriile specificate, returnează LOC GOL ȘI MAI MULT NIMIC, ASA INSEAMNA CA LASI LOC GOL CUM SI ARATA LOC GOL NU SCRII NIMICCCCCC! 
                        Categoria trebuie să fie bazată pe evenimentul real din știre, nu pe temele discutate. De exemplu, dacă este un protest al femeilor împotriva violării, clasificarea corectă este „Protest”, nu „Protest și Violare”. 

                        Iată datele cu știrea: {page}''',
                    model='gpt-4o',
                    tokens=4096
                )
                if not response_category['choices'][0]['message']['content']: continue

                response_date = self.gpt_request(
                    prompt=f'''Te rog să extragi data din știre și să o formatezi astfel: an:luna:zi/ora:minute. 
                        Dacă în știre nu este specificată o oră, lasă locul gol. 
                        Daca nu ai data sau ora returneaza loc gol si nimic mai mult
                        Iată ce data trebuie să extragi: {page}''',
                    model='gpt-4o',
                    tokens=4096
                )
                if not response_date['choices'][0]['message']['content']: continue
                
                response_location = self.gpt_request(
                    prompt=f'''Te rog să returnezi locația exactă menționată în știre, până la nivel de apartament, dacă este posibil. 
                        RETURNEAZĂ DOAR LOCATIA (țara, oraș, stradă, apartament) FĂRĂ NICIUN ALT TEXT ADIȚIONAL. 
                        Dacă nu găsești informații relevante, returnează un loc gol. 
                        Daca Locatia stirei nu in zona tarii Moldova atunci returneaza asemenea un loc gol.
                        Dacă informațiile nu includ cel puțin raionul sau strada, returnează de asemenea un loc gol. 
                        Iată ce trebuie să extragi: {page}''',
                    model='gpt-4o',
                    tokens=4096
                )
                if not response_location['choices'][0]['message']['content']: continue

                response_description = self.gpt_request(
                    prompt=f'''Te rog să extragi textul integral din știre exact așa cum este scris. 
                        RETURNEAZĂ DOAR TEXTUL FĂRĂ NICIUN ALT TEXT SUPLIMENTAR. 
                        Asigură-te că textul este curat (fără elemente de cod sau caractere speciale) și într-un singur rând. 
                        Iată ce trebuie să extragi: {page}''',
                    model='gpt-4o',
                    tokens=4096
                )

                response_title = self.gpt_request(
                    prompt=f'''Te rog să extragi titlul din știre exact așa cum este scris. 
                        RETURNEAZĂ DOAR TITLUL FĂRĂ NICIUN ALT TEXT SUPLIMENTAR. 
                        Iată ce trebuie să extragi: {page}''',
                    model='gpt-4o',
                    tokens=4096
                )
                response_media = self.gpt_request(
                    prompt=f'''Te rog să returnezi toate linkurile media relevante asociate cu știrea, inclusiv videoclipuri și imagini, care sunt bazate pe conținutul acesteia. 
                        Dacă există mai multe linkuri, separă-le prin virgulă. 
                        Dacă nu există linkuri media, returnează LOC GOL. 

                        Iată datele cu știrea: {page}''',
                    model='gpt-4o',
                    tokens=4096
                )
                response_danger_level = self.gpt_request(
                    prompt=f'''Evaluează nivelul de pericol al știrii pe o scară de la 0.01 pana la 100.0
                        de la cel mai mic pericol pana la cel mai mare pericol

                        Ia in considerarea ca pericolul se masoara cat de periculos este in zona unde e stirea data pentru un copil sau femeie

                        Ia în considerare titlul, categoria, locația și descrierea evenimentului pentru a face evaluarea. 

                        Returnează DOAR un numar (de la 0.01 pana la 100.0) și nimic altceva! 

                        Iată detaliile: Titlu: {response_title['choices'][0]['message']['content']}, Locație: {response_location['choices'][0]['message']['content']}, Descriere: {response_description['choices'][0]['message']['content']}, {response_category['choices'][0]['message']['content']}''',
                    model='gpt-4o',
                    tokens=4096
                )


                new_data = {
                    'whenHappened': response_date['choices'][0]['message']['content'],
                    'location': response_location['choices'][0]['message']['content'],
                    'title': response_title['choices'][0]['message']['content'],
                    'description': response_description['choices'][0]['message']['content'],
                    'category': response_category['choices'][0]['message']['content'],
                    'media': response_media['choices'][0]['message']['content'],
                    'danger_level': response_danger_level['choices'][0]['message']['content'],
                    'radius': 0.1,
                }
                print(new_data)
                news_list.append(new_data)
                

        self.dataset = {"data": news_list}

        return self.dataset
    
    def update_dataset_file(self, file_name: str):
        try:
            with open(file_name, 'r', encoding='utf-8') as json_file:
                dataset = json.load(json_file)
        except FileNotFoundError:
            dataset = {}

        combined_news_data = {**dataset, **self.dataset}

        with open(file_name, 'w', encoding='utf-8') as json_file:
            json.dump(combined_news_data, json_file, indent=4)


#ad = AnalysisData(SECRET_TOKEN)
#ad.generate_dataset()
#ad.update_dataset_file(file_name='data/dataset.json')