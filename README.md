# Konsultprofiler Graph Database

Detta projekt implementerar en Neo4j-grafdatabas för att hantera konsultprofiler och deras relationer.

## Struktur

- `docker-compose.yml` - Neo4j container konfiguration
- `import_profiles.py` - Python-skript för att importera profiler
- `pyproject.toml` - Projektkonfiguration och beroenden
- `schema.json` - Databasens schema och constraints
- JSON-filer med konsultprofiler

## Installation och utveckling

1. Installera Docker och Docker Compose
2. Skapa och aktivera Python-miljö med uv:
   ```bash
   uv venv
   source .venv/bin/activate  # Linux/Mac
   # eller
   .venv\Scripts\activate     # Windows
   ```
3. Skapa en .env-fil i projektets rot:
   ```bash
   # Neo4j connection details
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=password
   ```
4. Installera beroenden:
   ```bash
   pip install uv
   uv pip install -e .
   ```

## Köra med Docker

1. Bygg Docker-imagen:
   ```bash
   docker build -t konsultskills-graphdb .
   ```
2. Starta containern:
   ```bash
   docker run -p 5000:5000 konsultskills-graphdb
   ```
3. Öppna applikationen (om du har en webbtjänst):
   Gå till [http://localhost:5000](http://localhost:5000) i webbläsaren.

### Exempel på Dockerfile med pyproject.toml och uv

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml ./
COPY . .

RUN uv pip install -e .

EXPOSE 5000

CMD ["python", "import_profiles.py"]
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

## Använda Neo4j Browser

Efter att ha startat databasen med `make all` kan du använda Neo4j Browser för att utforska och analysera datan:

1. Öppna Neo4j Browser genom att gå till http://localhost:7474 i din webbläsare
2. Logga in med:
   - Username: neo4j
   - Password: (se .env-filen)

### Användbara Cypher-queries

Här är några exempel på queries du kan köra i Neo4j Browser:

#### Se alla noder och deras relationer
```cypher
MATCH (n) RETURN n LIMIT 25;
```

#### Se antal noder per typ
```cypher
MATCH (n) 
RETURN labels(n) as NodeType, count(*) as Count 
ORDER BY Count DESC;
```

#### Se en specifik konsult och alla dess relationer
```cypher
MATCH (c:Consultant {name: "Mattias Larsen"})-[r]-(n) 
RETURN c, r, n;
```

#### Se alla approaches och vilka assignments som använder dem
```cypher
MATCH (a:Assignment)-[r:USES_APPROACH]->(ap:Approach)
RETURN a, r, ap;
```

#### Sök efter konsulter med specifik kompetens
```cypher
MATCH (c:Consultant)-[:KNOWS_TECHNOLOGY]->(t:Technology)
WHERE t.name CONTAINS 'AI'
RETURN c.name, collect(t.name) as Technologies;
```

#### Hitta konsulter med liknande arbetssätt
```cypher
MATCH (c1:Consultant)-[:PERFORMED]->(a1:Assignment)-[:USES_APPROACH]->(ap:Approach)<-[:USES_APPROACH]-(a2:Assignment)<-[:PERFORMED]-(c2:Consultant)
WHERE c1 <> c2
RETURN c1.name, c2.name, collect(DISTINCT ap.name) as CommonApproaches
LIMIT 10;
```

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

print(f"[IMPORT] {data.get('name')}: {len(data.get('assignments', []))} assignments, "
      f"{len(data.get('technologies', []))} technologies, "
      f"{len(data.get('methods', []))} methods, "
      f"{len(data.get('tools', []))} tools, "
      f"{len(data.get('languages', []))} languages, "
      f"{len(data.get('education', []))} education")