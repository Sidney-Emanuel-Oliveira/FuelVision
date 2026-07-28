# Front-end do FuelVision

Dashboard React e TypeScript que consome a API Spring Boot do projeto. O guia completo está em [`docs/frontend/DASHBOARD.md`](../docs/frontend/DASHBOARD.md).

## Execução local

Com a API ativa em `http://localhost:8080`:

```bash
npm install
npm run dev
```

Acesse `http://localhost:5173`. O Vite encaminha requisições `/api` para o Back-end local.

## Verificações

```bash
npm run typecheck
npm run lint
npm run format:check
npm test
npm run build
```

O dashboard não possui dados simulados em produção. Os mocks existentes aparecem somente nos testes automatizados.
