---
name: art-catalog-fichas
description: "Creates professional art cataloging sheets (fichas de catalogacao) for artworks from inventory spreadsheets or website URLs. Use this skill whenever the user wants to create fichas, catalog sheets, or inventory cards for obras de arte, quadros, pinturas, esculturas, gravuras, fotografias artisticas, or any fine art piece. Also triggers on: 'inventario de obras', 'catalogo de arte', 'ficha tecnica de obra', 'catalogar acervo', 'documentar colecao', 'ficha de arte', 'art inventory', 'artwork documentation', 'cataloging sheet'. The skill reads artwork data from spreadsheets (.xlsx, .csv, Google Sheets) or website URLs (gallery pages, artist portfolios, auction listings, exhibition pages), researches each artist online, and generates one DOCX file per artwork with curatorial analysis, conservation notes, and lighting/installation guidelines — ready for architecture and interior design projects."
---

# Art Catalog Fichas

Generate professional artwork cataloging sheets from inventory data or website URLs. Each ficha documents an artwork with identification, physical description, curatorial analysis, and installation/lighting guidelines for architecture and interior design projects. Input can be a spreadsheet, a Google Sheets link, or a website URL (gallery, artist portfolio, auction house, exhibition page).

## When to Use

This skill is designed for art consultants, interior designers, architects, and collectors who need to document artworks in a structured, professional format. It's particularly useful when:

- A spreadsheet lists multiple artworks that each need individual documentation
- A website URL lists artworks (gallery page, artist portfolio, auction listing, exhibition page)
- An architecture/interior design project requires technical specs for artwork placement
- A collection needs formal cataloging with curatorial context
- The user has example fichas they want to replicate at scale

## Workflow Overview

```
1. READ DATA       → Parse spreadsheet OR scrape website URL for artwork inventory
2. FIND EXAMPLES   → Look for existing fichas as format reference (Google Drive, uploads)
3. RESEARCH        → For each artist: search web + Drive for bio, exhibitions, curatorial texts
4. GENERATE        → Create one DOCX per artwork using the ficha template
5. DELIVER         → Save all files to outputs folder
```

## Step 1: Read the Inventory Data

The input can be a **spreadsheet** (.xlsx, .csv, Google Sheets link) or a **website URL** (gallery, artist portfolio, auction listing, exhibition page).

### 1A: Spreadsheet Input

Read it with pandas:

```python
import pandas as pd
df = pd.read_excel('file.xlsx', sheet_name=None)  # read all sheets
```

If the user provides a Google Sheets link, try these approaches in order:
1. Use `google_drive_fetch` MCP if available (note: won't work for Sheets, only Docs)
2. Open in Chrome via `Claude in Chrome` MCP and extract with JavaScript or `get_page_text`
3. Navigate to the `/htmlview` URL and extract table data
4. Ask the user to export as .xlsx or .csv and upload

### 1B: Website URL Input

When the user provides a URL instead of a spreadsheet, extract artwork data from the web page:

**Extraction strategy** (try in order):
1. Use `Claude in Chrome` MCP: navigate to the URL, then use `get_page_text` or `javascript_tool` to extract structured data
2. Use `WebFetch` to retrieve the page HTML, then parse it with Python (BeautifulSoup)
3. If the page requires interaction (infinite scroll, "Load More" buttons, tabs), use Chrome MCP to interact and extract progressively

**Common website patterns:**

| Site type | What to look for | Extraction approach |
|-----------|-----------------|---------------------|
| Gallery portfolio (e.g., luismaluf.com) | Artist pages with artwork grids/lists | Navigate to artist page, extract each artwork's title, medium, dimensions, image URL |
| Auction house (e.g., Christie's, Sotheby's) | Lot listings with details | Extract lot number, artist, title, estimate, medium, dimensions from each listing |
| Artist personal site | Portfolio/works section | Look for artwork cards/entries with title, year, technique, dimensions |
| Exhibition page | Checklist or artwork list | Extract artist names, titles, media from the exhibition checklist |
| Online catalog (e.g., Artsy, Saatchi) | Artwork detail pages | Navigate to each artwork page and extract structured fields |

**Extraction with Chrome MCP:**
```
1. Navigate to URL with `navigate` tool
2. Use `get_page_text` to get full page text
3. If page has artwork listings, use `javascript_tool` to extract structured data:
   - document.querySelectorAll('.artwork-item') or similar selectors
   - Extract: title, artist, medium, dimensions, image URL, price
4. If page has sub-pages for individual artworks, collect those URLs first,
   then visit each one to extract detailed information
5. For paginated sites, navigate through pages collecting data from each
```

**Extraction with WebFetch + Python:**
```python
# After fetching HTML content
from bs4 import BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Look for common artwork containers
artworks = []
for item in soup.select('.artwork, .work-item, .portfolio-item, article'):
    artwork = {
        'title': item.select_one('h2, h3, .title')?.text.strip(),
        'artist': item.select_one('.artist, .author')?.text.strip(),
        'medium': item.select_one('.medium, .technique')?.text.strip(),
        'dimensions': item.select_one('.dimensions, .size')?.text.strip(),
        'image': item.select_one('img')?.get('src'),
    }
    artworks.append(artwork)
```

**Key considerations for URL input:**
- The page structure varies widely — always inspect the DOM first before writing extraction code
- Some galleries use JavaScript-rendered content (React, Vue) — prefer Chrome MCP over WebFetch for these
- If a URL points to a single artwork (not a list), create one ficha from that page's details
- If a URL points to an artist page with multiple works, create one ficha per artwork found
- Always cross-reference extracted data with web search to fill gaps (dimensions, technique, etc.)
- Image URLs found on the page should be included in the "Referencias Fotograficas" section

**Expected columns** (names may vary — match flexibly):

| Concept | Common column names |
|---------|-------------------|
| Item number | ITEM, #, Numero |
| Room/Location | AMBIENTE, Local, Room |
| Artwork title | OBRA, Titulo, Title, Nome |
| Description | DESCRICAO, Descricao, Description |
| Material/Technique | MATERIAL, Tecnica, Technique, Medium |
| Dimensions | DIMENSOES, Dimensoes, Dimensions |
| Notes | OBSERVACOES, Obs, Notes |
| Photo links | LINK, Fotos, Photos, Links |

If columns don't match, infer from content or ask the user.

## Step 2: Find Example Fichas (if provided)

The user may point to existing fichas as format reference. Check:
- Google Drive folders (search with `google_drive_search` for documents containing "Ficha" or "Catalogacao")
- Uploaded files (.docx, .pdf)
- Links to Google Docs

Read the examples fully with `google_drive_fetch` and extract the template structure: section headings, field names, formatting style, and tone. Adapt the output to match what the user already has.

If no examples are provided, use the default template in Step 4.

## Step 3: Research Each Artist

This step is important — it transforms a bare inventory row into a rich, professional document. When the input is a URL, some research may already be done during extraction (the source page itself is rich context), but always supplement with additional searches. For each unique artist in the dataset:

**Web search:**
- Search for `"[artist name]" artista` or `"[artist name]" artist`
- Look for gallery pages, exhibition histories, curatorial texts, museum collections
- Prioritize official gallery pages (they often have the richest bios)

**Google Drive search** (if MCP available):
- Search for documents mentioning the artist's name — the user may have PDFs, curatorial texts, or purchase records

**What to gather:**
- Full name, birth year/place
- Artistic practice and technique description
- Key exhibitions (3-5 most relevant)
- Gallery representation
- Collections/museums that hold their work
- Curatorial quotes or critical context (from PDFs, gallery texts)

**Handling missing info:** If research yields little, work with what the spreadsheet provides. Note "Informacao nao disponivel" for fields you can't fill rather than inventing content.

## Step 4: Generate DOCX Fichas

Use the `docx` skill (read its SKILL.md first) to create professional Word documents. Install docx-js locally if needed:

```bash
mkdir -p project && cd project && npm init -y && npm install docx
```

### Default Ficha Template

Each ficha follows this structure (adapt if user provided examples with different sections):

```
FICHA DE CATALOGACAO DE OBRA DE ARTE
Inventario Consolidado - [Project Name]
═══════════════════════════════════════

1. IDENTIFICACAO DA OBRA
   • Artista: [name (birthplace, year)]
   • Titulo: "[title]"
   • Serie: [if applicable]
   • Tecnica: [medium/technique]
   • Dimensoes: [H x W x D cm]
   • Edicao: [if applicable, e.g., 59/100]
   • Proveniencia: [gallery, auction, gift]
   • Item no Inventario: [number]
   • Ambiente Sugerido: [room]

2. DESCRICAO FISICA E CONSERVACAO
   • Moldura: [frame description or "Sem moldura"]
   • Protecao: [glass, acrylic, none]
   • Estado de Conservacao: [condition + care notes]
   • Composicao: [visual description of the artwork]

3. ANALISE CURATORIAL E CONTEXTO
   [2-3 paragraphs about the artist's practice, this work's
    significance, exhibition history, institutional presence.
    Include quotes from curatorial texts if available.]

4. DIRETRIZES DE INSTALACAO E PROJETO LUMINOTECNICO
   Posicionamento Sugerido: [placement advice for the room]
   Iluminacao:
   • Tipo de luminaria recomendada
   • Temperatura de cor (geralmente 2700K-3000K)
   • Tecnologia (LED sem UV/calor)
   • Angulo de incidencia (tipicamente 30 graus)
   • Notas especiais (reflexos em vidro, texturas, etc.)

5. REFERENCIAS FOTOGRAFICAS E FONTES
   • [photo links]
   • [gallery links]
   • [curatorial text references]

────────────────────────────────────
Documento gerado para fins de inventario patrimonial
e especificacao tecnica de design.
```

### Styling Guidelines

The docx output should feel professional and clean:

- **Font:** Arial throughout, 11pt body, 16pt title, 13pt section headings
- **Title:** Centered, dark navy (#1F3864), bold
- **Subtitle:** Centered, gray (#595959), italic
- **Section headings:** Blue (#2E75B6), bold, with a thin blue bottom border
- **Bullet items:** Use proper docx-js `LevelFormat.BULLET` (never unicode bullets)
- **Body text:** Black, regular weight, 1.15 line spacing
- **Footer note:** Centered, small (9pt), italic, light gray
- **Page size:** A4 with 1-inch margins

### Key docx-js Patterns

```javascript
const { Document, Packer, Paragraph, TextRun, HeadingLevel,
        AlignmentType, BorderStyle, LevelFormat, ExternalHyperlink } = require('docx');

// Bullet config (one per document, reference by name)
const bulletConfig = {
  reference: "bullets",
  levels: [{
    level: 0, format: LevelFormat.BULLET, text: "\u2022",
    alignment: AlignmentType.LEFT,
    style: { paragraph: { indent: { left: 720, hanging: 360 } } }
  }]
};

// Section heading with blue bottom border
function sectionHeading(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 300, after: 150 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "2E75B6", space: 8 } },
    children: [new TextRun({ text, font: "Arial", size: 26, bold: true, color: "2E75B6" })]
  });
}

// Labeled bullet item (bold label + normal value)
function bulletItem(label, value) {
  return new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    spacing: { after: 60 },
    children: [
      new TextRun({ text: `${label}: `, bold: true, font: "Arial", size: 22 }),
      new TextRun({ text: value, font: "Arial", size: 22 })
    ]
  });
}
```

After generating, validate each file:
```bash
python <docx-skill-path>/scripts/office/validate.py output.docx
```

### Lighting Recommendations Reference

Most artworks in residential/commercial interiors follow these principles:

| Artwork type | Light temp | Notes |
|-------------|-----------|-------|
| Oil/acrylic on canvas | 2700-3000K | Warm light enriches pigments |
| Works on paper | 2700K | Minimize UV; lower lux levels |
| Photography | 2700-3000K | Watch for reflections on glass |
| Textiles/mixed media | 2700K | Rasant light reveals texture |
| Sculpture | 3000K | Multiple angles for dimension |

General rules:
- LED technology (no UV, minimal heat)
- 30-degree angle to avoid specular reflection on glass
- Track or recessed adjustable spots preferred
- Neutral wall backgrounds enhance contrast

## Step 5: Deliver

Save all DOCX files to the outputs folder with clear naming:
```
Ficha_01_[Title_Short]_[Artist_LastName].docx
Ficha_02_[Title_Short]_[Artist_LastName].docx
...
```

Present links to the user using `computer://` paths. If there are many files, also mention total count and suggest the user upload them to Google Drive for conversion to Google Docs.

## Handling Revisions

The user may ask to revise a specific ficha with additional information (PDFs, gallery links, curatorial texts). When this happens:

1. Read the new source material thoroughly
2. Identify what information enriches or corrects the original ficha
3. Regenerate only that specific ficha with the enhanced content
4. Keep the same filename to overwrite the previous version

## Edge Cases

- **Multiple artworks on one row:** Some inventory items list a pair or set (e.g., "2 e 3"). Treat as a single ficha documenting the set.
- **Missing data:** Use "Informacao nao disponivel" rather than guessing. Note what's missing so the user can fill gaps.
- **Non-Latin characters:** Ensure proper encoding in the DOCX output.
- **Large inventories (20+ items):** Generate in batches, validating as you go, to catch errors early.
- **URL with incomplete data:** Websites often omit dimensions, edition numbers, or provenance. Mark missing fields as "Informacao nao disponivel" and note the source URL had limited data. Supplement with web search for the artist/title.
- **URL with JavaScript-rendered content:** Some gallery sites (React, Next.js, Vue) don't expose data in raw HTML. Use Chrome MCP's `javascript_tool` or `get_page_text` instead of WebFetch. If content still can't be extracted, ask the user to provide the data in another format.
- **URL pointing to a single artwork:** Create one ficha. The page itself becomes both the data source and a reference in "Referencias Fotograficas e Fontes".
- **URL with paginated results:** Navigate through all pages, collecting artwork data from each, before generating fichas.1
