# Konsultprofiler Graph Database

Detta projekt implementerar en Neo4j-grafdatabas för att hantera konsultprofiler och deras relationer.

## Struktur

- `docker-compose.yml` - Neo4j container konfiguration
- `import_profiles.py` - Python-skript för att importera profiler
- `pyproject.toml` - Projektkonfiguration och beroenden
- `schema.json` - Databasens schema och constraints
- JSON-filer med konsultprofiler

## Installation

1. Installera Docker och Docker Compose
2. Skapa och aktivera Python-miljö med uv:
   ```bash
   uv venv
   source .venv/bin/activate  # Linux/Mac
   # eller
   .venv\Scripts\activate     # Windows
   ```
3. Installera beroenden (välj en av metoderna):

   Metod 1 (rekommenderad):
   ```bash
   uv pip install -e .
   ```

   Metod 2 (backup om metod 1 inte fungerar):
   ```bash
   uv pip install neo4j python-dotenv tqdm
   ```

## Användning

1. Starta Neo4j:
   ```bash
   docker-compose up -d
   ```

2. Vänta tills Neo4j är igång (kontrollera loggarna med `docker-compose logs -f`)

3. Kör import-skriptet:
   ```bash
   python import_profiles.py
   ```

4. När du är klar, stäng ner Neo4j:
   ```bash
   docker-compose down
   ```

## Neo4j Browser

Du kan komma åt Neo4j Browser på http://localhost:7474
- Användarnamn: neo4j
- Lösenord: password

## Datamodell

### Noder

- **Consultant**: Konsultprofiler med egenskaper som namn, email, etc.
- **Technology**: Teknologier och plattformar (t.ex. Python, React, Azure)
- **Method**: Metoder och arbetssätt (t.ex. SAFe, Hypotesdriven utveckling)
- **Tool**: Verktyg (t.ex. Jira, Confluence, PowerBI)
- **Language**: Språk (t.ex. Svenska, Engelska)
- **Education**: Utbildningar (t.ex. MSc Teknisk Fysik)
- **Assignment**: Uppdrag med period och beskrivning

### Relationer

- `(Consultant)-[:KNOWS_TECHNOLOGY]->(Technology)`
- `(Consultant)-[:USES_METHOD]->(Method)`
- `(Consultant)-[:USES_TOOL]->(Tool)`
- `(Consultant)-[:SPEAKS {level: "Modersmål"}]->(Language)`
- `(Consultant)-[:HAS_EDUCATION {period: "1998-2004"}]->(Education)`
- `(Consultant)-[:PERFORMED]->(Assignment)`

### Constraints

- Unika namn för konsulter
- Unika namn för teknologier
- Unika namn för metoder
- Unika namn för verktyg
- Unika namn för språk
- Unika namn för utbildningar

## Exempel på queries

### Hitta konsulter med specifik teknologi
```cypher
MATCH (c:Consultant)-[:KNOWS_TECHNOLOGY]->(t:Technology {name: 'Python'})
RETURN c.name, c.role
```

### Hitta konsulter med specifik utbildning
```cypher
MATCH (c:Consultant)-[:HAS_EDUCATION]->(e:Education {name: 'MSc Teknisk Fysik'})
RETURN c.name, c.role
```

### Hitta konsulter som kan både Python och React
```cypher
MATCH (c:Consultant)-[:KNOWS_TECHNOLOGY]->(t1:Technology {name: 'Python'})
MATCH (c)-[:KNOWS_TECHNOLOGY]->(t2:Technology {name: 'React'})
RETURN c.name, c.role
```