# React + TypeScript + Vite

## Patient table pagination

The patient table displays 10 encounters per page. Previous and Next change the
visible rows; the final page displays any remaining encounters. With no encounters,
the table is empty and both buttons are disabled on page 1 of 1.

This template provides a minimal setup to get React working in Vite with HMR and some Oxlint rules.

## API hook

`src/hooks/useApi.ts` fetches JSON on mount and whenever its URL changes. It exposes
`data`, `isLoading`, `error`, `fetchData()`, `createData(body)`, and `deleteData(id)`.
Initial fetches are cancelled on cleanup. Non-2xx responses are errors; mutation
methods reject as well as setting `error`, so event handlers must handle rejection.
`isLoading` stays true while any request is pending.

```tsx
const { data, error, isLoading, fetchData, createData, deleteData } =
    useApi<Encounter[]>('http://127.0.0.1:8001/encounters');

// Inside an async event handler with try/catch:
await createData({ patient_nbr: 12345, age: '[40-50)' });
await fetchData();
// Only after the backend implements DELETE /encounters/{encounter_id}:
await deleteData(encounterId);
await fetchData();
```

Create sends JSON with POST to the collection URL; delete sends DELETE to
`{url}/{id}` and supports empty success responses. Mutations do not automatically
change cached data: call `fetchData()` to refresh it. `createData<Body, Result>(body)`
can specify the create response type (otherwise it is `unknown`).
The current backend supports GET and POST `/encounters`, but **does not implement
DELETE**. Calling `deleteData` against it reports the HTTP error; it cannot remove
an encounter until a backend delete endpoint is added. Creation fields follow the
backend's `EncounterCreate` schema; `patient_nbr` is required.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the Oxlint configuration

If you are developing a production application, we recommend enabling type-aware lint rules by installing `oxlint-tsgolint` and editing `.oxlintrc.json`:

```json
{
  "$schema": "./node_modules/oxlint/configuration_schema.json",
  "plugins": ["react", "typescript", "oxc"],
  "options": {
    "typeAware": true
  },
  "rules": {
    "react/rules-of-hooks": "error",
    "react/only-export-components": ["warn", { "allowConstantExport": true }]
  }
}
```

See the [Oxlint rules documentation](https://oxc.rs/docs/guide/usage/linter/rules) for the full list of rules and categories.
