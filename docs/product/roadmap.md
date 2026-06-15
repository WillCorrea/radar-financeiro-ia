# Roadmap — Radar Financeiro IA

## MVP 1 — Radar Diário

**Objetivo:** validar interesse dos usuários.

**Funcionalidades:**

- Monitoramento diário de ativos
- Resumo automático
- Envio diário de mensagem
- Histórico dos alertas

**Exemplo de saída:**

```
Radar Financeiro - 14/06/2026

PETR4 caiu 3,2% na semana.
VALE3 subiu 4,1% no mês.
HGLG11 negocia abaixo do valor patrimonial.

Resumo IA:
O mercado apresenta sinais mistos, com destaque para o setor de commodities e fundos imobiliários.
```

**Status no código:** ~70% — falta variação semana/mês, VP de FIIs, agendamento automático e endpoints de histórico.

---

## MVP 2 — Eventos Relevantes

**Objetivo:** aumentar retenção dos usuários.

**Funcionalidades:**

- Dividendos
- Juros sobre Capital Próprio (JCP)
- Fatos relevantes
- Resultados trimestrais
- Mudanças de rating
- Comunicados corporativos

**Exemplo de saída:**

```
Alerta:

PETR4 anunciou dividendos de R$ X por ação.
Data-base: XX/XX/XXXX
Pagamento previsto: XX/XX/XXXX
```

**Status no código:** `EventAnalyzer` existe como placeholder.

---

## MVP 3 — Inteligência Financeira

**Objetivo:** adicionar interpretação via IA.

**Funcionalidades:**

- Resumo de fatos relevantes
- Interpretação de resultados
- Explicações simplificadas
- Contextualização de eventos

**Exemplo de saída:**

```
Resultado PETR4:

Apesar da queda de receita no trimestre, a companhia apresentou melhora na geração de caixa e manteve sua política de distribuição de dividendos.
```

**Status no código:** `SummaryAgent` cobre apenas resumo diário; interpretação contextual ainda não existe.

---

## MVP 4 — Personalização

**Objetivo:** transformar o produto em um assistente individual.

**Funcionalidades:**

- Carteira personalizada
- Lista de ativos favoritos
- Alertas personalizados
- Filtros por perfil

**Exemplo:**

Usuário monitora: PETR4, VALE3, ITSA4, MXRF11 → o sistema envia apenas eventos desses ativos.

**Status no código:** modelos `User` e `UserAsset` existem; lógica parcial no job; sem API/UI.

---

## MVP 5 — Assistente Conversacional

**Objetivo:** permitir interação direta com IA.

**Exemplos:**

```
Usuário: Como está PETR4?
IA: [Resumo atualizado do ativo]

Usuário: Quais FIIs estão com maior desconto hoje?
IA: [Lista atualizada dos fundos monitorados]
```

**Status no código:** não iniciado.
