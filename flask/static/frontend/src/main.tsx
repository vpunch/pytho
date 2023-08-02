import React from 'react'
import ReactDOM from 'react-dom/client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import App from './App'


const QUERY_CLIENT = new QueryClient()

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <QueryClientProvider client={QUERY_CLIENT}>
      <App />
    </QueryClientProvider>
  </React.StrictMode>
);
