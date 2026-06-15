# Documentação — Radar Financeiro IA



Base de conhecimento do projeto. Tudo que precisamos para ir da Fase 0 até o MVP 5.



## Índice



| Documento | Conteúdo |

|---|---|

| [plano-implementacao.md](plano-implementacao.md) | **Documento mestre** — fases, critérios de aceite, docs vs skills vs rules |

| [product/visao-geral.md](product/visao-geral.md) | Visão, problema, objetivo, público-alvo, diferencial |

| [product/roadmap.md](product/roadmap.md) | MVPs 1 a 5 com exemplos |

| [architecture/pipeline.md](architecture/pipeline.md) | Arquitetura técnica e estrutura de pastas |

| [backlog/](backlog/README.md) | Estórias por fase |

| [prompts/](prompts/README.md) | Prompts de implementação derivados das estórias |
| [operations/database-migrations.md](operations/database-migrations.md) | Migrations Alembic — setup e comandos |



## Como usar



1. **Planejamento** → `plano-implementacao.md` + backlog da fase

2. **Implementar** → consulte a estória no backlog e invoque o prompt:

   > Implemente a estória MVP1-01 conforme `docs/prompts/fase-1/01-coletar-variacoes.md`

3. **Concluir** → marque a estória como concluída no backlog

4. **Padrão repetir 3+ vezes** → extraia uma skill em `.cursor/skills/`



## Status atual



- [x] Fase 0 — documentação e convenções (incl. F0-06 Alembic)

- [x] Fase 1 — MVP 1 (Radar Diário) — [backlog](backlog/fase-1/fase-1-mvp1.md)

- [ ] Fase 2 — MVP 2 (Eventos Relevantes)

- [ ] Fase 3 — MVP 3 (Inteligência Financeira)

- [ ] Fase 4 — MVP 4 (Personalização)

- [ ] Fase 5 — MVP 5 (Assistente Conversacional)

