# Fontes de dados — eventos corporativos (MVP 2)

## Fatos relevantes — CVM Dados Abertos

| Item | Detalhe |
|---|---|
| **Fonte** | Portal [dados.cvm.gov.br](https://dados.cvm.gov.br/) |
| **Dataset** | Cias Abertas → Documentos → Fato Relevante |
| **Formato** | CSV (`;`, encoding Latin-1) |
| **Autenticação** | Não requerida |
| **Implementação** | `collectors/events_collector.py` |

### URL dos arquivos

```
https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FATO_RELEVANTE/DADOS/fato_relevante_cia_aberta_{ANO}.csv
```

O collector carrega o ano corrente e, se necessário, o ano anterior conforme `EVENTS_LOOKBACK_DAYS`.

### Campos usados

| Campo CSV | Uso |
|---|---|
| `CNPJ_CIA` | Vincular evento ao ticker (via CNPJ da BRAPI) |
| `ASSUNTO` | Título do evento |
| `DT_ENTREGA` / `DT_REFER` | Data de publicação |
| `LINK_DOC` | URL do documento completo (PDF/HTML) |

### Resolução ticker → CNPJ

A CVM não expõe ticker no CSV. O collector consulta a **brapi.dev**:

```
GET https://brapi.dev/api/quote/{ticker}
```

e extrai o CNPJ do payload (`cnpj` ou `summaryProfile`).

### Limitações conhecidas

- **FIIs** (`*11`): podem não constar no dataset de cias abertas — retorno vazio esperado.
- **Sem API streaming**: download periódico do CSV (1x por execução do job, não por ticker).
- **Conteúdo completo** do fato relevante está no PDF/HTML (`LINK_DOC`); o collector traz metadados (título + link).
- **Classificação** (M&A, guidance, etc.) não é padronizada pela CVM — fica para o MVP 3 (IA).

### Próximos passos (evolução)

- Cache local do CSV diário para reduzir bandwidth
- Mapeamento ticker↔CNPJ persistido em banco
- Enriquecimento com texto do documento (MVP 3)

## Dividendos e JCP

Ver `collectors/dividends_collector.py` — fonte **brapi.dev** (`?dividends=true`).
